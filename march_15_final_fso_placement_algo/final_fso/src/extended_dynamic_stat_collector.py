from stat_collector import StatCollector
import networkx as nx
import random
import networkx.algorithms.flow as flow

class ExtendedDynamicStatCollector(StatCollector):
  def __init__(self, configFile):
    StatCollector.__init__(self, configFile)
    self.weigh_increment = 5
  
  def getEquivalendDynamicGraph(self, in_patternNodes):
    '''
    Args: patternNodes: list of non-gateway source nodes
    Returns: an equivalent dynamic graph
    Processing:
    intialize equiDynamic graph as empty
    initalize curDynamic graph as directed dynamic graph
    phase 1 (connectivity phase):
    -------------------------------
    set-up:
      i. add super-sink and connect it to all the gateway nodes in curDynamic graph
      ii. add 1 as edge weight to all edges
      iii. initialize remaining_in_degree and remaning_out_degree 
          counter for each node to max. permitted degree
        (as determined by fso_per_node or fso_per_gateway params)
      
    1. while there is remaining nodes in patternNodes:
    2. find Dijsktra paths to all nodes taking super-sink as the source
    
    3. add the min. cost path (if any in curDynamic graph) to one of the pattern nodes n
       (both edges and incident nodes on the path except super-sink) to equiDynamic graph, 
       then increment weight of each edge on this path by given param c in curDynamic graph,
       decrement the remaining_degree counter of the nodes on this path, 
        and freeze** on curDynamic graph the edges of all nodes on this path having 0 value
         in remaining_degree counter, 
        also remove from patternNode any node existing on this path 
        (this node thus got a path to gatways already) and continue to step 1
        
    4. if no such path found, find dijsktra paths taking current pattern node n as the source
        and find the min-cost path (if any in curDynamic graph) to one of 
        the pattern nodes already added to 
        equiDynamic graph (thus having a path to the gateways), then add the path to equiDynamic
        graph, increment the weights of the edges on the path in curDynamic graph by given param c,
        decrement the remaining_degree counter of the nodes on this path, 
        and freeze** on curDynamic graph the edges of all nodes on this path having 0 value
         in remaining_degree counter, 
        also remove from patternNode any node existing on this path 
        (this node thus got path already)
        
    5. if a full scan of the patternNodes list was made but no node could be connected to gateways,
    then stop the iteration, the remaining nodes are un-connectable nodes
    
    phase 2 (flow enhancement phase):
    ------------------------------------
    1. add a super-source connecting all the nodes in patterNodes in curDynamic graph (as it is
      with the weights of the edges accumulated in the previous phase)
      
    2. compute Dijsktra path from super-source to super-sink in curDynamic graph, 
      then add the min-cost path (if any) to equiDynamic graph,
      then increment weight of each edge on this path by given param c in curDynamic graph
       and freeze** on curDynamic graph the edges of all nodes on this path having 0 value
         in remaining_degree counter,
       
    3. if no such path found in step 2, then break else continue to step 2
    
    Note: freeze**: if remaining_in_degree is zero for a node n, then remove all other 
        in-coming edges of n in curDynamic graph except those existing in equiDynamic graph
        similarly for remaining_out_degree and out going edges...
        
    Note: edges to suepr-sink and super-source do not contribute to degrees of the nodes
    return the equiDynamic graph
    
    '''
    #initialize phase
    patternNodes = list(in_patternNodes)
    cur_dynamic_graph = nx.DiGraph()
    for u,v in self.dynamic_graph.edges():
      cur_dynamic_graph.add_edge(u,v, weight = 1)
      cur_dynamic_graph.add_edge(v,u, weight = 1)
      
    cur_dynamic_graph.add_node('snk')
    for g in self.gateways:
      cur_dynamic_graph.add_edge(g,'snk',weight = 1)
    
    cur_dynamic_graph.add_node('src')
    for n in patternNodes:
      cur_dynamic_graph.add_edge('src',n,weight = 1)
      
    eq_dynamic_graph = nx.DiGraph()
    
    remaining_in_degree = []
    remaining_out_degree = []
    
    for i in xrange(self.number_of_nodes):
      remaining_in_degree.append(0)
      remaining_out_degree.append(0)
      
    for n in self.dynamic_graph.nodes():
      if n in self.gateways:
        remaining_in_degree[n] = self.fso_per_gateway
        remaining_out_degree[n] = self.fso_per_gateway
      else:
        remaining_in_degree[n] = self.fso_per_node
        remaining_out_degree[n] = self.fso_per_node
    
    #Phase 1   
    while True:
      path = []
      try:
        path = nx.dijkstra_path(cur_dynamic_graph, 'src', 'snk', weight='weight')
      except nx.NetworkXNoPath:
        break
      
      # add path to equiDynamic graph
      eq_dynamic_graph.add_path(path[1:-1])
      self.logger.debug("adding path to eq_dynamic:"+str(path[1:-1]))
      # update degree of each node on this path and freeze degree saturated node, also
      # update the weigh on edges of this path
      u = path[1]
      for v in path[2:-1]:
        cur_dynamic_graph[u][v]['weight'] += self.weigh_increment
        if remaining_out_degree[u]>=1:
          remaining_out_degree[u] -= 1
          self.logger.debug("\t u,remaining_out_degree[u]:"+str(u)+","+str(remaining_out_degree[u]))
          if remaining_out_degree[u] == 0:
            self.logger.debug("freezing(out) node:"+str(u))
            for x,y in cur_dynamic_graph.out_edges(u):
              if not eq_dynamic_graph.has_edge(x, y):
                cur_dynamic_graph.remove_edge(x, y)
                self.logger.debug("\t removing edge:"+str(x)+"-"+str(y))
        
        if remaining_in_degree[v]>=1: 
          remaining_in_degree[v] -= 1
          self.logger.debug("\t v,remaining_in_degree[v]:"+str(v)+","+str(remaining_in_degree[v]))
          if remaining_in_degree[v] == 0:
            self.logger.debug("freezing(in) node:"+str(u))
            for x,y in cur_dynamic_graph.in_edges(v):
              if not eq_dynamic_graph.has_edge(x,y):
                cur_dynamic_graph.remove_edge(x,y)
                self.logger.debug("\t removing edge:"+str(x)+"-"+str(y))
        u=v
        
      # remove nodefrom patternNode
      patternNodes.remove(path[1])
      
      #disconenct the edge from src to this pattern node in cur_dynamic_graph
      cur_dynamic_graph.remove_edge('src', path[1])
      
    #phase 2
    #add back the src-to-pattern node edges
    for n in in_patternNodes:
      cur_dynamic_graph.add_edge('src',n,weight = 1)
      
    empty_iteration_count = 0
    
    while empty_iteration_count<100:
      self.logger.debug("empty_iteration_count:"+str(empty_iteration_count))
      added_new_edge = False
      path = []
      try:
        path = nx.dijkstra_path(cur_dynamic_graph, 'src', 'snk', weight='weight')
      except nx.NetworkXNoPath:
        break
      
      # update degree of each node on this path and freeze degree saturated node, also
      # update the weigh on edges of this path
      u = path[1]
      for v in path[2:-1]:
        cur_dynamic_graph[u][v]['weight'] += self.weigh_increment
        if not eq_dynamic_graph.has_edge(u,v):
          added_new_edge = True
        
        if remaining_out_degree[u]>=1:
          remaining_out_degree[u] -= 1
          self.logger.debug("\t u,remaining_out_degree[u]:"+str(u)+","+str(remaining_out_degree[u]))
          if remaining_out_degree[u] == 0:
            self.logger.debug("freezing(out) node:"+str(u))
            for x,y in cur_dynamic_graph.out_edges(u):
              if not eq_dynamic_graph.has_edge(x, y):
                cur_dynamic_graph.remove_edge(x, y)
                self.logger.debug("\t removing edge:"+str(x)+"-"+str(y))
        
        if remaining_in_degree[v]>=1: 
          remaining_in_degree[v] -= 1
          self.logger.debug("\t v,remaining_in_degree[v]:"+str(v)+","+str(remaining_in_degree[v]))
          if remaining_in_degree[v] == 0:
            self.logger.debug("freezing(in) node:"+str(u))
            for x,y in cur_dynamic_graph.in_edges(v):
              if not eq_dynamic_graph.has_edge(x,y):
                cur_dynamic_graph.remove_edge(x,y)
                self.logger.debug("\t removing edge:"+str(x)+"-"+str(y))
        u=v
            # add path to equiDynamic graph
      if added_new_edge:
        eq_dynamic_graph.add_path(path[1:-1]) 
        self.logger.debug("phase 2: adding path to eq_dynamic:"+str(path[1:-1]))
      #instead of disconnecting, increment the src-node weight
      cur_dynamic_graph['src'][path[1]]['weight'] += self.weigh_increment
      if added_new_edge:
        empty_iteration_count = 0
      else:
        empty_iteration_count += 1
      
    cur_dynamic_graph.remove_node('src')
    cur_dynamic_graph.remove_node('snk')
    return eq_dynamic_graph, cur_dynamic_graph, patternNodes
      
      
      
  def runExtendedDynamicStatCollector(self):
    '''
    runs this stat colletor
    processing:
      for each iteration 
      i) select pattern nodes
      ii) find an equivalent dynamic graph, 
          if its the first iteration, save it as equivalen static graph 
      iii) run max flow and save it
      for all iterations, find the avg max flow using the saved values
    '''
    max_flow_list_dyn = []
    max_flow_list_stat = []
    candidate_pattern_nodes = list(set(self.dynamic_graph.nodes()) - set(self.gateways))
    if not candidate_pattern_nodes: #no non-gateway nodes in the static graph, so this avg finding is mute
      self.ext_dynamic_avg_flow = 0.0
      self.logger.info("No non-gateway node found in static graph, avg and upperbound max flows set to 0!!")
      return
    number_of_candidate_pattern_nodes = len(candidate_pattern_nodes)
    number_of_pattern_nodes = \
      int(round(1.0*number_of_candidate_pattern_nodes * self.percent_of_pattern_nodes_in_avg_flow_calculation/100.0, 0))
    if number_of_pattern_nodes<1: #check if the ratio was too low
      number_of_pattern_nodes = 1
    
    eq_static_graph = None
    for i in xrange(self.number_of_pattern_in_avg_flow_calculation):
      pattern_nodes = random.sample(candidate_pattern_nodes, number_of_pattern_nodes)
      #self.logger.debug("pattern nodes:"+str(pattern_nodes))
      eq_dyamic_graph, self.cur_dynamic_graph, remaining_pattern_nodes = self.getEquivalendDynamicGraph(pattern_nodes)
      #self.logger.debug("un-connectable pattern nodes:"+str(remaining_pattern_nodes))
      
        
      for u,v in eq_dyamic_graph.edges():
        eq_dyamic_graph[u][v]['capacity'] =  1.0
        
      if i==0:
        eq_static_graph = nx.DiGraph(eq_dyamic_graph)
      
      eq_flow_comp_static_graph = nx.DiGraph(eq_static_graph)
            #add source node 
      eq_dyamic_graph.add_node('src')
      for n in pattern_nodes:
        eq_dyamic_graph.add_edge('src',n, capacity = float('inf'))
      
      eq_dyamic_graph.add_node('snk')
      for g in self.gateways:
        eq_dyamic_graph.add_edge(g, 'snk', capacity = float('inf'))
      
      
      eq_flow_comp_static_graph.add_node('src')
      for n in pattern_nodes:
        eq_flow_comp_static_graph.add_edge('src',n, capacity = float('inf'))
      
      eq_flow_comp_static_graph.add_node('snk')
      for g in self.gateways:
        eq_flow_comp_static_graph.add_edge(g, 'snk', capacity = float('inf'))
      
        
      residual_max_flow_dyn = flow.shortest_augmenting_path(G=eq_dyamic_graph, s='src', t='snk')
      max_flow_list_dyn.append(residual_max_flow_dyn.graph['flow_value'])
      
      residual_max_flow_stat = flow.shortest_augmenting_path(G=eq_flow_comp_static_graph, s='src', t='snk')
      max_flow_list_stat.append(residual_max_flow_stat.graph['flow_value'])
      
    self.ext_dynamic_avg_flow = 1.0*sum(max_flow_list_dyn)/len(max_flow_list_dyn)
    self.ext_static_avg_flow = 1.0*sum(max_flow_list_stat)/len(max_flow_list_stat)
    
    