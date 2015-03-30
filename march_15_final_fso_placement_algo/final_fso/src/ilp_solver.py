
from step_4_static import Step_4_static

class ILPSolver(Step_4_static):
  '''
  processes the problem formulation and solving of Relaxed-ILP of the input instance
  #---class field descriptions------
  max_flow_derived_by_relaxed_ILP(float): the maximum flow value as 
                  determined by the relaxed ILP solver, value is set in runILPSolver() method
  #----end of class field descriptions---
  '''
  def __init__(self,configFile):
    Step_4_static.__init__(self, configFile)
    #---class fields-------
    
    #---end of class fields----
  
  def runILPSolver(self):
    '''
    this class processes all the steps related to Relaxed ILP problem formulation
    i) formulate the problem
    ii) call the solver
    iii) save the value
    '''
    self.logger.info("Skipping Relaxed ILP Solver.....")