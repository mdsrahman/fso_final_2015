import random

import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

class Generate_Graph_Sample:
  def __init__(self, 
               max_x, 
               max_y, 
               total_nodes, 
               max_edges,
               short_edges_per_node, 
               long_edges_per_node,
               max_short_edge_dist,
               max_long_edge_dist):
    
    print"DEBUG: sampler initialized..."
    self.max_x = max_x
    self.max_y = max_y
    self.total_nodes = total_nodes
    self.max_edges = max_edges
    self.short_edges_per_node = short_edges_per_node
    self.long_edges_per_node = long_edges_per_node
    self.max_short_edge_dist  = max_short_edge_dist
    self.max_long_edge_dist = max_long_edge_dist
    
    self.short_edge_counter = np.zeros(self.total_nodes, dtype = int)
    self.long_edge_counter = np.zeros(self.total_nodes, dtype = int)
    
  def generate_node_positions(self):
    self.node_x = []
    self.node_y = []
    for i in xrange(self.total_nodes):
      x = random.uniform(0, self.max_x)
      y = random.uniform(0, self.max_y)
      self.node_x.append(x)
      self.node_y.append(y)
    
  def get_distance_sq(self,n1,n2):
    x1 = self.node_x[n1]
    y1 = self.node_y[n1]
    x2 = self.node_x[n2]
    y2 = self.node_y[n2]
    d = (x1- x2)**2 + (y1-y2)**2
    return d
  
  def has_room_for_edge(self,n):
    return self.has_room_for_short_edge(n) or self.has_room_for_long_edge(n)
    
  def has_room_for_short_edge(self,n):
    if self.short_edge_counter[n] \
      < self.short_edges_per_node:
      return True
    else: 
      return False
    
  def has_room_for_long_edge(self,n):
    if self.long_edge_counter[n] \
      < self.long_edges_per_node:
      return True
    else: 
      return False
    
  def add_edge(self,n1,n2,edge_type):
    self.adj.add_edge(n1,n2,con_type=edge_type)
    self.total_edge_counter += 1
    if edge_type == 'short':
      self.short_edge_counter[n1] += 1
      self.short_edge_counter[n2] += 1
    elif edge_type == 'long':
      self.long_edge_counter[n1] += 1
      self.long_edge_counter[n2] += 1
    return
  
  def generate_edges(self): 
    self.total_edge_counter = 0
    for n1 in xrange(self.total_nodes-1):
      for n2 in xrange(self.total_nodes-2):
        distance_sq =  self.get_distance_sq(n1, n2) 
        if distance_sq  <= self.max_short_edge_dist**2:
          if self.has_room_for_short_edge(n1) and self.has_room_for_short_edge(n2):
            self.add_edge(n1, n2, 'short')
        elif distance_sq  <= self.max_long_edge_dist**2:
          if self.has_room_for_long_edge(n1) and self.has_room_for_long_edge(n2):
            self.add_edge(n1, n2, 'long')
        if self.total_edge_counter == self.max_edges:
          return
    return
    

  def generate_adj_graph(self):
    self.adj = nx.Graph()
    self.adj.graph['name'] = 'Adjacency Graph'
    for i in xrange(self.total_nodes):
      self.adj.add_node(i)
    self.generate_edges()
    return
  
  def visualize_graph(self):
    node_position={}
    for i in xrange(self.total_nodes):
      node_position[i] =  (self.node_x[i], self.node_y[i])
      
    nx.draw_networkx(G = self.adj, pos = node_position ,with_labels = True, node_color ='w')
    plt.show()
    return
      
  def get_adj_graph(self):
    
    self.generate_node_positions()
    self.generate_adj_graph()
    #self.visualize_graph()
    return self.adj
  
  
    
    