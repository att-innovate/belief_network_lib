

import random
import itertools

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
    
    def sample(self, parent_bindings):
        """
            Given bound values, sample distribution to produce a value

            parent_bindings: {parent_node_id: val, parent_node_id:val, ...}
        """
        sample_value = None

        #Acqurie appropriate CPT entry
        distr_for_bindings = self.cpt[parent_bindings]

        #Sample retrieved distribution
        rand_num = random.random()

        acc_prob = rand_num
        for v in self.values:
            if None:
                pass
            
            acc_prob+=distr_for_bindings[v]

        return sampled_value
    
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

    