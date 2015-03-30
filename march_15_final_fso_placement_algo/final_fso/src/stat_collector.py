import subprocess
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
    self.dynamic_upperbound_flow = None
    self.dynamic_avg_flow = None
    self.path_to_java_code_for_avg_calc = './java/tm.jar'
    self.dynamic_graph_spec_file_path = './java/temp_dynamic_spec.txt'
    self.java_code_output_file_path = './java/temp_java_output.txt'
    #---end of class fields------
  def createDynamicGraphSpecOutputFile(self):
    '''
    creates the temporary dynamic spec file and save the self.dynamic_graph according
    to TM's spec
    '''
    with open(self.dynamic_graph_spec_file_path, 'w') as f:
      f.write("trafficSources:\n")
      for n in self.dynamic_graph.nodes():
        f.write(str(n)+"\n")
      f.write('\n')
      
      
      #---FSONodes:
      f.write("FSONodes:\n")
      nodes = self.dynamic_graph.nodes() 
      for n in nodes:
        for fso in range(1, self.fso_per_node+1):
          f.write(str(n)+"_fso"+str(fso)+"\n")
      f.write('\n')   
      
      #---FSOLinks:---
      f.write("FSOLinks:\n")   
      edges = self.dynamic_graph.edges()
      for u,v in edges:
        for fso1 in range(1, self.fso_per_node+1):
          for fso2 in range(1, self.fso_per_node+1):  
            #"0_0_fso2To2_0_fso1 10Gbps"
            f_text = str(u)+"_fso"+str(fso1)+"To"\
                    +str(v)+"_fso"+str(fso2)+" "+str(self.link_capacity)+"Mbps\n" 
            f.write(f_text)
            f_text = str(v)+"_fso"+str(fso2)+"To"\
                    +str(u)+"_fso"+str(fso1)+" "+str(self.link_capacity)+"Mbps\n" 
            f.write(f_text)
      f.write('\n')   
      #------gateways--:
      f.write('gateways:\n')
      for n in self.gateways:
        f.write(str(n)+"\n")
        
  def callJavaCodeToGetDynamicAvgFlow(self):
    '''
    i) prepare the dynamic graph spec and save it in ./java/temp_dynamic_spec.txt
    ii) call the program ./java/tm.jar
    iii) after the program returns, read the file ./java/temp_java_output.txt and collect
       the upper-bound and avg-flow and save those as floats
    '''
    self.createDynamicGraphSpecOutputFile()
  
    subprocess.call(['java','-jar',
                     self.path_to_java_code_for_avg_calc,
                     self.dynamic_graph_spec_file_path,
                     self.java_code_output_file_path,
                     str(self.percent_of_pattern_nodes_in_avg_flow_calculation),
                     str(self.number_of_pattern_in_avg_flow_calculation) 
                     ]) 
    with open(self.java_code_output_file_path,'r') as f:
      for line in f:
        vals = line.split(',')
        self.dynamic_upperbound_flow = float(vals[0])
        self.dynamic_avg_flow = float(vals[1])
      
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
    self.logger.info("in runStatCollector...")
    self.callJavaCodeToGetDynamicAvgFlow()
    
    
    