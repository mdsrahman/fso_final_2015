import unittest
from final_fso.src.extended_dynamic_stat_collector import ExtendedDynamicStatCollector
import matplotlib.pyplot as plt
import logging
import networkx as nx

class TestStatCollector(unittest.TestCase):
  def setUp(self):
    unittest.TestCase.setUp(self)
    self.ext_stat_collector = ExtendedDynamicStatCollector('./config.txt')
    #self.gi.generateNodePositions()
    print "Test for ExtDynamicStatCollector class.." 
  
  def visualizeAllGraphs(self):
    covering_node_graph = nx.Graph()
    covering_node_graph.graph['name'] = 'Target-covering nodes only graph'
    covering_node_graph.add_nodes_from(self.ext_stat_collector.node_cover)
    
    graphs = [self.ext_stat_collector.adj, 
              self.ext_stat_collector.short_edge_adj, 
              covering_node_graph,
              self.ext_stat_collector.backbone_graph_after_step_2, 
              self.ext_stat_collector.backbone_graph,
              self.ext_stat_collector.dynamic_graph,
              self.ext_stat_collector.static_graph]
    
    #for i in xrange(len(graphs)):
    for i in xrange(len(graphs)):
      plt_graph = graphs[i]
      plt_title = graphs[i].graph['name']
      plt.figure(i+1)
      
      plt.xticks( xrange(0,int(self.ext_stat_collector.max_x_coord)+1,int(self.ext_stat_collector.target_spacing)) )
      plt.yticks( xrange(0,int(self.ext_stat_collector.max_y_coord)+1,int(self.ext_stat_collector.target_spacing)) )
      plt.axis([-10, self.ext_stat_collector.max_x_coord+10, -10, self.ext_stat_collector.max_y_coord+10])
      plt.grid(True)
      plt.title(plt_title)
      
      self.ext_stat_collector.visualizeGraph(plt_graph)
    
    plt.show()

  def getNodesNotConnectedToGatewaysInDynamicGraph(self):
    '''
    returns the list of nodes not directly connected to the gateways
    must be called after self.adj has been set/built
    '''
    list_of_nodes = []
    for n in self.ext_stat_collector.dynamic_graph.nodes():
      if n not in self.ext_stat_collector.gateways:
        isConnectedToGateways = False
        for g in self.ext_stat_collector.gateways:
          if n==g or self.ext_stat_collector.dynamic_graph.has_edge(n, g):
            isConnectedToGateways = True
            break
        if not isConnectedToGateways:
          list_of_nodes.append(n)
    return list_of_nodes
      
    
  def test_StatCollectorMethods(self):
    '''
    selective calls to methods...
    '''
    #self.ext_stat_collector.logger.setLevel(logging.DEBUG)
    self.ext_stat_collector.runInputGenerator()
    #self.ext_stat_collector.logger.setLevel(logging.INFO)
    print "Input Generator Complete"
    
    #self.ext_stat_collector.logger.setLevel(logging.DEBUG)
    self.ext_stat_collector.runStep_1()
    #self.ext_stat_collector.logger.setLevel(logging.INFO)
    print "step 1 complete"
    
    #self.ext_stat_collector.logger.setLevel(logging.DEBUG)
    self.ext_stat_collector.runStep_2()
    #self.ext_stat_collector.logger.setLevel(logging.INFO)
    print "step 2 complete"
    
    #self.ext_stat_collector.logger.setLevel(logging.DEBUG)
    self.ext_stat_collector.runStep_3()
    #self.ext_stat_collector.logger.setLevel(logging.INFO)
    print "step 3 complete"
    
    #self.ext_stat_collector.logger.setLevel(logging.DEBUG)
    self.ext_stat_collector.runStep_4_dynamic()
    print "step 4-dynamic complete"
    #self.ext_stat_collector.logger.setLevel(logging.INFO)
    
    #self.ext_stat_collector.logger.setLevel(logging.DEBUG)
    self.ext_stat_collector.runStep_4_static()
    #self.ext_stat_collector.logger.setLevel(logging.INFO)
    print "step 4-static complete"
    
    self.ext_stat_collector.runILPSolver()
     
    
    
    #need to reset the relative path as python code is called at './src/test' rather than at './src'
    self.ext_stat_collector.path_to_java_code_for_avg_calc = '../java/tm.jar'
    self.ext_stat_collector.dynamic_graph_spec_file_path = '../java/temp_dynamic_spec.txt'
    self.ext_stat_collector.java_code_stat_file_path = '../java/temp_java_stat.txt'
    self.ext_stat_collector.java_code_stdout_file_path = '../java/temp_java_stdout.txt' 
    
    self.ext_stat_collector.printSummaryAfterSavingStat = True #will now print on screen summary
    
    #self.ext_stat_collector.logger.setLevel(logging.DEBUG)
    self.ext_stat_collector.runStatCollector()
    #self.ext_stat_collector.logger.setLevel(logging.INFO)
    
    #self.ext_stat_collector.logger.setLevel(logging.DEBUG)
    self.ext_stat_collector.runExtendedDynamicStatCollector()
    print "Ext dyn avg:",self.ext_stat_collector.ext_dynamic_avg_flow*self.ext_stat_collector.link_capacity," !!"
    print "Ext static avg:",self.ext_stat_collector.ext_static_avg_flow*self.ext_stat_collector.link_capacity," !!"

#     plt.figure(8)
#     self.ext_stat_collector.visualizeGraph(self.ext_stat_collector.cur_dynamic_graph)
#     plt.figure(9)
#     self.ext_stat_collector.visualizeGraph(self.ext_stat_collector.eq_dynamic_graph)
    #plt.show()
    #self.ext_stat_collector.logger.setLevel(logging.INFO)
    
    #print "Non-gateway nodes not connected to the gateway in the dynamic graph:",
    #print self.getNodesNotConnectedToGatewaysInDynamicGraph()
    #----------------------------------
    self.visualizeAllGraphs()
    #----------------------------------
    
    
if __name__=='__main__':
  unittest.main(verbosity = 2)
  
  
  
  
  
  
  
  
  
  
  
  