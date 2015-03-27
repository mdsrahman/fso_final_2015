import unittest
from final_fso.src.target_handler import TargetHandler


class TestTargetHandler(unittest.TestCase):
  def setUp(self):
    unittest.TestCase.setUp(self)
    self.th = TargetHandler('./config.txt')
    #self.gi.generateNodePositions()
    print "Test for TargetHandler.."
  

  def test_heuristicTargetCover(self):
    print "Set Covers:", sorted(self.th.node_cover)
    print "Total Set Cover nodes:",len(self.th.node_cover)
    print "Total Nodes:",self.th.number_of_nodes
    print "Targets Covered:",self.th.no_of_targets_covered
    print "Total Targets:",self.th.total_targets
    print "Is Node-heap empty:",self.th.node_hp.isHeapEmpty()
    
    
  
    
if __name__=='__main__':
  unittest.main(verbosity = 2)
  
  
  
  
  
  
  
  
  
  
  
  