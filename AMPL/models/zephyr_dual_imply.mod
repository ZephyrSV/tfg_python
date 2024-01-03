reset;

#####################
## Parameters
#####################
set V;
set E;

param M = card(E);

set X {i in E} within V; # Tail set
set Y {i in E} within V; # Head set

set uninvertibles within E; # set of edges that cannot be inverted
set forced_internals within V; # set of nodes that must be sinks
set forced_externals within V; # set of nodes that must be sources

#####################
## Variables
#####################
var inverted {i in E} binary; # from X[i] to Y[i]
var has_outgoing {j in V} binary;
var has_incoming {j in V} binary;
var is_internal {V} binary;

#####################
## Rules
#####################
maximize internal: sum {j in V} is_internal[j];

subject to incoming_implies_has_incoming {j in V}:
        sum {i in E: j in X[i]} (1-inverted[i]) + 
        sum {i in E: j in Y[i]} inverted[i] 
        >= has_outgoing[j];

subject to has_incoming_implies_incoming {j in V}:
        sum {i in E: j in X[i]} (1-inverted[i]) + 
        sum {i in E: j in Y[i]} inverted[i] 
        <= M * has_outgoing[j];

subject to outgoing_implies_has_outgoing {j in V}:
        sum {i in E: j in X[i]} inverted[i] + 
        sum {i in E: j in Y[i]} (1-inverted[i]) 
        >= has_incoming[j];

subject to has_outgoing_implies_outgoing {j in V}:
        sum {i in E: j in X[i]} inverted[i] + 
        sum {i in E: j in Y[i]} (1-inverted[i])  
        <= M * has_incoming[j];

s.t. compute_is_internal{i in V}:
		is_internal[i] * 2 <= has_outgoing[i] + has_incoming[i];