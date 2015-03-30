
from ilp_solver import ILPSolver

class StatCollector(ILPSolver):
  '''
  Responsible for saving all the graphs, generating and saving all the experimental data
  #---descriptions of class-fields----
  
  #-----end of descriptions of class fields-----
  '''
  def __init__(self,configFile):
    ILPSolver.__init__(self, configFile)
    #---class fields-------
    
    
    #---end of class fields------
  
  def runStatCollector(self):
    '''
    all the processing related to this class are done here
    tasks:
      i) generate the dynamic graph and save it in the appropriate format
        in the current directory as temp_dynamic_graph.txt (overwrite mode)
      ii) call TM's code (jar file in the same directory) and wait for its termination
      iii) retrieve the avg. max flow and upper bound flow from the file java_output.txt 
        (overwritten) file and save it
      iv) run method to get upper-bound flow and avg. max flow for static graph
      v) save all the experiment stats in the self.output_statistics_file file (append mode)
      vi) save all the graphs with proper title in the self.graph_output_folder folder
    '''
    
    
    
    