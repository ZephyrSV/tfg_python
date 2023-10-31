reset;
set V;
set E;

param M = card(V);

set X {E} within V;
set Y {E} within V;

param invertible{E} binary; # determines whether an edge is invertible


var inverted {E} binary;
var source {V} binary;
var sink {V} binary;
var is_internal{V} binary;

maximize obj: sum {j in V} is_internal[j];

#############

s.t. outgoing_1{j in V}: #for every vertex
	sum{i in E: j in Y[i]} inverted[i] 	+
	sum{i in E: j in X[i]} (1-inverted[i]) #how many times it appears as substrate
	- M * source[j]
	<= 0; # I dont understand what this is supposed to do

s.t. outgoing_2{j in V}:
	sum{i in E: j in Y[i]} inverted[i] 	+
	sum{i in E: j in X[i]} (1-inverted[i])
	- 0.5 * source[j]
	>= 0; # source of j can only be 1 when at least one substrate

##############

s.t. incoming_1{j in V}:
	sum{i in E: j in Y[i]} (1-inverted[i]) +
	sum{i in E: j in X[i]} inverted[i]
	- M * sink[j]
	<= 0;

s.t. incoming_2{j in V}:
	sum{i in E: j in Y[i]} (1-inverted[i]) +
	sum{i in E: j in X[i]} inverted[i]
	- 0.5 * sink[j]
	>= 0;

###############

s.t. internal_1 {j in V}:
	source[j] + sink[j] -1 - M * is_internal[j] <= 0;

s.t. internal_2 {j in V}:
	source[j] + sink[j] -1 - 0.5 * is_internal[j] >= 0;

