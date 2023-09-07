# Trying to adapt v0.mod to hypergraphs

#####################
## Parameters
#####################
param n integer > 0; # number of nodes
param m integer > 0; # number of edges 

set V := 1..n;
set E := 1..m;

param invertible{i in E} binary; # determines whether an edge is invertible
set substrates within V cross E;
set products within V cross E;

#####################
## Helper Parameters
#####################
param substrate_in{i in V} := 

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

subject to substrates_not_inverted{(i,j) in substrates}:
		has_in[i] >= 1-x[j];
		
subject to substrates_inverted{(i,j) in products}:
		has_in[i] >= x[j];

subject to products_not_inverted{(i,j) in products}:
		has_out[i] >= 1-x[j];
		
subject to products_inverted{(i,j) in substrates}:
		has_out[i] >= x[j];
		
subject to not_substrate_at_all{i1 in V}:
		has_in[i1] <= 
			(sum{(i2,j2) in substrates: i2 == i1} 1-x[j2]) + 
			(sum{(i3,j3) in products: i3 == i1} x[j3]);
			
subject to not_product_at_all{i in V}:
		has_out[i] <=
			(sum{(i2,j) in products[i]: i2 == i} 1-x[j]) + 
			(sum{(i2,j) in substrates[i]: i2 == i} x[j]);




###############################3
data;

param n := 7;
param m := 4;

set substrates :=
(1,*) 1
(2,*) 2
(3,*) 2
(4,*) 3
(5,*) 3 4
#(6,*)  
#(7,*) 
;

set products := 
#(1,*) 
(2,*) 1
(3,*) 1
(4,*) 2
#(5,*) 
(6,*) 3
(7,*) 3 4
;

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