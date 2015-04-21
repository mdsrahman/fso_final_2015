import heuristic_placement_algo as hpas
import cPickle as pkl
#from collections import defaultdict
#from shapely import geometry as shgm
import random
import networkx as nx
import numpy as np
import target_heapify as th
from copy import  deepcopy

class generate_heuristic_placement_algo_instance:
  def __init__(self,  
               adj,
               node_x,
               node_y,
               target_spacing, 
               min_fso_distance,
               sink_ratio,
               static_d_max,
               gen_tn):

    self.min_fso_distance = min_fso_distance
    self.target_spacing = target_spacing
    self.sink_ratio = sink_ratio
    self.static_d_max = static_d_max
    self.gen_tn = gen_tn
    #load the nodes

    self.node_x = node_x
    self.node_y = node_y
    print "max_x:",max(self.node_x)
    print "max_y:",max(self.node_y)
    
    self.max_node_no = len(self.node_x) - 1
    
    self.max_x = max(self.node_x)
    self.max_y = max(self.node_y)
    self.N = None
    
    self.sinks = None
    self.adj = nx.Graph(adj)

    self.total_nodes = self.adj.number_of_nodes() 
    self.nodes = self.adj.nodes()  
    self.select_sinks()
    print "DEBUG: running heuristic set cover...."
    self.heurisitc_set_cover()
    self.hpa = hpas.Heuristic_Placement_Algo(
                                            adj = self.adj, 
                                            sinks = self.sinks, 
                                            N = self.N ,  
                                            static_d_max = self.static_d_max) 
    #---end of __init__----------------------------------------------------
  
  
  def heurisitc_set_cover(self):
    thp = th.Target_Node_Assoc( self.node_x, 
                                self.node_y, 
                                self.target_spacing, 
                                self.min_fso_distance, 
                                node_bin_interval =  100,
                                gen_tn=self.gen_tn)
    print "@heurisitc_set_cover"
    self.N = list(thp.get_node_cover())
    self.total_targets = thp.total_targets
    self.targets_covered = thp.targets_covered
    self.T_N = deepcopy(thp.T_N)
    print ">>len_N:",len(self.N)
    return
  
  def get_hpa_instance(self):
    return self.hpa
   
  def select_sinks(self):
    self.sinks = []
    num_sinks = 1 + int(self.sink_ratio  *  self.total_nodes) 
    connected_components = nx.connected_components(self.adj)
    num_sinks = max(num_sinks,nx.number_connected_components(self.adj))
    for l in connected_components:
      n = random.choice(l)
      self.sinks.append(n)
    while (num_sinks > len(self.sinks)):
      list = random.sample(self.adj.nodes(), num_sinks - len(self.sinks))
      for i in list:     
        if i not in self.sinks:  
          self.sinks.append(i)
    return
    
  
  def get_connection_type (self, n1, n2):
    n1_x = self.node_x[n1]
    n1_y = self.node_y[n1]
    
    n2_x = self.node_x[n2]
    n2_y = self.node_y[n2]
    
    dist_sq = (n1_x - n2_x)**2 + (n1_y - n2_y)**2
    fso_dist_sq = self.min_fso_distance * self.min_fso_distance
    if dist_sq <= fso_dist_sq:
      return 'short'
    else:
      return 'long'
    return 'long'
  
  def generate_adj_graph(self):
    self.adj = nx.Graph()
    self.adj.graph["name"] = "adjacency graph"
    edges = np.genfromtxt(self.edg_file_name, delimiter=",", dtype = int)
     
    
    for i in xrange(self.max_node_no+1):
      self.adj.add_node(i)
    
    for e in edges:
      u = e[0]
      v = e[1]
      connection_type = 'short'
      connection_type = self.get_connection_type(u, v)
      self.adj.add_edge(u, v, con_type = connection_type)
    return
  
if __name__ == '__main__':
  map_file_name = './map/nyc_small.osm'
  target_spacing = 2
  min_fso_distance = 100
  sink_ratio = 0.05
  static_d_max = 4
  whpa = generate_heuristic_placement_algo_instance(
                                          node_file_name = map_file_name+".node.pkl", 
                                          edge_file_name = map_file_name+".edge.txt",
                                           target_spacing = target_spacing, 
                                           min_fso_distance = min_fso_distance,
                                           sink_ratio = sink_ratio,
                                           static_d_max = static_d_max)
  hp = whpa.get_hpa_instance()

  hp.solve()
  
  
  
  
  
  
  