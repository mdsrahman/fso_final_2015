import unittest
from final_fso.src.step_3 import Step_3
import matplotlib.pyplot as plt

class TestStep_3(unittest.TestCase):
  def setUp(self):
    unittest.TestCase.setUp(self)
    self.s3 = Step_3('./config.txt')
    #self.gi.generateNodePositions()
    print "Test for Step_3 class.."
  

  def test_Step3_graph_plot(self):
    '''
    selective calls to methods...
    '''
    self.s3.runInputGenerator()
    self.s3.runStep_1()
    self.s3.runStep_2()
    self.s3.runStep_3()
    
    graphs = [self.s3.adj, 
              self.s3.short_edge_adj, 
              self.s3.backbone_graph_after_step_2, 
              self.s3.backbone_graph]
    graph_title = ['Adjacency graph', 
                   'Short Edge Adjacency graph', 
                   'Backbone graph after step 2', 
                   'Backbone graph step 3']
    
    for i in xrange(len(graphs)):
      plt_graph = graphs[i]
      plt_title = graph_title[i]
      plt.figure(i+1)
      plt.grid(True)
      plt.xticks( xrange(0,int(self.s3.max_x_coord)+1,int(self.s3.target_spacing)) )
      plt.yticks( xrange(0,int(self.s3.max_y_coord)+1,int(self.s3.target_spacing)) )
      plt.title(plt_title)
      self.s3.visualizeGraph(plt_graph)
    
    plt.show()
  
    
if __name__=='__main__':
  unittest.main(verbosity = 2)
  
  
  
  
  
  
  
  
  
  
  
  