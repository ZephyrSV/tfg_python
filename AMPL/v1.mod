# Trying to adapt v0.mod to hypergraphs
reset;
#####################
## Parameters
#####################
param n integer > 0; # number of nodes
param m integer > 0; # number of edges 

set V := 1..n;
set E := 1..m;

param invertible{E} binary; # determines whether an edge is invertible
set substrate_in{V}; 
set product_in{V};

#####################
## Variables
#####################
var x {i in E} binary; #determines whether an edge is inverted

var has_out{i in V} binary;
var has_in{i in V} binary;

#####################
## Rules
#####################
maximize multiplying_in_out: sum{i in V} has_in[i] * has_out[i];

subject to respect_invertability {i in E}:
		x[i] <= invertible[i];

subject to substrates_not_inverted{i in V, j in substrate_in[i]}:
		has_in[i] >= 1-x[j];
		
subject to substrates_inverted{i in V, j in product_in[i]}:
		has_in[i] >= x[j];

subject to products_not_inverted{i in V, j in product_in[i]}:
		has_out[i] >= 1-x[j];
		
subject to products_inverted{i in V, j in substrate_in[i]}:
		has_out[i] >= x[j];
 
subject to not_substrate_at_all{i in V}:
		has_in[i] <= 
			sum{j in substrate_in[i]} (1-x[j]) +  
			sum{j in product_in[i]} x[j];
			
subject to not_product_at_all{i in V}:
		has_out[i] <=
			sum{j in product_in[i]} (1-x[j]) + 
			sum{j in substrate_in[i]} x[j];




###############################3
data;

param n := 7;
param m := 4;

set substrate_in[1] := 1;
set substrate_in[2] := 2;
set substrate_in[3] := 2;
set substrate_in[4] := 3;
set substrate_in[5] := 3 4;
set substrate_in[6] := ;
set substrate_in[7] := ;

set product_in[1] := ;
set product_in[2] := 1; 
set product_in[3] := 1;
set product_in[4] := 2;
set product_in[5] := ;
set product_in[6] := 3;
set product_in[7] := 3 4;

param invertible :=
1 1
2 0
3 0
4 1;


option solver cplex;
solve;
display x;
display has_in;
display has_out;
display _solve_user_time;
reset;
end;