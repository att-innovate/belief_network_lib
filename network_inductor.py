
#   network_inductory.py
#
#   Author: Don M. Dini
#   Date: November 2016
#

import logging

import csv
import random

import scipy
from scipy.stats import chi2

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

class NetworkInductor(object):
    """
    """

    def __init__(self, input_file, column_names=None, delimiter=","):
        self.input_file = input_file
        (self.variables, self.jpt) = self.process_input_data()
    
    def process_input_data(self, column_names=None, delimiter=","):
        """ 
            If 'column_names' are not specified, then takes variable names from
            the first column of inputs.
        """
        
        table = {}

        reader = csv.reader(in_file, delimiter=delimiter)

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
            
        if normed:
            for k in table:
                table[k] = float(table[k])/num_records
        
        return (variables, table)
    
    def grow_blanket(self, variable_of_interest)
        
        logger.info("Grow blanket phase for %s.", variable_of_interest)

        var_set = set(self.variables)

        other_vars = var_set-{variable_of_interest}
        curr_blanket = []
        for o in other_vars:
            if is_conditionally_dependent_given(variable_of_interest, o, curr_blanket, jp_table=self.jpt, sample=True):
                curr_blanket.append(o)
        
        return curr_blanket
    
    def shrink_blanket(self, variable_of_interest, initial_blanket) #, variables, jpt, initial_blanket):
        logger.info("Shrink blanket phase for %s.", variable_of_interest)
        
        curr_mb_set = set(initial_blanket)

        for y in initial_blanket:
            if not is_conditionally_dependent_given(variable_of_interest, y, curr_mb_set - {y}, jp_table=self.jpt, sample=True):
                curr_mb_set.difference_update({y})

        return curr_mb_set

    #def find_markov_blanket_for(variable_of_interest, variables, jpt):
    def find_markov_blanket_for(self, variable_of_interest):
    """ 
        'variable_of_interest' is an instance of Variable
        'variables': The complete set of variables identified for this domain.
        'jpt': Joint probability table capturing counts for random variables in this domain

        Returns:
        -Minimal list of variables, such that variable of interest is independent of all other variables, 
         conditioned on those in list.
        -Uses Grow-Shrink algorithm described in "Bayesian Network Induction via Local Neighborhoods" by Margaritis and Thrun.
    """
    
    # intermediate_list = self.grow_blanket(variable_of_interest, variables, jpt)
    # return_set = self.shrink_blanket(variable_of_interest, variables, jpt, intermediate_list)

    intermediate_list = self.grow_blanket(variable_of_interest)
    return_set = self.shrink_blanket(variable_of_interest, intermediate_list)

    return return_set



def generate_possible_bindings(var_list, sample=False, num_samples=30):
    return_bindings = []

    var_matrix = []
    for v in var_list:
        var_0 = get_var(v.name, "0")
        var_1 = get_var(v.name, "1")
        var_matrix.append((var_0, var_1))
    
    if sample:
        for i in range(num_samples):
            new_binding = []

            random_binary_string = [random.choice([0,1]) for i in range(len(var_list))]

            for j in range(len(random_binary_string)):
                new_binding.append(var_matrix[j][random_binary_string[j]])
            
            return_bindings.append(new_binding)
    else:
        pass
    
    
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

def check_dependent_test(var_i, var_o, binding, jp_table):
    """ 
        'binding' is a list of Variable instances, set to 
        specific values. 

        'jp_table' is a joint probabilty table
    """
    
    is_dependent = False

    var_i_0 = get_var(var_i.name, "0")
    var_i_1 = get_var(var_i.name, "1")
    var_o_0 = get_var(var_o.name, "0")
    var_o_1 = get_var(var_o.name, "1")

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

    if p_val<=SIGNIFICANCE_LEVEL:
        is_dependent = True
    #------------------------------

    return is_dependent

def is_conditionally_dependent_given(var_i, var_o, cond_vars, jp_table, sample=True):
    """ 
        Is (binary) variable var_i dependent upon (binary) variable var_o, conditioned upon
        variables in cond_vars? 

        This test is performed sequentially, for each possible binding of cond_vars.
        If 'sample' is true, then instead of using each possible, binding, a randomly
        selected sample of bindings is used. 

        For each such binding, a Chi^2 test of indepdenence is performed.
    """
    
    #The null position
    is_dependent = False 

    #Acquire bindings for conditional variables
    bindings = generate_possible_bindings(list(cond_vars), sample=sample)

    #All it takes is dependence under one binding for dependence
    #overall to occur
    for binding in bindings:
        if check_dependent_test(var_i, var_o, binding, jp_table):
            is_dependent = True
            break

    return is_dependent