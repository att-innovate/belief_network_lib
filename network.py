

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

    def __init__(self, values, id="Node"):
        self.id = id
        self.children = []
        self.parents = []
        self.values = values

        #Conditional probability table
        #Entries are:
        #{parent_node_id: val, parent_node_id: val, ...} ---> {val1: p1, val2: p2, ...}
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

            logger.info("parents: %s" % ",".join([str(p) for p in self.parents]) )
            
            #Acquire appropriate CPT entry
            #-----------------------------

            #Assemble arguments as tuple
            bindings_as_list = [] 
            parent_var_names_in_order = [n.id for n in self.parents]
            
            for p in parent_var_names_in_order:
                bindings_as_list.append(parent_bindings[p])

            bindings_as_tuple = tuple(bindings_as_list)
            
            cpt_entry = self.cpt[bindings_as_tuple]
            
            logger.info("Retrieved cpt entry: %s" % cpt_entry)
            #-----------------------------
            
            #Sample retrieved distribution
            #-----------------------------
            # rand_num = random.random()

            # acc_prob = rand_num
            # for v in self.values:
            #     if None:
            #         pass
                
            #     acc_prob+=distr_for_bindings[v]
            
            # sample_value = None
            #-----------------------------
        else:
            cpt_entry = self.cpt[ self.cpt.keys()[0] ]

            #Acquire the only CPT entry
            sample_value = None

        return sample_value
    
    def evaluate(self):
        """ 
            Acquire values with their probabilites.
        """
        pass

class BeliefNetwork:
    def __init__(self, nodes):
        self.nodes = nodes
    
    def __str__(self):
        pass
    
    def sample(self, bindings=None):
        #Cascade of sampling, resulting in an entire record
        
        #Acquire nodes sorted in topological order
        sorted_nodes = None

        nodes_to_value = {}

        for n in sorted_nodes:        
            #Determine value of parent nodes
            parent_ids = n.parents

            parent_node_vals = {}
            for p in parent_ids:
                parent_node_vals[p] = nodes_to_value[p]

            #Acquire value for this node
            sampled_value = n.sample(parent_node_vals)
            nodes_to_value[n.id] = sampled_value
    
    def evaluate(self, bindings):
        pass

def test_data():

    #Create test network
    #-------------------
    
    #Create Nodes
    nodeA = Node([0,1], id="A")
    nodeB = Node([0,1], id="B")
    nodeC = Node([0,1], id="C")
    nodeD = Node([0,1], id="D")
    nodeE = Node([0,1], id="E")
    
    #Create connections
    nodeA.add_child(nodeB)
    nodeB.add_child(nodeC)
    nodeB.add_child(nodeD)
    nodeE.add_child(nodeC)

    nodeC.add_parent(nodeB)
    nodeC.add_parent(nodeE)
    nodeD.add_parent(nodeB)
    nodeB.add_parent(nodeA)

    #Specify conditional probabilities
    # nodeA.cpt = None
    # nodeB.cpt = None
    # nodeC.cpt = None
    # nodeD.cpt = None
    # nodeE.cpt = None
    #-------------------

    nodes = [nodeA, nodeB, nodeC, nodeD, nodeE]

    for n in nodes:
        n.init_cpt()

    aBN = BeliefNetwork(nodes)

    #Obtain sample data
    #record = aBN.sample()

    return aBN

def main():
    pass

if __name__ == "__main__":
    main()

    