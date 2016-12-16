# belief_network_lib

Bayesian belief networks (aka Bayesian networks, aka probabilistic graphical models) are a powerful tool for representing dependence relationships in probability distributions. Given a joint probability distribution, Pr(X1, X2, ..., Xk), a table representing this requires |X1|X...X|Xk| entries. This representation can be accomplished much more compactly by identifying conditional independence relationships among the variables. Belief networks, are one method of encoding these independence relationships. Once this network is identified, it can then be used to perform various types of probabilistic inference. 

There is great utility, however, in learning this structure given only collections of data samples. One highly useful application, for which this library was specifically created to address, is dimensionality reduction in cases where variables have strong non-linear relationships. 

In cases where there is a linear relationship between the variables, an approach relying on covariance, such as Principal Components Analysis, is applicable and highly effective. In cases where variables' relationships are non-linear (e.g. highly discontinuous), other methods are motivated. 

An example of using this library to accomplish this specific application is contained in the Juypter notebook in the 'examples' directory.

# Installation

# Usage

## Create a network and sample data

~~~~
from belief_network_lib import network

nodeA = network.Node(id="A")
nodeB = network.Node(id="B")

nodeA.cpt = {None: [0.4, 0.6]}   #Node A has no parents, thus the key in the conditional probability table is None

nodeB.cpt = {(0,):[0.5, 0.5], (1,):[0.1, 0.9]}  #Node B has one parent, thus the conditional 
                                                #probability table has two entries, one for
                                                #each possible value the parent (A) might take on.

nodeA.add_child(nodeB)
nodeB.add_parent(nodeA)

nodes = [nodeA, nodeB]
aBN = network.BeliefNetwork(nodes)              #Nodes must be in topologically sorted order.

samples = [aBN.sample() for x in range(1000)]
~~~~

`samples` now contains:

~~~~
[{'A': 1, 'B': 1},
 {'A': 0, 'B': 1},
 {'A': 1, 'B': 1},
 {'A': 0, 'B': 1},
 {'A': 1, 'B': 1},
 {'A': 0, 'B': 1},
 {'A': 0, 'B': 0},
 {'A': 0, 'B': 0},
 {'A': 0, 'B': 0},
 {'A': 1, 'B': 1}
 .
 .
 .
 ]
~~~~

## Detect Markov blanket given data

~~~~
from belief_network_lib import network_learner

input_file = open(path/to/csv/file)
aNI = network_learner.NetworkLearner(input_file)

aNI.find_markov_blanket_for("B")
~~~~

# Links

* Margaritis, Dimitris, and Sebastian Thrun. Bayesian network induction via local neighborhoods. No. CMU-CS-99-134. CARNEGIE-MELLON UNIV PITTSBURGH PA DEPT OF COMPUTER SCIENCE, 1999. [Link to paper](http://www.dtic.mil/dtic/tr/fulltext/u2/a373341.pdf)
