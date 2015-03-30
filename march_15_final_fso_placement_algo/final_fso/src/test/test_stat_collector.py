import unittest
from final_fso.src.stat_collector import StatCollector
import matplotlib.pyplot as plt
import logging
import networkx as nx

class TestStep_4_static(unittest.TestCase):
  def setUp(self):
    unittest.TestCase.setUp(self)
    self.stat_collector = StatCollector('./config.txt')
    #self.gi.generateNodePositions()
    print "Test for StatCollector class.." 
  
  

  def test_Step_4__static_graph_plot(self):
    '''
    selective calls to methods...
    '''
    #self.stat_collector.logger.setLevel(logging.DEBUG)
    self.stat_collector.runInputGenerator()

    #self.stat_collector.logger.setLevel(logging.INFO)
    self.stat_collector.runStep_1()
    self.stat_collector.runStep_2()
    self.stat_collector.runStep_3()
    #self.stat_collector.logger.setLevel(logging.DEBUG)
    self.stat_collector.runStep_4_dynamic()
    self.stat_collector.fso_per_node = 2
    #self.stat_collector.logger.setLevel(logging.DEBUG)
    self.stat_collector.runStep_4_static()
    print "No. of gateways:" ,len(self.stat_collector.gateways)
    
    graphs = [self.stat_collector.adj, 
              self.stat_collector.short_edge_adj, 
              self.stat_collector.backbone_graph_after_step_2, 
              self.stat_collector.backbone_graph,
              self.stat_collector.dynamic_graph,
              self.stat_collector.static_graph]
    
    for i in xrange(len(graphs)):
      plt_graph = graphs[i]
      plt_title = graphs[i].graph['name']
      plt.figure(i+1)
      plt.grid(True)
      plt.xticks( xrange(0,int(self.stat_collector.max_x_coord)+1,int(self.stat_collector.target_spacing)) )
      plt.yticks( xrange(0,int(self.stat_collector.max_y_coord)+1,int(self.stat_collector.target_spacing)) )
      plt.title(plt_title)
      self.stat_collector.visualizeGraph(plt_graph)
    
    plt.show()
  
    
if __name__=='__main__':
  unittest.main(verbosity = 2)
  
  
  
  
  
  
  
  
  
  
  
  