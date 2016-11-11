

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
    
    def evaluate(self):
        """ 
            Acquire values with their probabilites.
        """
        pass

class BeliefNetwork:
    def __init__(self, nodes):
        self.nodes = nodes
    
    def __str__(self):
        """
        ASCII art version of network. 
        """

        pass
    
    def sample(self, bindings=None):
        #Cascade of sampling, resulting in an entire record
        
        #Acquire nodes sorted in topological order
        sorted_nodes = self.nodes

        nodes_to_value = {}

        for n in sorted_nodes:
            logger.info("nodes_to_value: %s" % nodes_to_value)

            logger.info("Getting sample for %s" % n.id)

            #Determine value of parent nodes
            #-------------------------------
            parent_ids = [p.id for p in n.parents]

            logger.info("Parents: %s" % ",".join(parent_ids))

            parent_node_vals = {}
            
            for p in parent_ids:
                parent_node_vals[p] = nodes_to_value[p]
            #-------------------------------

            #Acquire value for this node
            sampled_value = n.sample(parent_node_vals)

            logger.info("sampled value for %s: %s" % (n.id, sampled_value))

            nodes_to_value[n.id] = sampled_value
        
        return nodes_to_value
    
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

    # for n in nodes:
    #     n.init_cpt()

    #Specify conditional probabilities
    nodeA.cpt = {None:[0.1, 0.9]}
    nodeE.cpt = {None:[0.9, 0.1]}
    nodeB.cpt = {(0,):[0.5, 0.5],
                 (1,):[0.01, 0.99]}
    nodeC.cpt = {(0,0):[0.01, 0.99],
                 (0,1):[0.3, 0.7],
                 (1,0):[0.99, 0.01],
                 (1,1):[0.8, 0.2]
                }
    nodeD.cpt = {(0,):[0.99, 0.01],
                 (1,):[0.01, 0.99]}
    #-------------------

    nodes = [nodeA, nodeB, nodeE, nodeC, nodeD]

    aBN = BeliefNetwork(nodes)

    #Obtain sample data
    #record = aBN.sample()

    return aBN

def main():
    pass

if __name__ == "__main__":
    main()

    