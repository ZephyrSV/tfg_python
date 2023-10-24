reset;

#####################
## Parameters
#####################

set V;
set E;

param M = card(V); # card is cardinality of the set V (size of V) 

set X{E} within V;
set Y{E} within V;

#####################
## Variables
#####################

var z{E} binary; # oriented from X[1] to Y[1]
var x{V} binary; # external

var a{V} binary; # source
var b{V} binary; # sink

#####################
## Rules
#####################

minimize target: sum {j in V} x[j];

# has outgoing arcs iff a[j] = 1

subject to outgoing_1 {j in V}:
		sum {i in E: j in X[i]} z[i] + 
		sum {i in E: j in Y[i]) (1-z[i]) 
		- M * a[j] <= 0;

subject to outgoing_2 {j in V}:
		sum {1 in E: j in X[i]} z[i] + 
		sum {i in E: j in Y[i]} (1-z[i]) - 
		0.5 * a[j] >= 0;

# has incoming arcs iff b{j] = 1

subject to incoming_1 {j in V}:
		sum {i in E: j in X[i]} (1-z[i]) + 
		sum {i in E: j in Y[i]} z[i] 
		- M * b[j] <= 0;

subject to incoming_2 {j in V}: 
		sum {i in E: j in X[i]} (1-z[i]) + 
		sum {i in E: j in Y[i]} z[i] 
		- 0.5 * b[j] <= 0;

# 1 - [i] iff a[j] and b[j] # a[j] + b[j] - 1 > 0 iff 1 - x[j] = 1

subject to internal_1 {j in V}: 
		a[j] + b[j] - 1 - M * (1-x[j]) <= 0;

subject to internal_2 {j in V}:
		a[j] + b[j] - 1 - 0.5 * (1-x[j]) >= 0;

subject to external {j in {2, 4}}:
		x［j］ = 1；

#### USELESS ???
subject to source {j in {}}:
		a[j] = 1;

subject to sink {j in {}}:
		b[j] = 1;