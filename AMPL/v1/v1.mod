# Trying to adapt v0.mod to hypergraphs
reset;
#####################
## Parameters
#####################
param n integer > 0; # number of nodes
param m integer > 0; # number of edges 

set V := 1..n;
set E := 1..m;

set X{E};
set Y{E};

param invertible{E} binary; # determines whether an edge is invertible
set substrate_in{i in V} := {j in E: i in X[j]}; 
set product_in{i in V} := {j in E: i in Y[j]};

#####################
## Variables
#####################
var inverted {i in E} binary; #determines whether an edge is inverted

var has_out{i in V} binary;
var has_in{i in V} binary;

#####################
## Rules
#####################
maximize multiplying_in_out: sum{i in V} has_in[i] * has_out[i];

subject to respect_invertability {i in E}:
		inverted[i] <= invertible[i];

subject to substrates_not_inverted{i in V, j in substrate_in[i]}:
		has_in[i] >= 1-inverted[j];
		
subject to substrates_inverted{i in V, j in product_in[i]}:
		has_in[i] >= inverted[j];

subject to products_not_inverted{i in V, j in product_in[i]}:
		has_out[i] >= 1-inverted[j];
		
subject to products_inverted{i in V, j in substrate_in[i]}:
		has_out[i] >= inverted[j];
 
subject to not_substrate_at_all{i in V}:
		has_in[i] <= 
			sum{j in substrate_in[i]} (1-inverted[j]) +  
			sum{j in product_in[i]} inverted[j];
			
subject to not_product_at_all{i in V}:
		has_out[i] <=
			sum{j in product_in[i]} (1-inverted[j]) + 
			sum{j in substrate_in[i]} inverted[j];




###############################3
data "ex1_v1.dat";

reset;
end;