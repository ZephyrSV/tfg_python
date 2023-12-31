reset;
#####################
## Parameters
#####################

set V; # nodes
set E; # hyperedges

set X{E}; # for each hyperedge, its tail set
set Y{E}; # for each hyperedge, its head set

set uninvertibles within E; # set of edges that cannot be inverted
set forced_externals within V; # set of nodes that must be sinks
set forced_internals within V; # set of nodes that must be sources

set substrate_in{i in V} := {j in E: i in X[j]}; 
set product_in{i in V} := {j in E: i in Y[j]};

#####################
## Variables
#####################
var inverted {E} binary; #determines whether an edge is inverted

var has_incoming{V} binary;
var has_outgoing{V} binary;
var is_internal{V} binary;

#####################
## Rules
#####################

maximize internal: sum{i in V} is_internal[i];

subject to not_substrate_at_all{i in V}:
		has_outgoing[i] <=
			sum{j in substrate_in[i]} (1-inverted[j]) +  
			sum{j in product_in[i]} inverted[j];
			
subject to not_product_at_all{i in V}:
		has_incoming[i] <=
			sum{j in product_in[i]} (1-inverted[j]) + 
			sum{j in substrate_in[i]} inverted[j];

subject to is_internal_1 {i in V}:
        is_internal[i] * 2  <= has_incoming[i] + has_outgoing[i];