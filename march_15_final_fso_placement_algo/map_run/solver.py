#import map_to_graph 

import wrapper_heuristic_placement_algo as whpa
import relaxed_ilp_modified as rilp
import numpy as np
import csv
import random




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


if __name__ == '__main__':
  #*************************************
  #                  params            
  #*************************************
  seed = 101973
  ilp_max_nodes = 200 #<---
  ilp_max_edges = 400 #<---
  
  
  
  target_spacing = 10
  min_fso_distance = 200
  sink_ratio = 0.02
  capacity = 1000.0
  fso_per_node = 4 
  run_ilp = True
  
  stat_filepath = './stat/frag_city_stat.txt'
  output_folder = './graph/'
  mapfiles = ['seattle']
  
  #dyn_spec_filepath = './dyn_spec/'
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
  random.seed(seed)
  
  for mfile in mapfiles:
    configname = mfile
    w = whpa.generate_heuristic_placement_algo_instance(
                                          node_file_name = mfile+".node.pkl", 
                                          edge_file_name = mfile+".edge.txt",
                                           target_spacing = target_spacing, 
                                           min_fso_distance = min_fso_distance,
                                           sink_ratio = sink_ratio,
                                           static_d_max = fso_per_node,
                                           gen_tn = run_ilp)         
    hp = w.get_hpa_instance()
    #-----------------------------------------------------------------------
    #*************************************
    #     heuristic solver           
    #************************************* 
    print"Running Heurisitc Placement Algo...."
    hp.solve()
    
    dynamic_nodes = hp.g1.number_of_nodes()
    dynamic_edges = hp.g1.number_of_edges()
    static_nodes = hp.static.number_of_nodes()
    static_edges = hp.static.number_of_edges()
    
    print "\t Static nodes:", static_nodes, " Static edges:",static_edges
    print "\t Dynamic nodes:", dynamic_nodes, " Dynamic edges:",dynamic_edges
    #*************************************
    #    relaxed ILP solver          
    #*************************************
    ilp_max_flow = 0.0

    print "Running Relaxed ILP...."
    ilp = rilp.ILP_Relaxed(nmax = hp.n_max,
                            dmax = hp.d_max,
                            adj = hp.adj,
                            T_N =  w.T_N, 
                            sinks = hp.sinks,
                            disconnected_nodes = hp.disconnected_covering_nodes)
    ilp.solve()
    ilp_max_flow = ilp.max_flow
    #*************************************
    #    stat WITH ilp         
    #************************************* 
    #print ilp.max_flow
    if ilp_max_flow >0.0:
      d_i_ratio = 100.0*hp.max_flow/ilp_max_flow
    else:
      d_i_ratio = 0.0
      
    if hp.max_flow >0.0:
      s_d_ratio = 100.0*hp.static_max_flow/hp.max_flow
    else:
      s_d_ratio = 0.0
    #d_f_ratio = 100.0*hp.max_flow/hp.full_adj_max_flow
            
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
    stat_row={} 
    stat_row['sample_no'] = mfile
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

    
    #-------------------------------------------------------------------------
    
    f= open(stat_filepath, 'a')
    writer = csv.DictWriter(f, stat_headers)
    writer.writerow(stat_row)
    f.close()
    
    print "\t\twriting dynamic graph spec to file..."

    create_dynamic_graph_spec(filename = './spec/'+str(configname)+'.txt', 
                              g = hp.g1, 
                              sources = list(hp.g1.nodes()), 
                              sinks = hp.sinks, 
                              fso_per_node = fso_per_node, 
                              capacity_gbps = 10) 
  f.close()
  print "*****************solved for map:",configname
  print "\t\twriting dynamic graph spec to file..."
  save_graph_edges(g = hp.adj, filepath = output_folder+str(configname)+'.adj.txt' )
  save_graph_edges(g = hp.G_p, filepath = output_folder+str(configname)+'.bg.txt' )
  save_graph_edges(g = hp.static, filepath = output_folder+str(configname)+'.static.txt' )
  save_graph_edges(g = hp.g1, filepath = output_folder+str(configname)+'.dynamic.txt' )


  
   
    
    
    
    