
from step_4_dynamic import Step_4_dynamic

class Step_4_static(Step_4_dynamic):
  '''
  This class handles all processing related to the static graph
  #-----class-field description------
  ''' 
  def __init__(self,configFile):
    Step_4_dynamic.__init__(self, configFile)
    #---class fields------
    
    #---end of class fields
  
  def runStep_4_static(self):
    '''
    entry point for processing all tasks related to this class
    almost modeled on the steps of runStep_4_dynamic() of Step_4_dynamic
    except few exceptions
    
    '''