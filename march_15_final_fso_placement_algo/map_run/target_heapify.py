
import heapq
from collections import defaultdict
import random
import numpy as np
#import itertools

class MyHeap: 
  pq = []                         # list of entries arranged in a heap
  entry_finder = {}               # mapping of tasks to entries
  REMOVED = '<removed-task>'      # placeholder for a removed task
  #counter = itertools.count()     # unique sequence count
  
  def add_item(self, task, priority=0):
      'Add a new task or update the priority of an existing task'
      if task in self.entry_finder:
        self.remove_item(task)
      #count = next(self.counter)
      entry = [priority, task]
      self.entry_finder[task] = entry
      heapq.heappush(self.pq, entry)
  
  def remove_item(self,task):
      'Mark an existing task as REMOVED.  Raise KeyError if not found.'
      #print "DEBUG:entry_finder",self.entry_finder
      entry = self.entry_finder.pop(task)
      entry[1] = self.REMOVED
  
  def pop_item(self):
      'Remove and return the lowest priority task. Raise KeyError if empty.'
      while self.pq:
          priority, task = heapq.heappop(self.pq)
          if task is not self.REMOVED:
            del self.entry_finder[task]
            return priority, task
      return None,  None
      #raise KeyError('pop from an empty priority queue')


class Target_Node_Assoc:
  def __init__(self, node_x, node_y, target_interval, node_coverage, node_bin_interval, gen_tn = False):
    
    self.number_of_nodes = len(node_x)
    self.max_x = max(node_x)
    self.max_y = max(node_y)
    self.target_interval = target_interval
    self.node_coverage = node_coverage
    self.node_x = list(node_x)
    self.node_y = list(node_y)
    self.node_target_count = np.zeros(self.number_of_nodes, dtype = int)
    self.node_cover = []
    self.node_bin_interval = node_bin_interval
    self.node_bin = {}
    self.T_N = None
    self.gen_tn = gen_tn
    self.bin_nodes()
    
    self.max_target_x = int(self.max_x // self.target_interval)
    self.max_target_y = int(self.max_y // self.target_interval)
    self.total_targets = (self.max_target_x+1) * (self.max_target_y +1)
    #print  "max_target_x, max_target_y:", max_target_x, max_target_y
    self.targets_covered = 0
    self.target = np.zeros((self.max_target_x+1, self.max_target_y+1), dtype=bool)
    self.h = MyHeap()
    #print self.node_x
    #print self.node_y
  
  

  def build_heap(self):
    self.T_N =defaultdict(list)
    for i in xrange(self.number_of_nodes):
      total_targets_covered = 0
      target_coord_list = self.get_targets_covered_by_node(i)
      for target_coord in target_coord_list :
        k,l = target_coord
        tindex = k*self.max_target_y + l
        if self.gen_tn:
          self.T_N[tindex].append(i)
        if self.is_covered_by_node(k,l,i):
          total_targets_covered += 1    
      self.node_target_count[i] = total_targets_covered
      self.h.add_item(i, -total_targets_covered)
      #if i%100==0: 
      #  print "heaped", i
    return
  
  def bin_nodes(self):
    self.bin_x_max = int(self.max_x // self.node_bin_interval  )
    self.bin_y_max = int(self.max_y // self.node_bin_interval  )
    print "in bin_nodes, interval, x_max, bin_y_max", self.node_bin_interval, self.max_x
    for i in xrange(self.bin_x_max+1):
      self.node_bin[i] = {}
      for j in xrange(self.bin_y_max+1):
        self.node_bin[i][j] = []
    #print "in bin_nodes, total, bin_x_max, bin_y_max", self.number_of_nodes, self.bin_x_max, self.bin_y_max
    for n in xrange(self.number_of_nodes):
      #print "binning", n
      x = self.node_x[n]
      y = self.node_y[n]
      bin_x = int( x // self.node_bin_interval)
      bin_y = int( y // self.node_bin_interval)
      self.node_bin[bin_x][bin_y].append(n)
    return
  
  def get_targets_covered_by_node(self,n):  #returns a SUPERSET.
    x = self.node_x[n]
    y = self.node_y[n]
    x_min = int(max(0,  x - self.node_coverage) // self.target_interval)
    x_max = int(min(self.max_x, x + self.node_coverage) // self.target_interval)
    y_min = int(max(0,  y - self.node_coverage) // self.target_interval)
    y_max = int(min(self.max_y, y + self.node_coverage) // self.target_interval)
    ret_val = [] 
    for k in xrange(x_min, x_max+1):
      for l in xrange(y_min, y_max+1):
        ret_val.append((k,l))
    #print "DEBUG@target_heapify(..):k,l,n,ret_val:",k,l,n,ret_val 
    #ri = raw_input("enter:")
    return ret_val
  
  def get_nodes_covering_target(self,i,j):   #returns Supersete
    tx = i*self.target_interval
    ty = j*self.target_interval
  
    min_bin_x = int(max(0, tx - self.node_coverage) // self.node_bin_interval)
    max_bin_x = int(min(self.max_x, tx + self.node_coverage) // self.node_bin_interval)
    min_bin_y = int(max(0, ty - self.node_coverage) // self.node_bin_interval)
    max_bin_y = int(min(self.max_y, ty + self.node_coverage) // self.node_bin_interval)
    
    nodes = set()
    for i in xrange(min_bin_x, max_bin_x+1):
      for j in xrange(min_bin_y, max_bin_y+1):
        nodes.update(self.node_bin[i][j])
    return nodes
  
  def get_overlapping_nodes(self, n):   #returns Supersete
    x = self.node_x[n]
    y = self.node_y[n]
    x_min = int(max(0,  x - 2*self.node_coverage) // self.node_bin_interval)
    x_max = int(min(self.max_x, x + 2*self.node_coverage) // self.node_bin_interval)
    y_min = int(max(0,  y - 2*self.node_coverage) // self.node_bin_interval)
    y_max = int(min(self.max_y, y + 2*self.node_coverage) // self.node_bin_interval)
    nodes = set()
    for i in xrange(x_min, x_max+1):
      for j in xrange(y_min, y_max+1):
        nodes.update(self.node_bin[i][j])
    return nodes
  
  def is_covered_by_node(self,i,j,n):
    threshold = self.node_coverage
    x1 = i*self.target_interval
    y1 = j*self.target_interval
    x2 = self.node_x[n]
    y2 = self.node_y[n]
    dist = (x1-x2)**2+(y1-y2)**2
    if dist <= threshold*threshold:
      return True
    else:
      return False
    
  def heuristic_set_cover(self):

    self.targets_covered = 0
   
    while self.h.pq and self.targets_covered < self.total_targets:
      n_priority, n = self.h.pop_item()
      self.node_target_count[n] = 0 # not needed perhaps.
      if n_priority == 0 or n == None:
        break
      targets_covered_by_n = 0
      t_index_covered_by_n = self.get_targets_covered_by_node(n)
      overlapping_nodes = self.get_overlapping_nodes(n)
      #r_t = raw_input("press enter:")
      for target_coord in t_index_covered_by_n:
        k,l = target_coord
        if not self.target[k][l] and self.is_covered_by_node(k, l, n):
          self.target[k][l] = True
          targets_covered_by_n += 1 # perhaps not used, except debug.
          self.targets_covered += 1
          for v in overlapping_nodes:
            if v !=n and self.node_target_count[v] !=0 and self.is_covered_by_node(k,l,v): 
              self.node_target_count[v] -= 1       
      for v in overlapping_nodes:
        if v!=n and self.node_target_count[v] !=0:
          self.h.add_item(v,-self.node_target_count[v])
    
      
      if targets_covered_by_n > 0:
        self.node_cover.append(n)
        if (100*self.targets_covered/self.total_targets)%5==0:
          print "DEBUG:@target_heapify(..):%node_covered:",\
          "Total targets:",self.total_targets, " targets covered:",self.targets_covered,\
          " percent of coverage:",\
          100*self.targets_covered/self.total_targets," current #node:",len(self.node_cover)
          #r_input = raw_input("press_enter:")
    return
  
  ''' covering_nodes = self.get_nodes_covering_target(k, l) 
          for v in covering_nodes:
            if v !=n and self.is_covered_by_node(k, l, v): 
              self.node_target_count[v] -= 1
              self.h.add_item(v, - self.node_target_count[v])'''
 
  def get_node_cover(self):
    
    self.build_heap()
    
    print "DEBUG:association complete..."
    self.heuristic_set_cover()
    #print "DEBUG:",self.targets_covered
      #print "DEBUG:",
    return self.node_cover
  
if __name__ =='__main__':
  node_bin_interval  = 100
  number_of_nodes = 1000
  node_coverage = 1000
  max_x = 100
  max_y = 100
  target_interval = 20
  tna = Target_Node_Assoc(number_of_nodes, max_x, max_y, target_interval, node_coverage, node_bin_interval ) 
  node_cover = tna.get_node_cover()
  print sorted(node_cover)
  
  
  
  
  
  
  
  
