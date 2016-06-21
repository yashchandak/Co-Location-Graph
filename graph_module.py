# -*- coding: utf-8 -*-
"""
Created on Thu Jun  9 20:24:34 2016

@author: yash

TODO
1)Self-loops
2)[Done/Improve] Approximate Distance metric
3) Improve visualisation for batch graphs
"""

import networkx as nx
import numpy as np
#Every size relative to person
classes_ratio =  {"Aeroplane" : 1500 , "Bicycle" : 150, "Bird" : 20, "Boat" : 200, "Bottle" : 20, "Bus" : 500, "Car" : 250, "Cat" : 30, "Chair" : 80, "Cow" : 200, "Dining Table" : 150, "Dog" : 40, "Horse" : 150, "Motorbike" : 150, "Person" : 100, "Potted plant" : 50, "Sheep" : 80, "Sofa" : 150, "Train" : 500,"Tv" : 50}
   
size_factor = 100

def co_location(all_results, axf, thresh, selected):
    node_sizes  = []
    labels      = {}
    edge_labels = {}
    edges       = []
    weights     = []
    filtered_results = []
    #keep only the objects falling under selected classes
    #objects = [obj  for result in all_results   for obj in result  if (selected['All'] or selected[obj[0]])]    
    if len(all_results) == 0:
        return
    
    for result in all_results:
        filtered_results.append([obj   for obj in result  if (selected['All'] or selected[obj[0]])])
        
    print (filtered_results)
    nodes   = [obj[6]  for result in filtered_results   for obj in result  if (selected['All'] or selected[obj[0]])]
    
    for objects in filtered_results:
        for i in range(len(objects)):            
            labels[(objects[i][6])] = objects[i][0]+'\n(ID: '+ str(objects[i][6]) + ')'
            node_sizes.append( int(size_factor * objects[i][5])**2 )
            
            for j in range(i+1  ,len(objects)):             
                d = apx_distance(objects[i], objects[j])
                if (d > thresh):  #filter based on apx distance
                    continue                
                
                edges.append((objects[i][6], objects[j][6]))
                edge_labels [(objects[i][6], objects[j][6])]=str("%0.1f" %(d))
                weights.append(1) #constant weights for edge width, for time being
    
    if len(weights): 
        maxim = max(weights)
        weights = [max(1, 3*maxim/w) for w in weights]
    
    G = nx.Graph()  
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    pos = nx.spring_layout(G, k = 0.45)
    
    #Disable x-y axis and make plot area white
    cf = axf.get_figure()
    cf.set_facecolor('w')
    axf = cf.gca()
    axf.set_axis_off()
    
    nx.draw_networkx_nodes(G, pos, node_size = node_sizes, ax=axf)
    nx.draw_networkx_edges(G, pos, width = weights, edge_color = 'g', ax=axf)
    nx.draw_networkx_labels(G, pos, labels = labels, ax=axf)
    nx.draw_networkx_edge_labels(G, pos, edge_labels = edge_labels, font_color = 'b', label_pos = 0.3, ax=axf)

   
def apx_distance(x,y):
    #very crude approximation of istance 
    curr_ratio  = (x[3]*x[4])/(y[3]*y[4])
    act_ratio   = classes_ratio[x[0]]/classes_ratio[y[0]]
    z_ratio     = max(curr_ratio, act_ratio)/min(curr_ratio, act_ratio)
    dist        = 0.1* np.sqrt( (x[1] - y[1])**2 + (x[2] - y[2])**2)*z_ratio
    #print ('%s : %s : %f : %f : %f : %f ' % (x[0], y[0], curr_ratio, act_ratio, z_ratio, max(1, int(dist))))
    return dist
    