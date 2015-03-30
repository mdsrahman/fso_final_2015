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
    self.stat_collector.runInputGenerator()
    self.stat_collector.runStep_1()
    self.stat_collector.runStep_2()
    self.stat_collector.runStep_3()
    self.stat_collector.runStep_4_dynamic()
    self.stat_collector.fso_per_node = 2
    self.stat_collector.runStep_4_static()
    self.stat_collector.runILPSolver()
    self.stat_collector.runStatCollector()
    
  
    
if __name__=='__main__':
  unittest.main(verbosity = 2)
  
  
  
  
  
  
  
  
  
  
  
  