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
    
    #need to reset the relative path as python code is called at './src/test' rather than at './src'
    self.stat_collector.path_to_java_code_for_avg_calc = '../java/tm.jar'
    self.stat_collector.dynamic_graph_spec_file_path = '../java/temp_dynamic_spec.txt'
    self.stat_collector.java_code_output_file_path =  '../java/temp_java_output.txt'
    
    self.stat_collector.runStatCollector()
    print "Dynamic Average Flow:",self.stat_collector.dynamic_avg_flow
    print "Dynamic Upperbound Flow:",self.stat_collector.dynamic_upperbound_flow
  
    
if __name__=='__main__':
  unittest.main(verbosity = 2)
  
  
  
  
  
  
  
  
  
  
  
  