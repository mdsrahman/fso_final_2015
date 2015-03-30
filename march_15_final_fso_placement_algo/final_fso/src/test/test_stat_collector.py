import unittest
from final_fso.src.stat_collector import StatCollector
import matplotlib.pyplot as plt
import logging
import networkx as nx

class TestStatCollector(unittest.TestCase):
  def setUp(self):
    unittest.TestCase.setUp(self)
    self.stat_collector = StatCollector('./config.txt')
    #self.gi.generateNodePositions()
    print "Test for StatCollector class.." 
  
  

  def test_StatCollectorMethods(self):
    '''
    selective calls to methods...
    '''
    self.stat_collector.logger.setLevel(logging.DEBUG)
    self.stat_collector.runInputGenerator()
    
    self.stat_collector.runStep_1()
    self.stat_collector.logger.setLevel(logging.INFO)
    
    #------------------------------------------------------------------
    covering_node_graph = nx.Graph()
    covering_node_graph.graph['name'] = 'Target-covering nodes only graph'
    covering_node_graph.add_nodes_from(self.stat_collector.node_cover)
    #--------------------------------------------------------------------
    
    self.stat_collector.runStep_2()
    self.stat_collector.runStep_3()
    self.stat_collector.runStep_4_dynamic()
    self.stat_collector.runStep_4_static()
    self.stat_collector.runILPSolver()
     
    #need to reset the relative path as python code is called at './src/test' rather than at './src'
    self.stat_collector.path_to_java_code_for_avg_calc = '../java/tm.jar'
    self.stat_collector.dynamic_graph_spec_file_path = '../java/temp_dynamic_spec.txt'
    self.stat_collector.java_code_output_file_path =  '../java/temp_java_output.txt'
     
     
    self.stat_collector.runStatCollector()
    print "Dynamic Average Flow:",self.stat_collector.dynamic_avg_flow
    print "Dynamic Upperbound Flow:",self.stat_collector.dynamic_upperbound_flow
    print "Static Average Flow:",self.stat_collector.static_avg_flow
    print "Static Upperbound Flow:",self.stat_collector.static_upperbound_flow
    
    
    graphs = [self.stat_collector.adj, 
              self.stat_collector.short_edge_adj, 
              covering_node_graph,
              self.stat_collector.backbone_graph_after_step_2, 
              self.stat_collector.backbone_graph,
              self.stat_collector.dynamic_graph,
              self.stat_collector.static_graph]
    
    #for i in xrange(len(graphs)):
    for i in xrange(len(graphs)):
      plt_graph = graphs[i]
      plt_title = graphs[i].graph['name']
      plt.figure(i+1)
      
      plt.xticks( xrange(0,int(self.stat_collector.max_x_coord)+1,int(self.stat_collector.target_spacing)) )
      plt.yticks( xrange(0,int(self.stat_collector.max_y_coord)+1,int(self.stat_collector.target_spacing)) )
      plt.axis([0, self.stat_collector.max_x_coord, 0, self.stat_collector.max_y_coord])
      plt.grid(True)
      plt.title(plt_title)
      
      self.stat_collector.visualizeGraph(plt_graph)
    
    plt.show()
if __name__=='__main__':
  unittest.main(verbosity = 2)
  
  
  
  
  
  
  
  
  
  
  
  