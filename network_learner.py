#   Copyright (c) 2016 AT&T Intellectual Property. All rights reserved.
#
#   network_learner.py
#
#   Description:
#   Library for learning a Bayesian Belief Netowrk from CSV data.
#   Binary variables are supported at this time.
#
#   See examples directory for a comprehensive (Jupyter notebook) example of using this library
#   to solve problems.    
#
#   Author: Don M. Dini
#   Date: November 2016
#

import logging

import csv
import random
import itertools
import math

import scipy
from scipy.stats import chi2

logger = logging.getLogger("BELIEF-NETWORK-LIB")
logger.setLevel(logging.ERROR)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

BINDINGS_THRESHOLD = 30

class BinaryVariable(object):
    """
        Value can be 0 or 1
    """
    cache = {}  #map name and value to class instance

    def __init__(self, name, init_val=None):
        self.name = name
        self.value = None
        if init_val is not None:
            self.value = init_val
        
        BinaryVariable.cache[(self.name, self.value)] = self
    
    def set_val(self, val):
        self.value = val
    
    def __str__(self):
        return self.name+"(%s)" % self.value
    
    @classmethod
    def get_cached(cls, name, value):
        if (name, value) in cls.cache:
            return cls.cache[(name, value)]
        else:
            return None

class NetworkLearner(object):
    """
    """

    def __init__(self, input_file, column_names=None, delimiter=","):
        self.input_file = input_file
        
        #self.variables is a set of strings indicating names of variables
        (self.variables, self.jpt) = self.process_input_data()
    
    def process_input_data(self, column_names=None, delimiter=",", normed=False):
        """ 
            If 'column_names' are not specified, then takes variable names from
            the first column of inputs.
        """
        
        table = {}

        reader = csv.reader(self.input_file, delimiter=delimiter)

        variables = None

        #Acquire column names
        if column_names is None:
            headers = reader.next()
        else:
            headers = column_names 

        num_records = 0
        for row in reader:
            #Initialize variables for this row
            var_set = set()
            for i in range(len(row)):
                
                #First, check cached variables
                var_name = headers[i]
                var_val = row[i]

                cached_version = BinaryVariable.get_cached(var_name, var_val)

                if cached_version is None:
                    new_var = BinaryVariable(headers[i], init_val=row[i])
                else:
                    new_var = cached_version
                
                var_set.add(new_var)

            hashable_set = frozenset(var_set)
            if hashable_set in table:
                table[hashable_set]+=1
            else:
                table[hashable_set]=1
            
            num_records+=1

            if variables is None:
                variables = var_set
            
        if normed:
            for k in table:
                table[k] = float(table[k])/num_records
        
        var_names = set([v.name for v in variables])

        return (var_names, table)
    
    def grow_blanket(self, variable_of_interest, significance=0.5):
        
        logger.info("Grow blanket phase for %s.", variable_of_interest)

        var_set = set(self.variables)

        other_vars = var_set-{variable_of_interest}
        curr_blanket = []
        for o in other_vars:
            if is_conditionally_dependent_given(variable_of_interest, o, curr_blanket, jp_table=self.jpt, significance=significance):
                curr_blanket.append(o)
        
        return curr_blanket
    
    def shrink_blanket(self, variable_of_interest, initial_blanket, significance=0.5):
        logger.info("Shrink blanket phase for %s.", variable_of_interest)
        
        curr_mb_set = set(initial_blanket)

        for y in initial_blanket:
            if not is_conditionally_dependent_given(variable_of_interest, y, curr_mb_set - {y}, jp_table=self.jpt, significance=significance):
                curr_mb_set.difference_update({y})

        return curr_mb_set

    #def find_markov_blanket_for(variable_of_interest, variables, jpt):
    def find_markov_blanket_for(self, variable_of_interest, significance=0.5):
        """ 
            'variable_of_interest' is an instance of Variable
            'variables': The complete set of variables identified for this domain.
            'jpt': Joint probability table capturing counts for random variables in this domain

            Returns:
            -Minimal list of variables, such that variable of interest is independent of all other variables, 
            conditioned on those in list.
            -Uses Grow-Shrink algorithm described in "Bayesian Network Induction via Local Neighborhoods" by Margaritis and Thrun.
        """

        intermediate_list = self.grow_blanket(variable_of_interest, significance=significance)
        return_set = self.shrink_blanket(variable_of_interest, intermediate_list, significance=significance)

        return return_set



def get_var(var_name, var_val):
    
    new_var = None
    
    cached_version = BinaryVariable.get_cached(var_name, var_val)
    if cached_version is None:
        new_var = BinaryVariable(var_name, init_val=var_val)
    else:
        new_var = cached_version
    
    return new_var

def get_sample_bindings(var_list, num_samples):
    logger.info("Sampling bindings - acquiring %s samples." % str(num_samples))
    
    return_bindings = []

    var_matrix = []
    for var_name in var_list:
        var_0 = get_var(var_name, "0")
        var_1 = get_var(var_name, "1")
        var_matrix.append((var_0, var_1))
    
    for i in range(num_samples):
        new_binding = []

        random_binary_string = [random.choice([0,1]) for i in range(len(var_list))]

        for j in range(len(random_binary_string)):
            new_binding.append(var_matrix[j][random_binary_string[j]])
        
        return_bindings.append(new_binding)
    
    return return_bindings

def get_all_bindings(var_list):
    logger.info("Getting all bindings for variables: %s" % ", ".join(var_list))

    return_bindings = []

    var_matrix = []
    for var_name in var_list:
        var_0 = get_var(var_name, "0")
        var_1 = get_var(var_name, "1")
        var_matrix.append((var_0, var_1))

    it = itertools.product(*var_matrix)
    for e in it:
        return_bindings.append(e)
        
    return return_bindings

def generate_possible_bindings(var_list, sample=None):
    """
        'var_list' is a list of names of variables (strings)

        'sample':
            -If True, instead of generating each possible binding, a randomly
            selected sample of bindings is generated.
            -If False, then each possible binding is used.
            -If None, then if # total bindings is less than threshold (defined in generate_possible_bindings),
            all bindings are used. If greater than threshold, then switches to sampling. 
    """
    
    logger.info("Generating bindings for variables: %s" % ", ".join(var_list))

    #Determine num_samples

    return_bindings = []
    
    if sample is None:
        total_num_bindings = math.pow(2, len(var_list))

        if total_num_bindings > BINDINGS_THRESHOLD:
            num_samples = int(math.floor((0.8)*total_num_bindings))
            return_bindings = get_sample_bindings(var_list, num_samples)
        else:
            return_bindings = get_all_bindings(var_list)
    elif sample is True:
        num_samples = int(math.floor((0.8)*total_num_bindings))
        return_bindings = get_sample_bindings(var_list, num_samples)
    else:
        return_bindings = get_all_bindings(var_list)
            
    return return_bindings

def get_event_count(jp_table, set_of_bound_vars):
    
    return_val = 0
    
    for entry in jp_table:
        if entry.issuperset(set_of_bound_vars):
            return_val += jp_table[entry]
    
    return return_val

def get_test_statistic(n, x00, x01, x10, x11):
    """ Form Chi^2 test statistic from count info """
    
    if n==0:
        return 0

    e00 = float((x00+x01)*(x00+x10))/n
    e01 = float((x00+x01)*(x01+x11))/n
    e10 = float((x10+x11)*(x00+x10))/n
    e11 = float((x10+x11)*(x01+x11))/n
    
    term1 = 0
    if e00!=0:
        term1 = (x00 - e00)*(x00 - e00)/e00
    
    term2 = 0
    if e01!=0:
        term2 = (x01 - e01)*(x01 - e01)/e01
    
    term3 = 0
    if e10!=0:
        term3 = (x10 - e10)*(x10 - e10)/e10
    
    term4 = 0
    if e11!=0:
        term4 = (x11 - e11)*(x11 - e11)/e11

    return term1 + term2 + term3 + term4

def check_dependent_test(var_i, var_o, binding, jp_table, significance=0.5):
    """ 
        'var_i', 'var_o' are names of variables (strings)

        'binding' is a list of Variable instances, set to 
        specific values. 

        'jp_table' is a joint probabilty table
    """
    
    is_dependent = False

    var_i_0 = get_var(var_i, "0")
    var_i_1 = get_var(var_i, "1")
    var_o_0 = get_var(var_o, "0")
    var_o_1 = get_var(var_o, "1")

    #Obtain individual event counts
    #------------------------------
    var_set1 = set()
    var_set1.add(var_i_0)
    var_set1.add(var_o_0)
    var_set1.update(binding)

    count00 = get_event_count(jp_table, var_set1) # var_i.set_val(0), var_o.set_val(0), binding)
    
    var_set2 = set()
    var_set2.add(var_i_0)
    var_set2.add(var_o_1)
    var_set2.update(binding)
    count01 = get_event_count(jp_table, var_set2) # var_i.set_val(0), var_o.set_val(1), binding)
    
    var_set3 = set()
    var_set3.add(var_i_1)
    var_set3.add(var_o_0)
    var_set3.update(binding)
    count10 = get_event_count(jp_table, var_set3) #var_i.set_val(1), var_o.set_val(0), binding)
    
    var_set4 = set()
    var_set4.add(var_i_1)
    var_set4.add(var_o_1)
    var_set4.update(binding)
    count11 = get_event_count(jp_table, var_set4) #var_i.set_val(1), var_o.set_val(1), binding)
    #------------------------------

    total_count = count00 + count01 + count10 + count11

    #Form test statistic
    #------------------------------
    test_statistic = get_test_statistic(total_count, count00, count01, count10, count11)
    #------------------------------

    logger.info("Test statistic: %s", test_statistic)

    #Obtain p-value
    #------------------------------
    p_val = 1-chi2.cdf(test_statistic, 1)

    logger.info("p_val: %s" % p_val)

    if p_val<=significance:
        is_dependent = True
    #------------------------------

    return is_dependent

def is_conditionally_dependent_given(var_i, var_o, cond_vars, jp_table, sample=None, significance=0.5):
    """ 
        Is (binary) variable var_i dependent upon (binary) variable var_o, conditioned upon
        variables in cond_vars? 

        This test is performed sequentially, for each possible binding of cond_vars.
        
        'sample' parameter:
            -If True, then instead of using each possible binding, a randomly
            selected sample of bindings is used.
            -If False, then each possible binding is used.
            -If None, then if # total bindings is less than threshold (defined in generate_possible_bindings),
            all bindings are used. If greater than threshold, then switches to sampling. 

        For each such binding, a Chi^2 test of indepdenence is performed.

        var_i is the name of a variable (string)
        var_o is the name of a variable (string)
        cond_vars is a list of names of variables (list of strings)
    """
    
    logger.info("Checking - %s conditionally independent of %s given %s" % (var_i, var_o, ", ".join([str(s) for s in cond_vars]) ))

    #The null position
    is_dependent = False 

    #Acquire bindings for conditional variables
    #'bindings' is a list of bound variables - BinaryVariable instances
    # with set (non-None) values. 
    bindings = generate_possible_bindings(list(cond_vars), sample=sample)

    #All it takes is dependence under one binding for dependence
    #overall to occur
    for binding in bindings:
        if check_dependent_test(var_i, var_o, binding, jp_table, significance=significance):
            is_dependent = True
            break

    return is_dependent