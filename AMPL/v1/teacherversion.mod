reset;

#####################
## Parameters
#####################
set V;
set E;

set X{E} within V; # The tail set for each hyperedge
set Y{E} within V; # The head set for each hyperedge
param invertible{E} binary; # determines whether an edge is invertible

#####################
## Variables
#####################

var inverted{E} binary; # 1 iff edge is inverted (Head and Tail)  
var is_internal{V} binary; # to maximize


#####################
## Rules
#####################

maximize obj: sum {j in V} is_internal[j];

subject to outgoing_half_implies_internal {j in V}: # for each node 'j'
		sum {i in E: j in X[i]} (1-inverted[i]) + 	# for every hyperedge 'i', sum 1 iff 'j' belongs to its *tail* set and is *not* inverted
		sum {i in E: j in Y[i]} inverted[i] 		# for every hyperedge 'i', sum 1 iff 'j' belongs to its *head* set and is *inverted*
		>= is_internal[j]; # will only allow is_internal to be one iff there's an outgoing edge. 

subject to incoming_half_implies_internal {j in V}: # for each node 'j'
		sum {i in E: j in Y[i]} (1-inverted[i]) +	# for every hyperedge 'i', sum 1 iff 'j' belongs to its *head* set and is *not* inverted
		sum {i in E: j in X[i]} inverted[i] 		# for every hyperedge 'i', sum 1 iff 'j' belongs to its *tail* set and is *inverted*
		>= is_internal[j]; # will only allow is_internal to be one iff there's an incoming edge.

subject to respect_invertibility {i in E}:
		inverted[i] <= invertible[i];
