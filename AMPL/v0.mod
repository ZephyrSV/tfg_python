############################################################################
## Author - Zephyr Serret Verbist - zserret@me.com
##
## Given a undirected or partially undirected graph, this model's purpose 
## is to chose an orientation for each edge such that we maximize the amount 
## off internal edges (edges with non-zero out-degree and non-zero in-degree).
############################################################################# 
reset;
## param n is the amount of vertices 
param n integer > 0;

set V := 1..n;
param E {V cross V} binary; # Input edge matrix (origin, destination)
param E_single {V cross V} binary; # only the input edge matrix of directed edges


var x {V cross V} binary; # Resulting edge matrix (origin, destination)

var has_out{V} binary; # 1 if x[i] has at least one outgoing edge, 0 otherwise
var has_in{V}  binary; # 1 if x[i] has at least one incoming edge, 0 otherwise

# The only problem I have is here... I need an "and" operation... I currently multiply. 
maximize multiplying_in_out: sum{i in V} has_in[i] * has_out[i]; 

subject to original_graph{(i,j) in (V cross V)}: 
		x[i,j] <= E[i,j];
		# Prohibits the selection of edges that weren't present in the original graph
		
subject to no_double_sided{(i,j) in (V cross V): i < j}: 
		x[i,j]+x[j,i] <= 1;
		# Forces us to orient the double-sided edges.
		
subject to force_single {(i,j) in (V cross V)}: 
		x[i,j] >= E_single[i,j];
		# Forces to choose the edges that are already one-sided
		# (not exactly necessary)
		
subject to has_out_bigger_than_x{(i,j) in (V cross V)}: 
		has_out[i] >= x[i,j];
		# Forces has_out to be 1 if there's an outgoing edge
		
subject to has_in_bigger_than_x{(i,j) in (V cross V)}:
		has_in[j]  >= x[i,j]; 
		# Forces has_in to be 1 if there's an incoming edge
		
subject to has_out_smaller_than_sum_x{i in V}:
		has_out[i] <= sum{j in V} x[i,j];
		# Forces has_out to be 0 if there's no outgoing edge
		
subject to has_in_smaller_than_sum_x{j in V}:
		has_out[j] <= sum{i in V} x[i,j];
		# Forces has_in to be 0 if there's no incoming edge

##################################################################################
##################################################################################

data "C:\Users\zador\Documents\GitHub\tfg_python\AMPL\7node_v0_2.dat";


option solver cplex;
solve;
display x;
display has_in;
display has_out;
display _solve_user_time;
reset;
end;