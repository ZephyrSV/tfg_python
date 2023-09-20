#####################
## Parameters
#####################
set V;
set E;

set X{E};
set Y{E};

param invertible{E} binary; # determines whether an edge is invertible
set substrate_in{i in V} := {j in E: i in X[j]}; 
set product_in{i in V} := {j in E: i in Y[j]};

#####################
## Variables
#####################
var inverted {E} binary; #determines whether an edge is inverted

var has_out{V} binary;
var has_in{V} binary;

var is_internal{V} binary;

#####################
## Rules
#####################
maximize internal_nodes: sum{i in V} is_internal[i];
#maximize multiplying_in_out: sum{i in V} has_in[i] * has_out[i];

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

s.t. compute_is_internal{i in V}:
		is_internal[i] <= has_in[i] + has_out[i] - 1;


###############################3
data "ex1_v1.dat";

reset;
end;