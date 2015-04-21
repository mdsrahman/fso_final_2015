
import csv

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

with open('./stat/synthetic_graph_stat.txt') as csvfile:
  reader = csv.DictReader(csvfile, fieldsname = stat_headers)
  for row in reader:
    print row['ilp_max_flow'], \
    row['dynamic_max_flow'], \
    row['static_max_flow'],\
    row['covered_targets']
    
    
    