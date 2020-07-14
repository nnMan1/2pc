import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.image as mpimg
import numpy as np

#plt.ion()

class Network:
    def __init__(self, nodes):
        
        self.graph = nx.Graph()
        for node in nodes:
            self.graph.add_node(node)
        
        self.fig = plt.figure()
        self.nodePos = nx.circular_layout(self.graph)

    def draw(self):
        nx.draw_networkx(self.graph, with_labels = True,pos=self.nodePos)
        plt.show(block = False)  
        
    def sentMessage(self,source, nodes, message):
        x1, y1 = self.nodePos[source][0], self.nodePos[source][1]
    
        tmps = []

        for i in range(len(nodes)):
            tmps.append(plt.text(x1,y1,message,horizontalalignment='center', verticalalignment='center'))

        for i in range(10):
            for j in range(len(nodes)):
                tmps[j].remove()

                plt.draw()

                x2, y2 = self.nodePos[nodes[j]][0], self.nodePos[nodes[j]][1]
                tmps[j] = plt.text(x1+(x2-x1)*i*0.1,y1+(y2-y1)*i*0.1,message, horizontalalignment='center', verticalalignment='center')
                
            plt.pause(0.05)
            plt.draw()

        for i in range(len(nodes)):
            tmps[i].remove()

        
        plt.pause(0.1)
        plt.draw()

if __name__=='__main__':
    graph = Network(['shard1repl', 'shard2repl', 'shard3repl', 'client'])
    graph.draw()

    graph.sentMessage('shard1repl', ['shard3repl', 'shard2repl'], 'prepare')
    graph.sentMessage('shard2repl', ['shard1repl'], 'vote_commit')

    input("Press enter to exit")
