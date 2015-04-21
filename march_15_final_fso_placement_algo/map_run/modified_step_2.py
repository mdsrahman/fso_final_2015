import networkx as nx
import random 
import heapq as hq
import numpy as np
import time
class Modified_Step_2():
  def __init__(self, adj, sink, sc_node):

    self.adj = nx.Graph(adj)
    
    self.node_list = self.adj.nodes()
    self.sink = list(sink)
    self.sc_node = list(sc_node)
    self.bg = None
    '''print "@Modified_Step_2:self.adj.#nodes",self.adj.number_of_nodes()
    print "@Modified_Step_2:self.adj.#edgds",self.adj.number_of_edges()
    print "@Modified_Step_2:self.adj.#sinks",len(self.sink)
    print "@Modified_Step_2:self.adj.#sc_node",len(self.sc_node)
    '''

  def run_bfs(self):
    self.bg = nx.Graph()
    self.bg.graph['name'] = 'Background Graph'
    self.n = []
    
    self.n_indx = np.zeros(self.adj.number_of_nodes(), dtype =int)
    for indx, i in enumerate(self.n_indx):
      self.n_indx[indx] = -1
    
    counter=0
    for k in self.sink:
      self.n.append(k)
      self.n_indx[k]=counter
      counter += 1
      
    for k in self.sc_node:
      self.n.append(k)
      self.n_indx[k]=counter
      counter += 1
    
    print "total nodes for bfs-path pairs:", len(self.n)
    
    total_n = len(self.n)
    
    self.distance = np.zeros((total_n,total_n), dtype = int)
    
    for i in xrange(total_n):
      for j in xrange(total_n):
        self.distance[i][j] = 20000   #infinity.
    
    self.bfs_paths = {}
    for i in xrange(total_n):
      self.bfs_paths[i]={}
      for j in xrange(total_n):
        self.bfs_paths[i][j] =[]
    
    e_time = time.clock()
    counter = 0
    bfs_graph = nx.Graph()
    
    for i_indx,i in enumerate(self.n):
      counter += 1
      path = nx.single_source_shortest_path(self.adj,i)
      reachable_nodes = path.keys()
      temp_set = list(set(reachable_nodes).intersection(set(self.n))) # sc+sink?
      for j in temp_set:
        path_len = len(path[j])
        j_indx = self.n_indx[j] 
        self.distance[i_indx][j_indx] = path_len
        self.bfs_paths[i_indx][j_indx] = list(path[j])
      if counter%100==0:
        print "DEBUG: end-oneWhile:",time.clock() - e_time
        e_time = time.clock()
      del path
      
      
    #for g in self.n:
    #  self.bg.add_node(g)    
    self.h = []
    for g in self.sink:
      #print "DEBUG:pushing g:",g
      for n_indx, n in enumerate(self.n):
        g_indx = self.n_indx[g]
        priority = self.distance[g_indx][n_indx]
        if priority > 0:
          hq.heappush(self.h, (priority, g_indx, n_indx))
        
    uncovered_target = list(self.sc_node)
    while self.h and uncovered_target:
      d, i_indx, j_indx = hq.heappop(self.h)
      if self.n[j_indx] in uncovered_target:
        path = self.bfs_paths[i_indx][j_indx] 
      
        self.bg.add_path(path)
        #print "DEBUG: path:",path
        #print "DEBUG:self.bg.edges():",self.bg.edges()
        uncovered_target.remove(self.n[j_indx])
        for k_indx,k in enumerate(self.n):
          j_indx = self.n_indx[j]
          priority =  self.distance[j_indx][k_indx]
          if priority > 0 and k in uncovered_target:
            hq.heappush(self.h, (priority, j_indx, k_indx))
               
            
            
            
