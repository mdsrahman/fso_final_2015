import unittest
from final_fso.src.step_2 import Step_2


class TestTargetHandler(unittest.TestCase):
  def setUp(self):
    unittest.TestCase.setUp(self)
    self.s2 = Step_2('./config.txt')
    #self.gi.generateNodePositions()
    print "Test for Step_2 class.."
  

  def test_heuristicTargetCover(self):
    '''
    selective calls to methods...
    '''
    
  
    
if __name__=='__main__':
  unittest.main(verbosity = 2)
  
  
  
  
  
  
  
  
  
  
  
  