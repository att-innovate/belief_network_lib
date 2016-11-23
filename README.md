# belief-network-lib

Bayesian belief networks (aka Bayesian networks, aka probabilistic graphical models) are a powerful tool for representing dependence relationships in probability distributions. Given a joint probability distribution, Pr(X1, X2, ..., Xk), a table representing this requires |X1|X...X|Xk| entries. This representation can be accomplished much more compactly by identifying conditional independence relationships among the variables. Belief networks, are one method of encoding these independence relationships. Once this network is identified, it can then be used to perform various types of probabilistic inference. 

There is great utility, however, in learning this structure given only collections of data samples. One highly useful application, for which this library was specifically created to address, is dimensionality reduction in cases where variables have strong non-linear relationships. 

In cases where there is a linear relationship between the variables, an approach relying on covariance, such as Principal Components Analysis, is applicable and highly effective. In cases where variables' relationships are non-linear (e.g. highly discontinuous), other methods are motivated. 

An example of using this library to accomplish this specific application is contained in the Juypter notebook in the 'examples' directory.

# Installation

# Usage

## Create a network and sample data

~~~~
from belief-network-lib import network

nodeA = Node([0,1], id="A")
nodeB = Node([0,1], id="B")

nodeA.cpt = {}
nodeB.cpt = {}

nodeA.add_child(nodeB)
nodeB.add_parent(nodeA)

nodes = [nodeA, nodeB]
aBN = BeliefNetwork(nodes)

samples = [aBN.sample() for x in range(1000)]
~~~~

## Detect markov blanket

~~~~
from belief-network-lib import network_learner
~~~~

# Links
