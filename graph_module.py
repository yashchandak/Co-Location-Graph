# -*- coding: utf-8 -*-
"""
Created on Thu Jun  9 20:24:34 2016

@author: yash

TODO
1)Self-loops
2)Approximate Distance metric
3)Better visualisation
"""

import networkx as nx

abs_ratio   = {}
size_factor = 100

def co_location(objects, axf):
    node_sizes  = []
    labels      = {}
    nodes       = [i for i in range(len(objects))]
    edges       = []
    weights     = []
    
    for i in range(len(objects)):
        labels[i] = objects[i][0]
        node_sizes.append( int(size_factor * objects[i][5])**2 )
        for j in range(i+1  ,len(objects)):
            edges.append((i,j))
            weights.append(apx_distance(objects[i], objects[j]))

    G = nx.Graph()  
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    pos = nx.spring_layout(G)
    nx.draw(G, pos, width=weights, node_size=node_sizes, labels=labels, with_labels=True, ax=axf)

   
def apx_distance(x,y):
    #TODO implement distance metric    
    return 2
    