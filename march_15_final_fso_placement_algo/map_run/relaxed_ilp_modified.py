from pycpx import CPlexModel
import networkx as nx
import numpy as np
import time
 

class ILP_Relaxed():
  def __init__(self,
               nmax,
               dmax,
               adj,
               T_N,
               sinks,
               disconnected_nodes
               ):
    print "ILP_Relaxed initialized...., dmax,nmax:", dmax,nmax
    self.adj = adj
    self.T_N = T_N
    self.sinks  = sinks
    self.n_max = nmax
    self.d_max = dmax
    self.disconnected_nodes = disconnected_nodes
    
  def solve(self):
    n = self.adj.number_of_nodes()
    N =  1.00*n
    m = CPlexModel()
    
    print "Allocating Variables.....n:",n
    X = m.new(size=n, vtype=float,lb=0,ub=1)
    E = m.new(size=(n,n), vtype=float,lb=0,ub=1)
    Y = m.new(size=n, vtype=float,lb=0,ub=1)
    B = m.new(size=(n,n), vtype=float,lb=0,ub=1)
    F = m.new(size=(n,n), vtype=float,lb=0, ub=1)
    F_S = m.new(size=n, vtype=float,lb=0)
    F_T = m.new(size=n, vtype=float,lb=0)
    G = m.new(size=(n,n), vtype=float,lb=0,ub=1)
    G_S = m.new(size=n, vtype=float,lb=0)
    G_T = m.new(size=n, vtype=float,lb=0)

    print "Finished Initializing variables....."
    #print "n:",n
    #----------------------------------------
    #                equation-(3)+(4)
    #-------------------------------------------
      
    for (i,j) in self.adj.edges():
      m.constrain(2*E[i,j] <= X[i]+X[j] ) # dont understand
      
    print "Setting up Equations.....3 4"
    #*********************************************
    
    #----------------------------------------
    #                equation-(5)
    #-------------------------------------------
    for i in xrange(n):
      m.constrain( 0<= Y[i] <= X[i] )
    print "Setting up Equations.....5"
    #*********************************************
    
    
    #----------------------------------------
    #                equation-(6)-7-8
    #-------------------------------------------
    for (i,j) in self.adj.edges():
      m.constrain( 0 <= B[i,j] <= E[i,j] )
      m.constrain( E[i,j] ==  E[j,i] )
      m.constrain( B[i,j] ==  B[j,i] )
      m.constrain(2*B[i,j] <= Y[i]+Y[j] )
      if self.adj[i][j]['con_type'] !='short': 
        m.constrain(B[i,j]==0)
    print "Setting up Equations.....6-9"
    

    #*********************************************
    
    #----------------------------------------
    #                equation-(10)
    #-------------------------------------------
    for i in self.sinks:
      m.constrain( X[i] == 1)
      m.constrain( Y[i] == 1)
    print "Setting up Equations....10."
    #*********************************************
    
    
    #----------------------------------------
    #                equation-(11 or 12)
    #-------------------------------------------
    
    targets = self.T_N.keys()
    e_t = time.clock()
    count=0
    for t in targets:
      t_n = np.zeros(n,dtype = int)
      list = self.T_N[t]
      if (len(list) == 0):
        print "target not covered"
        continue
      lhs = Y[list[0]]
      for i in list[1:]: 
        lhs += Y[i]
      e_t = time.clock()  
      m.constrain(lhs >= 1)
      count+=1
      if (count%100 ==0):
        print "100 equation generation:",(time.clock() - e_t)*1000
        e_t = time.clock()
    print "Setting up Equations.....11 12"
    
    
    
    
    #*********************************************

    #----------------------------------------
    #                equation-(13)
    #-------------------------------------------
    for i in xrange(n):
      for j in self.adj[i]:
        m.constrain( 0<= F[i,j] <= B[i,j] )
    print "Setting up Equations.....13"
    #*********************************************

    #----------------------------------------
    #                equation-(14) and (15)
    #-------------------------------------------
    
    for i in xrange(n):
      if i in self.sinks or i in self.disconnected_nodes:
          m.constrain( F_S[i] == 0 )
      else:
          m.constrain( F_S[i] == Y[i]/N )
    print "Setting up Equations.....14 15"
    #*********************************************
    
    #----------------------------------------
    #                equation-(16) and (17)
    #-------------------------------------------
    for i in xrange(n):
      if i in self.sinks:
          m.constrain( 0<= F_T[i] <= 1)
      else:
          m.constrain( F_T[i] == 0 )
    print "Setting up Equations.....16 17"
    #*********************************************
    
    #----------------------------------------
    #                equation-(18)
    #-------------------------------------------
    # 
    for j in xrange(n):
      lhs_sum_j = F_S[j]
      rhs_sum_j = F_T[j]
      for i in self.adj[j]:
        lhs_sum_j += F[i,j]
        rhs_sum_j += F[j,i]
      m.constrain(lhs_sum_j == rhs_sum_j)
    print "Setting up Equations.....18"
    #*********************************************
    
    #----------------------------------------
    #                equation-(19)
    #-------------------------------------------
    m.constrain( F_S.sum() == F_T.sum() )
    print "Setting up Equations.....19"
    #*********************************************
    
    #----------------------------------------
    #                equation-(20)
    #-------------------------------------------
    sink_count = len(self.sinks)
    m.constrain(X.sum() - sink_count <= self.n_max)
    print "Setting up Equations.....20"
    #*********************************************
    
    #----------------------------------------
    #                equation-(21)
    #-------------------------------------------
    # stupid trick to use b00
    for i in xrange(n):
      lhs = B[0][0]
      for j in self.adj[i]:
        lhs += B[i, j]
      m.constrain(lhs <= self.d_max + B[0][0])
    print "Setting up Equations.....21"
    #*********************************************
    
    #----------------------------------------
    #                equation-(22)
    #-------------------------------------------
    for (i,j) in self.adj.edges():
      m.constrain( 0<= G[i,j] <= E[i,j] )
    print "Setting up Equations.....22"
    #*********************************************

    #----------------------------------------
    #                equation-(23) and (24)
    #-------------------------------------------
    for i in xrange(n):
      if i in self.sinks:
        m.constrain( G_S[i] == 0 )
      else:
        m.constrain( 0<=G_S[i] <= X[i]*self.adj.degree(i))
    print "Setting up Equations.....23 24"
    #*********************************************
    
    #----------------------------------------
    #                equation-(25) and (26)
    #-------------------------------------------
    for i in xrange(n):
      if i in self.sinks:
        m.constrain( 0 <= G_T[i] <= self.adj.degree(i))
      else:
        m.constrain( G_T[i] == 0 )
    print "Setting up Equations.....25 26"
    #*********************************************
    
    #----------------------------------------
    #                equation-(27)
    #-------------------------------------------
    for j in xrange(n):
      lhs_sum_j = G_S[j]
      rhs_sum_j = G_T[j]
      for i in self.adj[j]:
        lhs_sum_j += G[i,j]
        rhs_sum_j += G[j,i]
      m.constrain( lhs_sum_j == rhs_sum_j)
    print "Setting up Equations.....27"
    #*********************************************
    
    #----------------------------------------
    #                equation-(28)
    #-------------------------------------------
    m.constrain( G_S.sum() == G_T.sum() )
    #*********************************************
    
    #----------------------------------------
    #              ----OBJECTIVE-----
    #-------------------------------------------
    print "Starting CEPLEX....."
    m.maximize(G_S.sum())
    
    #----------------------------------------
    #              ----RESULT-----
    #-------------------------------------------
    print "Finished CEPLEX Optimization....."
    temp = m[G_S.sum()]
    self.max_flow = temp[0,0]
    print temp
    print self.max_flow
    
    print "max_flow:",self.max_flow
    #t_input = raw_input("press enter:")
    #print "Max Flow:X",m[X]
    #print "Max Flow:Y",m[Y]
   
    
    





    