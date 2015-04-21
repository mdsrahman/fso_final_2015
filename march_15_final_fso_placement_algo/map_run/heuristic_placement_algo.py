import networkx as nx
import networkx.algorithms.flow as flow

import random 


from numpy import mean,ceil


from operator import itemgetter

import operator as op
import time
'''
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection'''

import modified_step_2 as mdfs2

#import pylab
#import relaxed_ilp_solver_for_placement_algo as rilp
#from xlwt.Row import adj

class Heuristic_Placement_Algo:
  def __init__(self, adj, sinks, N, static_d_max = 4): #, seed = 101239):
 
    self.capacity = 1.0
    self.adj = nx.Graph(adj)
    self.sinks = list(sinks)
    self.G_p = None
    self.g1 = None
    self.g = None
   
    self.n_max =  None
    self.static_d_max = static_d_max
    #self.full_adj_max_flow = None
    self.avg_max_flow_val =  None
    self.avg_upper_bound_flow_val = None
    self.N = list(N)
    self.last_time = time.time()
    
  def print_graph(self, g):
    if 'name' in g.graph.keys():
      print "graph_name:",g.graph['name']
    print "---------------------------"
    #print "connected:",nx.is_connected(g)
    print "num_edges:",g.number_of_edges()
    
    for n in g.nodes(data=True):
      print n 
      
    for e in g.edges(data=True):
      print e
  
  
  def modified_backbone_network(self):
    m = mdfs2.Modified_Step_2(adj = self.adj, sink=self.sinks, sc_node = self.N )
    m.run_bfs()
    self.disconnected_covering_nodes = list(set(self.N))
    self.bg = nx.Graph(m.bg)
    for i in self.bg.nodes():
      if i in self.N:
        self.disconnected_covering_nodes.remove(i)
        
    self.G_p = nx.Graph(self.bg)
    print "DEBUG:?? number of nodes in the backbone network:",self.G_p.number_of_nodes(),\
         " edges:",self.G_p.number_of_edges()
    return
    
  def get_max_degree_nodes(self,g):
    n_list=[]
    non_sink_nodes = set(g.nodes()) - set(self.sinks)
    node_degree = nx.degree(g, non_sink_nodes)
    sorted_node_degree = sorted(node_degree.items(), key=itemgetter(1),reverse=True)
    max_degree = -1
    for n,degree in sorted_node_degree:
      if degree >= max_degree:
        max_degree = degree
        n_list.append(n)
      else:
        break
    candidate_nodes = []
    candidate_nodes.extend(self.sinks)
    for n,degree in reversed(sorted_node_degree):
      if degree <= max_degree - 2:
        candidate_nodes.append(n)
      else:
        break
    return max_degree, n_list,candidate_nodes
  
  def check_node_for_degree_reduction(self, n, cnodes):
    for s in self.sinks:
      bfs_successors = nx.bfs_successors(self.G_p, s)
      if n in bfs_successors.keys():
        break
    else:
      return False
    nbr_s = bfs_successors[n]
    for c in cnodes:
      for nbr in nbr_s:
        if self.adj.has_edge(c, nbr) and str(self.adj[c][nbr]['con_type']) =='short':
          self.G_p.remove_edge(n, nbr)
          self.G_p.add_edge(c, nbr)
          return True
    return False
  
  def reduce_node_degree(self):
    for s in self.sinks:
      self.G_p.add_node(s)
        
    while True:
      max_degree, max_deg_nodes, cnodes = self.get_max_degree_nodes(self.G_p)
      self.d_max = max_degree
      #print max_degree,max_deg_nodes,cnodes
      if max_degree <= 1 or len(max_deg_nodes)==0 or len(cnodes)==0:
        break
      degree_reduced = False
      for n in max_deg_nodes:
        degree_reduced = self.check_node_for_degree_reduction(n, cnodes)
        if degree_reduced:
          break
      if not degree_reduced:
        break
    self.n_max = int(1.1*self.G_p.number_of_nodes())
    return
    #-----------------related to step 4--------------------
  def add_super_source(self, g):
    g.add_node('src')
    source_connected_nodes = list(set(self.g.nodes()) - set(self.sinks))
    for n in source_connected_nodes:
      g.add_edge('src',n,capacity = float('inf'))
    return g
  
  def add_super_sink(self, g):
    g.add_node('snk')
    for n in self.sinks:
      g.add_edge(n,'snk',capacity = float('inf'))
    return g
  
  def add_capacity(self, g, capacity=1.0):
    edge_set = g.edges()
    for x,y in edge_set:
      g.edge[x][y]['capacity'] = capacity
    return g
  
  def compute_residual_graph(self,g, capacity='capacity', flow='flow'):
    for i,j in g.edges():
      g[i][j]['capacity'] -= g[i][j]['flow']
      g[i][j]['flow'] = 0.0
    return g
  
  def generate_all_node_source_potential(self, r, nlist):
    source_potential ={}
    for n in nlist:
      source_potential[n] = 0
    for n in nlist:
      r1 = nx.DiGraph(r)
      
      if r1.has_node('src'):
        r1.remove_node('src')
        
      if not r1.has_node('snk'):
        r1 = self.add_super_sink(r1)
      if r1.has_edge(n,'snk'):
        r1.remove_edge(n, 'snk')
        
      r1 = flow.shortest_augmenting_path(G=r1, s=n ,t='snk', capacity = 'capacity')
      src_p = r1.graph['flow_value']
      if src_p >0:
        source_potential[n] = src_p 
    return source_potential
  
  
  def generate_all_node_sink_potential(self, r, nlist):
    sink_potential ={}
    for n in nlist:
      sink_potential[n] = 0
    for n in nlist:
      r1 = nx.DiGraph(r)
      
      if r1.has_node('snk'):
        r1.remove_node('snk')
        
      if not r1.has_node('src'):
        r1 = self.add_super_source(r1)
      if r1.has_edge('src',n):
        r1.remove_edge('src',n)
        
      r1 = flow.shortest_augmenting_path(G=r1, s='src' ,t=n, capacity = 'capacity')
      snk_p = r1.graph['flow_value']
      if snk_p >0:
        sink_potential[n] = snk_p
      
    return sink_potential
  
  def get_time_diff(self, msg = None):
    time_t = self.last_time
    self.last_time = time.time()
    print"\t\tDEBUG: time elapsed: ", time.time() - time_t," ",msg
  
  def run_step_4(self):
    self.g = self.adj
    self.g1 = nx.Graph(self.G_p)
 
    #make it dynamic---##
    g1_node_list = self.g1.nodes()
    for u in g1_node_list:
      for v in g1_node_list:
        if u!=v and self.adj.has_edge(u, v):
          self.g1.add_edge(u,v)
    
      
    backbone_nodes = list(self.g1.nodes())
    available_nodes = list(set(self.g.nodes()) - set(backbone_nodes))
    iter_counter = 0
    self.last_time = time.time()
    
    while(available_nodes and self.g1.number_of_nodes() <= self.n_max):
      iter_counter += 1
      self.get_time_diff()
      print "\t\tDEBUG: iteration no:",iter_counter,\
        " available nodes:",len(available_nodes),\
        " allowable nodes:",self.n_max - self.g1.number_of_nodes(),\
        " current nodes:",self.g1.number_of_nodes()
      #t_input = raw_input("press enter:")
      #self.get_time_diff(msg = "at the beginning of while loop") #----!!!time diff
      
      d = nx.Graph(self.g1)
      
      max_benefit = 0
      max_i = max_j = -1
      
      new_node_list = None
      
      backbone_nodes = list(self.g1.nodes())
      total_bnodes = len(backbone_nodes)
      
      
      d = self.add_capacity(g = d, capacity = self.capacity)
      d= self.add_super_source(d)
      d = self.add_super_sink(d)
      
      r = flow.shortest_augmenting_path(G=d, s='src', t='snk', capacity = 'capacity')
      
      r = self.compute_residual_graph(g=r, capacity = 'capacity', flow='flow')
      
      source_potential = self.generate_all_node_source_potential(r = r, 
                                               nlist = backbone_nodes) 
      sink_potential = self.generate_all_node_sink_potential(r = r, 
                                             nlist = backbone_nodes) 
      for c1 in range(total_bnodes-1):
        i = backbone_nodes[c1]
        dg = nx.Graph(self.adj)
        i_path_length, i_path = nx.single_source_dijkstra(G = dg, source = i, target=None, cutoff=None)
        for c2 in range(c1+1, total_bnodes):
          j = backbone_nodes[c2]
          if j not in i_path_length.keys():
            continue
          
          i_j_path = list(i_path[j])
          new_nodes_on_i_j_path = [u for u in i_j_path if u in available_nodes]
          
          new_node_count = len(new_nodes_on_i_j_path)
          if new_node_count+self.g1.number_of_nodes() > self.n_max:
            continue
          if  new_node_count >= 1:
            i_j_path_benefit = min(source_potential[i], sink_potential[j])/(1.0 * new_node_count)
            j_i_path_benefit = min(source_potential[j], sink_potential[i])/(1.0 * new_node_count)
            if i_j_path_benefit > max_benefit:
              max_benefit = i_j_path_benefit
              max_i = i
              max_j = j
              new_node_list = list(new_nodes_on_i_j_path)
            elif j_i_path_benefit > max_benefit:
              max_benefit =j_i_path_benefit
              max_i = j
              max_j = i
              new_node_list = list(new_nodes_on_i_j_path)
      if max_i == -1:
        break 
      if len(new_node_list)+self.g1.number_of_nodes()>self.n_max:
        break
      for n in new_node_list:
        self.g1.add_node(n)
        print "\t\tDEBUG@heurisitc_placement_algo..(): adding new node step iv: node",n
        available_nodes.remove(n)
      
      for n in new_node_list: 
        for nbr in self.g[n]:
          if nbr in self.g1.nodes():
            self.g1.add_edge(n,nbr)
    return
  
  def is_path_valid_for_static_graph(self, path):
    if len(path)<2:
      return False

    i = path[0]
    j = path[-1]
    
    i_deg = self.static.degree(i)
    j_deg = self.static.degree(j)
    if (self.static_d_max - i_deg) < 1 or (self.static_d_max - j_deg) < 1:
      return False
    for n in path[1:-1]:
      if self.static.has_node(n) and ( self.static_d_max - self.static.degree(n)) < 2:
        return False
    return True
  
  def run_static_modified_step_4(self):
    self.g = self.adj
    self.static = nx.Graph(self.G_p)
    
      
    backbone_nodes = list(self.static.nodes())
    available_nodes = list(set(self.g.nodes()) - set(backbone_nodes))
    iter_counter = 0
    self.last_time = time.time()
    
    while(available_nodes and self.static.number_of_nodes() <= self.n_max):
      iter_counter += 1
      self.get_time_diff()
      print "\t\tDEBUG: iteration no:",iter_counter,\
        " available nodes:",len(available_nodes),\
        " allowable nodes:",self.n_max - self.static.number_of_nodes(),\
        " current nodes:",self.static.number_of_nodes()
      d = nx.Graph(self.static)
      
      max_benefit = 0
      max_i = max_j = -1
      
      new_node_list = None
      
      backbone_nodes = list(self.static.nodes())
      total_bnodes = len(backbone_nodes)
      
      src_list = list(set(self.static.nodes()) - set(self.sinks))
      
      d = self.add_capacity(g = d, capacity = self.capacity)
      d= self.add_super_source(d)
      d = self.add_super_sink(d)
      
      r = flow.shortest_augmenting_path(G=d, s='src', t='snk', capacity = 'capacity')
      
      r = self.compute_residual_graph(g=r, capacity = 'capacity', flow='flow')
      
      source_potential = self.generate_all_node_source_potential(r = r, 
                                               nlist = backbone_nodes) 
      sink_potential = self.generate_all_node_sink_potential(r = r, 
                                             nlist = backbone_nodes) 
      for c1 in range(total_bnodes-1):
        i = backbone_nodes[c1]
        dg = nx.Graph(self.adj)
        i_path_length, i_path = nx.single_source_dijkstra(G = dg, source = i, target=None, cutoff=None)
        for c2 in range(c1+1, total_bnodes):
          j = backbone_nodes[c2]
          if j not in i_path_length.keys():
            continue
          
          i_j_path = list(i_path[j])
          if not self.is_path_valid_for_static_graph(i_j_path):
            continue
          new_nodes_on_i_j_path = [u for u in i_j_path if u in available_nodes]
          
          new_node_count = len(new_nodes_on_i_j_path)
          if new_node_count+self.static.number_of_nodes() > self.n_max:
            continue
          
          if  new_node_count >= 1:
            i_j_path_benefit = min(source_potential[i], sink_potential[j])/(1.0 * new_node_count)
            j_i_path_benefit = min(source_potential[j], sink_potential[i])/(1.0 * new_node_count)
            #print "DEBUG:i_j_path_benefit, j_i_path_benefit ",i_j_path_benefit,j_i_path_benefit
            if i_j_path_benefit > max_benefit:
              max_benefit = i_j_path_benefit
              max_i = i
              max_j = j
              new_node_list = list(new_nodes_on_i_j_path)
            elif j_i_path_benefit > max_benefit:
              max_benefit =j_i_path_benefit
              max_i = j
              max_j = i
              new_node_list = list(new_nodes_on_i_j_path)
      if max_i == -1:
        break 
      if len(i_j_path)+self.static.number_of_nodes() - 2 > self.n_max:
        break
      for n in new_node_list:
        available_nodes.remove(n)
      self.static.add_path(i_j_path)
      
    static_nodes = self.static.nodes()
    len_static_nodes = len(static_nodes)
    for uindx in range(len_static_nodes - 1):
      u = static_nodes[uindx]
      if self.static.degree(u)+1 > self.static_d_max:
        continue
      for vindx in range(uindx+1, len_static_nodes):
        v= static_nodes[vindx]
        if self.static.degree(v)+1 > self.static_d_max:
          continue
        if self.adj.has_edge(u,v):
          self.static.add_edge(u,v)
        if self.static.degree(u)+1 > self.static_d_max:
          break 
    return

  
  
  def ncr(self,n, r):
    r = min(r, n-r)
    if r == 0: return 1
    numer = reduce(op.mul, xrange(n, n-r, -1))
    denom = reduce(op.mul, xrange(1, r+1))
    return numer//denom

  def find_static_average_flow(self, num_iterations = 100, source_ratio = 0.05):
    print "\t\t@heurisitc placement algo: step: finding static graph avg. flows"
    self.static_avg_flow = 0.0
    self.static_upper_bound_flow = 0.0
    source_sample_size = int(ceil(source_ratio * self.static.number_of_nodes()))
    
    sample_flow_vals = []
    sample_upper_bound_flow_vals = []
    
    allowed_sources = []
    for n in self.static.nodes():
      if n not in self.sinks:
        allowed_sources.append(n)
        
    sink_list = []
    for n in self.sinks:
      if self.static.has_node(n):
        sink_list.append(n)
        
    pattern_count = self.ncr(self.static.number_of_nodes(), source_sample_size)
    real_iteration_count = min(pattern_count, num_iterations)
    
    if len(allowed_sources) == 0:
      return 0,0
    if len(allowed_sources) < source_sample_size:
      source_sample_size = len(allowed_sources)
    for i in range(real_iteration_count):
      #choose source_ratio nodes randomly
      #print "DEBUG:",allowed_sources, "  source_sample_size:",source_sample_size
      sources = random.sample(allowed_sources,source_sample_size)
      

      #run flow algo and find max flow
      static_d = nx.Graph(self.static)
      #print "DEBUG:@find_static_average_flow(): static_d nodes:",static_d.nodes()
      #print "DEBUG:@find_static_average_flow(): static_d src_list:",sources

      static_d = self.add_capacity(g = static_d, 
                                   capacity = self.capacity)
      static_d = self.add_super_source(static_d)
      static_d = self.add_super_sink(static_d)
      #print "DEBUG:s-t path:", [p for p in nx.all_shortest_paths(G=static_d,source='src',target='snk')]
      static_r = flow.shortest_augmenting_path(G=static_d, s='src', t='snk', capacity = 'capacity')
      #set avg_flow and upper_bound_flows
      sample_flow_vals.append(static_r.graph['flow_value'])
      sample_upper_bound_flow_vals.append( sum(self.static.degree(sources).values()) )
      
    self.avg_max_flow_val = mean(sample_flow_vals)
    self.avg_upper_bound_flow_val = mean(sample_upper_bound_flow_vals)

  def solve(self):
    #print "\t@heurisitc placement algo: step i: running greedy target cover...."
    #self.greedy_set_cover_targets()
    #self.get_time_diff(msg = "greedy_set_cover_complete") #----!!!time diff
    
    print "\t@heurisitc placement algo: step i: building backbone network...."
    #self.build_backbone_network()
    
    self.modified_backbone_network()
    self.get_time_diff(msg = "backbone_network_complete") #----!!!time diff
    print "Total Node in the network after step ii: ",self.G_p.number_of_nodes()
    print "\t@heurisitc placement algo: step iii: reducing node degree...."
    self.reduce_node_degree()
    self.get_time_diff(msg = "node_reduction_complete") #----!!!time diff
    print "\t@heurisitc placement algo: after step iii: number of nodes:",self.G_p.number_of_nodes()
    
    print "\t@heurisitc placement algo: step iv-a: builidng dynamic graph...."
    self.run_step_4()
    print "\t@heurisitc placement algo: after step iv: number of nodes:",self.g1.number_of_nodes()
    
    d = nx.Graph(self.g1)
    d = self.add_capacity(g = d, capacity = self.capacity)
    d = self.add_super_source(d)
    d= self.add_super_sink(d)
    r = flow.shortest_augmenting_path(G=d, s='src', t='snk', capacity = 'capacity')
    self.max_flow = r.graph['flow_value']
    
    print "\t@heurisitc placement algo: step iv-b: builidng static graph...."
    self.run_static_modified_step_4()
    static_d = nx.Graph(self.static)
    static_d = self.add_capacity(g = static_d, capacity = self.capacity)
    static_d = self.add_super_source(static_d)
    static_d= self.add_super_sink(static_d)
    static_r = flow.shortest_augmenting_path(G=static_d, s='src', t='snk', capacity = 'capacity')
    self.static_max_flow = static_r.graph['flow_value']
    
    self.find_static_average_flow()
   
    return

 
 
  
  
  
  
