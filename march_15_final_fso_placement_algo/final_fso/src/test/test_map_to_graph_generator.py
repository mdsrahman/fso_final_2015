import unittest
from final_fso.src.map_to_graph_generator import MapToGraphGenerator

class TestMapToGraphGenerator(unittest.TestCase):
  def setUp(self):
    mapFilePath = './maps/nyc.osm'
    outputFilePath = './maps/graphs/test.txt'
    unittest.TestCase.setUp(self)
    self.m2gg = MapToGraphGenerator(mapFilePath, outputFilePath)
    print "Test for MapToGraphGenerator....."
    

  def test_Step2_graph_plot(self):
    '''
    call the method of MapToGraphGenerator...
    '''
    self.m2gg.generateMapToGraph()
    self.m2gg.debugGenerateVisualGraph()
    
if __name__=='__main__':
  unittest.main(verbosity = 2)
  
  
  
  
  
  
  
  
  
  
  
  