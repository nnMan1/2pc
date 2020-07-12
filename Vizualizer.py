import networkx as nx
import matplotlib.pyplot as plt
from grave import plot_network
from grave.style import use_attributes

graph = nx.Graph()
graph.add_nodes_from(['shar1Repl', 'shard2Repl', 'shard3Repl', 'congifRepl', 'mongoClient'])

fig, ax = plt.subplots()

nx.draw(graph,with_labels=True)
plt.show()