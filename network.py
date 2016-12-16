#   Copyright (c) 2016 AT&T Intellectual Property. All rights reserved.
#
#   network.py
#   
#   Description: Simple Bayesian Belief Network library.
#   The class BeliefNetwork implements a representation of a Bayesian Belief network, in which each
#   variable is a binary variable (taking on the values 0 or 1).
#
#   Once specified, the network can then be sampled (using forward sampling) to create data samples.
#   
#   An example of creating a BeliefNetwork instance is contained in the readme.
#
#   Author: Don M. Dini
#   Date: November 2016
#

import logging
import random
import itertools

logger = logging.getLogger("BELIEF-NETWORK-LIB")
logger.setLevel(logging.ERROR)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

class Node:
    """
        A Node in a belief network. It is assumed this node takes on discrete values.
    """

    def __init__(self, values=[0,1], id="Node"):
        self.id = id
        self.children = []
        self.parents = []
        self.values = values

        #Conditional probability table
        #Entries are:
        
        #(parent_node val1, parent_node val2, ...) ---> [p1, p2, ...]
        #parent node vals in key preserve order found in 'self.parents'
        #probabilities for values preserve order found in 'self.values'
        self.cpt = {}
    
    def init_cpt(self):
        
        values_list = []
        
        #Lists of possible values
        for p_var in self.parents:
            values = p_var.values
            values_list.append(values)
        
        #Possible variable bindings
        #--------------------------
        elem_iter = itertools.product(*values_list)
        bindings = [v for v in elem_iter]
        #--------------------------
        
        #Assign init CPT values for each possible
        #variable binding
        #
        #Initial CPT values are uniform distribution
        for tuple_value in bindings:
            self.cpt[tuple_value] = [float(1)/len(self.values) for v in self.values]
    
    def get_variable_combinations(self):
        val_lists = [p.values for p in self.parents]
        
        combinations = None 
        
        elem_it = itertools.product(*val_lists)

        combinations = [e for e in elem_it]

        return combinations
    
    def add_parent(self, aNode):
        self.parents.append(aNode)
    
    def add_child(self, aNode):
        self.children.append(aNode)
    
    def sample(self, parent_bindings=None):
        """
            Given bound values, sample distribution to produce a value

            If a required parent is not specified, then marginalize across the parent value.

            parent_bindings: {parent_node_id: val, parent_node_id:val, ...}
        """

        logger.info("sample - bindings: %s", parent_bindings)

        sample_value = None
        
        if len(self.parents)>0:
            
            #Acquire appropriate CPT entry
            #-----------------------------

            #Assemble arguments as tuple
            bindings_as_list = [] 
            parent_var_names_in_order = [n.id for n in self.parents]
            
            for p in parent_var_names_in_order:
                bindings_as_list.append(parent_bindings[p])


            bindings_as_tuple = tuple(bindings_as_list)
            
            cpt_entry = self.cpt[bindings_as_tuple]
            
            #-----------------------------
            
            #Sample retrieved distribution
            #-----------------------------
            rand_num = random.random()

            acc_prob = 0
            #for v in self.values:
            for i in range(len(cpt_entry)):
                
                var_name = self.values[i]
                val_prob = cpt_entry[i]
                
                acc_prob+=val_prob

                if acc_prob>=rand_num:
                    sample_value = var_name
                    break
            
            #-----------------------------
        else:
            #Acquire the only CPT entry
            cpt_entry = self.cpt[ self.cpt.keys()[0] ]

            logger.info("Retrieved CPT entry: %s" % cpt_entry)

            rand_num = random.random()

            acc_prob = 0
            for i in range(len(cpt_entry)):
                
                var_name = self.values[i]
                val_prob = cpt_entry[i]
                
                acc_prob+=val_prob

                if acc_prob>=rand_num:
                    sample_value = var_name
                    break

        return sample_value

class BeliefNetwork:
    def __init__(self, nodes):
        self.nodes = nodes
    
    def __str__(self):
        """
        ASCII art version of network.
        """

        #TODO

        pass
    
    def sample(self, bindings=None):
        """
            Cascade of sampling, resulting in an entire record

            Uses simple Forward Sampling algorithm, described in:
            "Probabilistic Graphical Models: Principles and Techniques" by Koller and Friedman
            Chapter 12

            'bindings': {<variable name>:<variable value>, ...}

            Assumes 'self.nodes' are in topological sorted order.
        """

        logger.info("Sampling 1 record.")

        #Acquire nodes sorted in topological order
        sorted_nodes = self.nodes

        nodes_to_value = {}

        for n in sorted_nodes:

            if bindings is not None and n.id in bindings:
                nodes_to_value[n.id] = bindings[n.id]
            else:

                #Determine value of parent nodes
                #-------------------------------
                parent_ids = [p.id for p in n.parents]

                parent_node_vals = {}
                
                for p in parent_ids:
                    parent_node_vals[p] = nodes_to_value[p]
                #-------------------------------

                #Acquire value for this node
                sampled_value = n.sample(parent_node_vals)

                nodes_to_value[n.id] = sampled_value
        
        return nodes_to_value
    
    def evaluate(self, bindings):
        pass

def notebook_data():

    nodeY = Node(id="Y")

    nodeX1 = Node(id="X1")

    nodeX2 = Node(id="X2")
    #Subtree of variables
    node2_subnodes = []
    for i in range(5):
        subnode = Node(id="X2%s" % i)
        node2_subnodes.append(subnode)

    nodeX3 = Node(id="X3")
    #Subtree of variables
    node3_subnodes = []
    for i in range(5):
        subnode = Node(id="X3%s" % i)
        node3_subnodes.append(subnode)

    nodeX4 = Node(id="X4")
    #Subtree of variables
    node4_subnodes = []
    for i in range(5):
        subnode = Node(id="X4%s" % i)
        node4_subnodes.append(subnode)
    
    #Parent child relationships
    nodeY.add_parent(nodeX1)
    nodeY.add_parent(nodeX2)
    nodeY.add_parent(nodeX3)
    nodeY.add_parent(nodeX4)

    nodeX1.add_child(nodeY)
    nodeX2.add_child(nodeY)
    nodeX3.add_child(nodeY)
    nodeX4.add_child(nodeY)

    #Node 2 subtree
    for n2_node in node2_subnodes:
        nodeX2.add_parent(n2_node)
        n2_node.add_child(nodeX2)
    
    #Node 3 subtree
    for n3_node in node3_subnodes:
        nodeX3.add_parent(n3_node)
        n3_node.add_child(nodeX3)

    #Node 4 subtree
    for n4_node in node4_subnodes:
        nodeX4.add_parent(n4_node)
        n4_node.add_child(nodeX4)

    #Conditional probability tables
    nodeY.cpt = {(0,0,0,0):[0.99, 0.01], (0,0,0,1):[0.99, 0.01], (0,0,1,0):[0.99, 0.01], (0,0,1,1):[0.01, 0.99], (0,1,0,0):[0.99, 0.01], (0,1,0,1):[0.01, 0.99], (0,1,1,0):[0.01, 0.99], (0,1,1,1):[0.99, 0.01], (1,0,0,0):[0.99, 0.01], (1,0,0,1):[0.99, 0.01], (1,0,1,0):[0.99, 0.01], (1,0,1,1):[0.99, 0.01], (1,1,0,0):[0.01, 0.99], (1,1,0,1):[0.99, 0.01], (1,1,1,0):[0.99, 0.01], (1,1,1,1):[0,1]}

    #Node 1 and subtree
    #------------------
    rand_val = random.random()
    nodeX1.cpt = {None:[rand_val, 1-rand_val]}
    #------------------
    
    #Node 2 and subtree
    #------------------
    nodeX2.cpt = {}

    var_tuples = nodeX2.get_variable_combinations()
    for v_t in var_tuples:
        rand_val = random.random()
        nodeX2.cpt[v_t] = [rand_val, 1-rand_val]

    for n2_node in node2_subnodes:
        rand_val = random.random()
        n2_node.cpt = {None:[rand_val, 1-rand_val]}
    #------------------

    #Node 3 and subtree
    #------------------
    nodeX3.cpt = {}

    var_tuples = nodeX3.get_variable_combinations()
    for v_t in var_tuples:
        rand_val = random.random()
        nodeX3.cpt[v_t] = [rand_val, 1-rand_val]

    for n3_node in node3_subnodes:
        rand_val = random.random()
        n3_node.cpt = {None:[rand_val, 1-rand_val]}
    #------------------
    
    #Node 4 and subtree
    #------------------
    nodeX4.cpt = {}

    var_tuples = nodeX4.get_variable_combinations()
    for v_t in var_tuples:
        rand_val = random.random()
        nodeX4.cpt[v_t] = [rand_val, 1-rand_val]

    for n4_node in node4_subnodes:
        rand_val = random.random()
        n4_node.cpt = {None:[rand_val, 1-rand_val]}
    #------------------

    #Create network
    #List of nodes in topological sorted order
    nodes = []
    nodes.extend(node4_subnodes)
    nodes.extend(node3_subnodes)
    nodes.extend(node2_subnodes)
    nodes.append(nodeX2)
    nodes.append(nodeX3)
    nodes.append(nodeX4)
    nodes.append(nodeX1)
    nodes.append(nodeY)

    aBN = BeliefNetwork(nodes)
    
    #Sample network
    samples = [aBN.sample() for x in range(10000)]

    return samples

def main():
    pass

if __name__ == "__main__":
    main()

    