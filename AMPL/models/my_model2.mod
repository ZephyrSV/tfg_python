reset;
#####################
## Parameters
#####################

set V; # nodes
set E; # hyperedges

set X{E}; # for each hyperedge, its tail set
set Y{E}; # for each hyperedge, its head set

param invertible{E} binary; # determines whether an edge is invertible
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

#####################
## Rules
#####################

maximize obj: sum{i in V} (source[i] * sink[i]);

subject to not_substrate_at_all{i in V}:
		source[i] <=
			sum{j in substrate_in[i]} (1-inverted[j]) +  
			sum{j in product_in[i]} inverted[j];
			
subject to not_product_at_all{i in V}:
		sink[i] <=
			sum{j in product_in[i]} (1-inverted[j]) + 
			sum{j in substrate_in[i]} inverted[j];