#####################
## Parameters
#####################
set V;
set E;

set X{E} within V; # The tail set for each hyperedge
set Y{E} within V; # The head set for each hyperedge

#####################
## Variables
#####################

var inverted{E} binary; # 1 iff edge is inverted (Head and Tail)  
var is_internal{V} binary; # to maximize


#####################
## Rules
#####################

maximize obj: sum {j in V} is_internal[j];

subject to outgoing_half_implies_internal {j in V}: 
	sum {i in E: j in X[i]} (1-inverted[i]) + 
	sum {i in E: j in Y[i]} inverted[i]
	>= is_internal[j]; 
    # will only allow is_internal to be one if there's an outgoing edge. 

subject to incoming_half_implies_internal {j in V}:
	sum {i in E: j in Y[i]} (1-inverted[i]) +
	sum {i in E: j in X[i]} inverted[i]
	>= is_internal[j]; 
    # will only allow is_internal to be one if there's an incoming edge.
