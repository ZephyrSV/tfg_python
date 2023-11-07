reset;
#####################
## Parameters
#####################

set V; # nodes
set E; # hyperedges

set X{E}; # for each hyperedge, its tail set
set Y{E}; # for each hyperedge, its head set

set uninvertible within E; # set of edges that cannot be inverted
set forced_sinks within V; # set of nodes that must be sinks
set forced_sources within V; # set of nodes that must be sources

set substrate_in{i in V} := {j in E: i in X[j]}; 
set product_in{i in V} := {j in E: i in Y[j]};

#####################
## Variables
#####################
var inverted {E} binary; #determines whether an edge is inverted

var sink{V} binary;
var source{V} binary;

var is_internal{V} binary;

#####################
## Rules
#####################

maximize obj: sum{i in V} is_internal[i];


subject to substrates_not_inverted{i in V, j in substrate_in[i]}:
		source[i] >= 1-inverted[j];
		
subject to substrates_inverted{i in V, j in product_in[i]}:
		source[i] >= inverted[j];

subject to products_not_inverted{i in V, j in product_in[i]}:
		sink[i] >= 1-inverted[j];
		
subject to products_inverted{i in V, j in substrate_in[i]}:
		sink[i] >= inverted[j];
 
subject to not_substrate_at_all{i in V}:
		source[i] <= 
			sum{j in substrate_in[i]} (1-inverted[j]) +  
			sum{j in product_in[i]} inverted[j];
			
subject to not_product_at_all{i in V}:
		sink[i] <=
			sum{j in product_in[i]} (1-inverted[j]) + 
			sum{j in substrate_in[i]} inverted[j];

s.t. compute_is_internal{i in V}:
		is_internal[i] <= source[i] + sink[i] - 1;


