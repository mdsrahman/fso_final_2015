import unittest
from final_fso.src.map_to_graph_generator import MapToGraphGenerator

class TestMapToGraphGenerator(unittest.TestCase):
  def setUp(self):
    mapFilePath = './maps/small_nyc_test.osm'
    outputFilePath = './maps/graphs/small_nyc_test_edges.txt'
    short_edge_length = 100
    long_edge_length = 1000
    
    unittest.TestCase.setUp(self)
    self.m2gg = MapToGraphGenerator(mapFilePath, outputFilePath, short_edge_length, long_edge_length, False)
    print "Test for MapToGraphGenerator....."
    

  def test_Step2_graph_plot(self):
    '''
    call the method of MapToGraphGenerator...
    '''
    self.m2gg.generateMapToGraph()
    self.m2gg.debugGenerateVisualGraph()
    self.m2gg.debugPrintSummary()
    
if __name__=='__main__':
  unittest.main(verbosity = 2)
  
  
  
  
  
  
  
  
  
  
  
  