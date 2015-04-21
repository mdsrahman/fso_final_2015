
import wrapper_heuristic_placement_algo as whpa
#import relaxed_ilp_solver_for_placement_algo as rilp
import generate_sample
#import relaxed_ilp_modified as rilp_m
import random
import cPickle as pkl
import csv
import numpy as np

def create_dynamic_graph_spec(filename, g, sources, sinks, fso_per_node, capacity_gbps):
  f=open(filename,"w")
  #-------trafficSources-------:
  f.write("trafficSources:\n")
  for n in g.nodes():
    f.write(str(n)+"\n")
  f.write('\n')
  
  
  #---FSONodes:
  f.write("FSONodes:\n")
  nodes = g.nodes() 
  for n in nodes:
    for fso in range(1, fso_per_node+1):
      f.write(str(n)+"_fso"+str(fso)+"\n")
  f.write('\n')   
  
  #---FSOLinks:---
  f.write("FSOLinks:\n")   
  edges = g.edges()
  for u,v in edges:
    for fso1 in range(1, fso_per_node+1):
      for fso2 in range(1, fso_per_node+1):  
        #"0_0_fso2To2_0_fso1 10Gbps"
        f_text = str(u)+"_fso"+str(fso1)+"To"\
                +str(v)+"_fso"+str(fso2)+" "+str(capacity_gbps)+"Gbps\n" 
        f.write(f_text)
        f_text = str(v)+"_fso"+str(fso2)+"To"\
                +str(u)+"_fso"+str(fso1)+" "+str(capacity_gbps)+"Gbps\n" 
        f.write(f_text)
  f.write('\n')   
  #------gateways--:
  f.write('gateways:\n')
  for n in sinks:
    f.write(str(n)+"\n")
  #f.write('\n')
  
  f.close()
  return 

def save_graph_edges( g, filepath):
  with open(filepath,"w") as f:
    for u,v in g.edges():
      f.write(str(u)+","+str(v)+"\n")
  return

def save_graph_data(configpath, adj, T, T_N, sinks, node, tnode):
  pkl_data={}
  pkl_data['adj'] = adj
  pkl_data['T']= T
  pkl_data['T_N']=T_N
  pkl_data['sinks'] = sinks
  pkl_data['node'] =node 
  pkl_data['tnode'] = tnode
  pkl.dump(obj = pkl_data, file = open(configpath,'wb'))
  return


def load_graph_data(configpath):
  pkl_data = pkl.load( open(configpath, "rb" ) )
  return pkl_data['adj'], pkl_data['T'], pkl_data['T_N'],\
         pkl_data['sinks'], pkl_data['node'], pkl_data['tnode']

if __name__ == '__main__':
  #*************************************
  #                  params            
  #*************************************
  seed = 3194576
  start = 1
  #seed = 5194574
  #start = 6
  #seed = 9457613
  #start = 11
  #seed = 2075432
  #start = 16
  #seed = 3457343
  #start = 21
  #seed = 89852133
  #start = 26
  #seed = 9813235
  #start = 31
  #seed = 126524
  #start = 36
  #seed = 5645343
  #start = 41
  #seed = 1114367
  #start = 46


  sample_count = 1
  
  random.seed(seed)
  

  stat_filepath = './stat/synthetic_graph_stat.txt'
  dynamic_graph_for_TN_spec_folder = './spec/'
  output_folder = './output/'
  target_spacing = 10
  sink_ratio = 0.01
  capacity = 1000.0
  fso_per_node = 4 
  run_ilp = True #<----------ILP Deactivated
   
  
  #-------------graph--spec--------------------------
  max_x = 1000 
  max_y =  500
  total_nodes =  500
  max_edges =  100000
  short_edges_per_node =  150
  long_edges_per_node = 50
  min_fso_distance = max_short_edge_dist = 100
  max_long_edge_dist = 1000
  #--------------------------------------------
  
  #*************************************
  #                  end of params            
  #*************************************
  
  
  
  stat_headers = [
           'sample_no', 
           'sample_node_count', 
           'sampe_edge_count', 
           'dynamic_max_flow', 
           'ilp_max_flow',
           'static_max_flow',
           'avg_static_max_flow',
           'static_upperbound_flow',
           'step_1_node_count',
           'step_2_node_count',
           'step_3_node_count',
           'step_4_node_count',
           'static_min_degree',
           'static_max_degree',
           'static_avg_degree',
           'step_3_max_degree',
           'total_targets',
           'covered_targets',
           'disconnected_covering_nodes',
           'static_graph_degree_for_dynamic_equivalence'
          ]
           
  
  f= open(stat_filepath, 'w')
  writer = csv.DictWriter(f, stat_headers)
  writer.writeheader()
  f.close()
  
  for i in xrange(start,start+sample_count):
    f= open(stat_filepath, 'a')
    stat_row = {}
    configname = str(i)
    
    gs = generate_sample.Generate_Graph_Sample(
               max_x, 
               max_y, 
               total_nodes, 
               max_edges,
               short_edges_per_node, 
               long_edges_per_node,
               max_short_edge_dist,
               max_long_edge_dist)
    
    adj = gs.get_adj_graph()
    node_x = list(gs.node_x)
    node_y = list(gs.node_y)
    
    #*************************************
    #     heuristic solver           
    #************************************* 
    print"Running Heurisitc Placement Algo....for sample:",i
    w = whpa.generate_heuristic_placement_algo_instance(
                                           adj = adj,
                                           node_x =  node_x,
                                           node_y = node_y,
                                           target_spacing = target_spacing, 
                                           min_fso_distance = min_fso_distance,
                                           sink_ratio = sink_ratio,
                                           static_d_max = fso_per_node,
                                           gen_tn = run_ilp)         
    hp = w.get_hpa_instance()
    
    hp.solve()
    print "Max Dynamic Flow:--------------:",hp.max_flow
    print "Max Static Flow:---------------:",hp.static_max_flow 
    print "Number of Edges,nodes Dynamic:---------",hp.g1.number_of_edges(),hp.g1.number_of_nodes()
    print "Number of Edges,nodes Static------------",hp.static.number_of_edges(),hp.static.number_of_nodes()
    #print "Number of nodes after step 1:",
    #*************************************
    #    relaxed ILP solver          
    #*************************************
    ilp_max_flow = 0.0
    
    if run_ilp:
      import relaxed_ilp_modified as rilp_m
      print "Running Relaxed ILP....n_max:",hp.n_max
      ilp = rilp_m.ILP_Relaxed(nmax = hp.n_max,
                              dmax = 4,
                              adj = hp.adj,
                              T_N = w.T_N, 
                              sinks = hp.sinks,
                              disconnected_nodes = hp.disconnected_covering_nodes)
      ilp.solve()
      ilp_max_flow = float(ilp.max_flow)

    #*************************************
    #    stat collection         
    #************************************* 
    static_graph_degree_list = (hp.static.degree()).values()
    backbone_graph_degree_list = (hp.G_p.degree()).values()
    
    static_graph_min_degree = min(static_graph_degree_list)
    static_graph_max_degree = max(static_graph_degree_list)
    static_graph_avg_degree = np.mean(static_graph_degree_list)
    
    backbone_graph_min_degree = min(backbone_graph_degree_list)
    
    disconencted_covering_nodes = len(hp.disconnected_covering_nodes)
                                      
    stat_row['sample_no'] = i
    stat_row['sample_node_count'] = hp.adj.number_of_nodes()
    stat_row['sampe_edge_count'] = hp.adj.number_of_edges()
    stat_row['dynamic_max_flow'] = hp.max_flow
    stat_row['ilp_max_flow'] = ilp_max_flow
    stat_row['static_max_flow'] = hp.static_max_flow
    stat_row['avg_static_max_flow'] = hp.avg_max_flow_val
    stat_row['static_upperbound_flow'] = hp.static_upper_bound_flow
    stat_row['step_1_node_count'] = len(hp.N)
    stat_row['step_2_node_count'] = hp.bg.number_of_nodes()
    stat_row['step_3_node_count'] = hp.G_p.number_of_nodes()
    stat_row['step_4_node_count'] = hp.g1.number_of_nodes()
    stat_row['static_min_degree'] = static_graph_min_degree
    stat_row['static_max_degree'] = static_graph_max_degree
    stat_row['static_avg_degree'] = static_graph_avg_degree 
    stat_row['step_3_max_degree'] = backbone_graph_min_degree
    stat_row['total_targets'] = w.total_targets
    stat_row['covered_targets'] = w.targets_covered
    stat_row['disconnected_covering_nodes'] = disconencted_covering_nodes 

    
    f= open(stat_filepath, 'a')
    writer = csv.DictWriter(f, stat_headers)
    writer.writerow(stat_row)
    f.close()
    
    print "\t\twriting dynamic graph spec to file..."
    save_graph_edges(g = hp.adj, filepath = output_folder+str(configname)+'.adj.txt' )
    save_graph_edges(g = hp.G_p, filepath = output_folder+str(configname)+'.bg.txt' )
    save_graph_edges(g = hp.static, filepath = output_folder+str(configname)+'.static.txt' )
    save_graph_edges(g = hp.g1, filepath = output_folder+str(configname)+'.dynamic.txt' )
    
    create_dynamic_graph_spec(filename = dynamic_graph_for_TN_spec_folder+str(configname)+'.txt', 
                              g = hp.g1, 
                              sources = list(hp.g1.nodes()), 
                              sinks = hp.sinks, 
                              fso_per_node = fso_per_node, 
                              capacity_gbps = 10) 
    
    
  
  
  
  
  
   
    
    
    
    