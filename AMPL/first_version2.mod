param n integer > 0;

set V := 1..n;
param E_single {(i,j) in (V cross V)} binary; # (origin, destination)
param E {(i,j) in (V cross V)} binary; # (origin, destination)

var x {(i,j) in (V cross V)} binary;

var out_deg{i in V} = sum{j in V} x[i,j];
var in_deg{i in V}  = sum{j in V} x[j,i];

#maximize take_all: sum{(i,j) in (V cross V)} x[i,j];
#maximize all_out: sum{i in V} out_deg[i];
maximize multiplying_neg: sum{i in V} (-out_deg[i]) *(-in_deg[i]); 

subject to original_graph{(i,j) in (V cross V)}: x[i,j] <= E[i,j];
subject to no_double_sided{(i,j) in (V cross V): i < j}: x[i,j]+x[j,i] <= 1;
subject to force_single {(i,j) in (V cross V)}: x[i,j] >= E_single[i,j];


data "C:\Users\zador\Documents\!!! UNIVERSITY\TFG\4node_v0.dat";


option solver cplex;
solve;
display x;
display out_deg;
display _solve_user_time;

end;