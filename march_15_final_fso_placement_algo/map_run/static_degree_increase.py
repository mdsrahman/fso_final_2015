import networkx as nx
import networkx.algorithms.flow as flow
import time
import operator as op
import random
from numpy import mean,ceil
from matplotlib import pyplot as plt
import numpy as np

  
class Compare_Static_VS_Dynamic:
  def __init__(self, adj, static, sinklist, dynamic_avg_max_flow):
    self.adj = nx.Graph(adj)
    self.static = nx.Graph(static)
    self.sinks =  list(sinklist)
    self.dynamic_avg_max_flow = dynamic_avg_max_flow
    self.capacity = 1.0
    
  def compare(self):
    self.find_static_average_flow(200, 0.05)
    self.d_max = max(self.static.degree().values())
    self.init_d_max = self.d_max
    print "Initial d_max:",self.d_max
    print "Dynamic avg flow:",self.dynamic_avg_max_flow
    
    print "Static Initial avg flow:",self.static_avg_flow
    #self.d_max = self.d_max+1 #new d_max
    
    while (self.avg_max_flow_val < self.dynamic_avg_max_flow): #improve GS until desiredobjective.
      edgeAdded = False
      while True:  # improve GS with one extra degree
        #print "DEBUG: current d_max:",self.d_max
        #print "static_nodes:",self.static.nodes()
        R = self.generate_residual_graph(self.static) 
        #print "R.nodes:",R.nodes()  
        
        sReach = nx.bfs_successors(R, "src").keys()
        #print "sReach:",sReach
        tReach = nx.bfs_successors(R, "snk").keys()
        #print "tReach:",tReach
        brk=0
        #r_input = raw_input("press enter:")
        # Add (i,j) from adj s.t. i is in sreach, j is in treach, and degrees of i and d 
        # is less than newdmax.
        for i in sReach: 
          #print "i in sReach:",i
          for j in tReach:
            #print "DEBUG:i for nbr j:",j
            if not self.static.has_edge(i, j) and self.adj.has_edge(i,j) and \
                     self.static.degree(i) < self.d_max+1 \
                     and self.static.degree(j) < self.d_max:    #d_max is fucked up.
              self.static.add_edge(i,j)
              edgeAdded=True
              brk = 1   
              break
          if brk==1: # only add one edge
            break
        if brk==0:  # because no edge added.
          break
        
      self.find_static_average_flow(200, 0.05)
      self.d_max = self.d_max + 1 #new d_max
      if (not edgeAdded):
        break
    return 
  
  '''===================================='''
  def generate_residual_graph(self,g): # original copy passed.
    d =  nx.Graph(g)
    d = self.add_capacity(g = d, capacity = self.capacity) 
    d= self.add_super_source(d)
    d = self.add_super_sink(d)
    
    r = flow.shortest_augmenting_path(G=d, s='src', t='snk', capacity = 'capacity')
    dirR = nx.DiGraph(r)
    #print "self.sink:",self.sinks
    for i,j in dirR.edges():
      if (dirR[i][j]['capacity'] == dirR[i][j]['flow']):
        dirR.remove_edge(i,j)
    return dirR
  
  
  def add_super_source(self, g):
    g.add_node('src')
    source_connected_nodes = list(set(self.adj.nodes()) - set(self.sinks))
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
  
  
  
  def ncr(self,n, r):
    r = min(r, n-r)
    if r == 0: return 1
    numer = reduce(op.mul, xrange(n, n-r, -1))
    denom = reduce(op.mul, xrange(1, r+1))
    return numer//denom

  def find_static_average_flow(self, num_iterations, source_ratio ):
    #print "DEBUG:sink_list:",self.sinks
    #print "\t\t@heurisitc placement algo: step: finding static graph avg. flows"
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
      #print "DEBUG: finding average pattern: iteraton#1",i
      sources = random.sample(allowed_sources,source_sample_size)
  
      static_d = nx.Graph(self.static)

      static_d = self.add_capacity(g = static_d, 
                                   capacity = self.capacity)
      static_d = self.add_super_source(static_d)
      static_d = self.add_super_sink(static_d)

      static_r = flow.shortest_augmenting_path(G=static_d, s='src', t='snk', capacity = 'capacity')
      
      sample_flow_vals.append(static_r.graph['flow_value'])
      sample_upper_bound_flow_vals.append( sum(self.static.degree(sources).values()) )
      
    self.avg_max_flow_val = mean(sample_flow_vals)
    self.avg_upper_bound_flow_val = mean(sample_upper_bound_flow_vals)
    #print "DEBUG:end of average_flow_findng_iteration:"

if __name__== '__main__':
  '''
  n = 50
  n_s =20
  p= 0.4
  adj = nx.fast_gnp_random_graph(n, p)
  node_list  = random.sample(adj.nodes(), n_s)
  static = nx.Graph(adj.subgraph(node_list))'''
  
  total_samples = 50
  
  df = open("./collected/stat/static_graph_dmax_stat.txt","a")
  
  for sample_no in xrange(1, total_samples+1):
    
    f = open('./collected/spec/'+str(sample_no)+'.txt',"r")
    
    gfound = False
    sinks = []
    for line in f:
      if gfound:
        sinks.append(int(line[0:-1]))
      if line[0:-1]=='gateways:':
        gfound = True
    print sinks
    f.close()
    
    adj = nx.Graph()
    adj_data = np.genfromtxt('./collected/output/'+str(sample_no)+'.adj.txt',dtype =int, delimiter=',')
    m,n = adj_data.shape
    for i in xrange(m):
      u = int(adj_data[i][0])
      v = int(adj_data[i][1])
      adj.add_edge(u,v)
       
      
    static = nx.Graph()
    static_data = np.genfromtxt('./collected/output/'+str(sample_no)+'.static.txt',dtype =int, delimiter=',')
    m,n = static_data.shape
    for i in xrange(m):
      u = int(static_data[i][0])
      v = int(static_data[i][1])
      static.add_edge(u,v)

    #print "static #edges:",static.number_of_edges()
  
    
    dynamic = None
    dynamic_avg_max_flow = 5.0 #???
    svd = Compare_Static_VS_Dynamic(adj, static, sinks, dynamic_avg_max_flow)
    svd.compare()
    df.write(str(svd.init_d_max)+","+str(svd.d_max)+","+str(svd.avg_max_flow_val)+"\n")
    print "Final d_max, averge max_flow:",svd.d_max,svd.avg_max_flow_val
  
  df.close()
  
  
  

