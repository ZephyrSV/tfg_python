reset;

param n integer > 0;
param m integer > 0;
param M = n;

set V := 1..n;
set E := 1..m;
set X {E} within V;
set Y {E} within V;

var z {E} binary;
var x {V} binary;
var a {V} binary;
var b {V} binary;

minimize target: sum {j in V} x[j];

#############

s.t. outgoing_1{j in V}:
	sum{i in E: j in X[i]} z[i] 	+
	sum{i in E: j in Y[i]} (1-z[i])
	- M * a[j] 
	<= 0;
	
s.t. outgoing_2{j in V}:
	sum{i in E: j in X[i]} z[i] 	+ 
	sum{i in E: j in Y[i]} (1-z[i])
	- 0.5 * a[j] 
	>= 0;

##############

s.t. incoming_1{j in V}: 
	sum{i in E: j in X[i]} (1-z[i]) +
	sum{i in E: j in Y[i]} z[i] 
	- M * b[j]
	<= 0;
	
s.t. incoming_2{j in V}: 
	sum{i in E: j in X[i]} (1-z[i]) +
	sum{i in E: j in Y[i]} z[i] 
	- 0.5 * b[j]
	>= 0;
	
###############

s.t. internal_1 {j in V}:
	a[j] + b[j] -1 - M * (1-x[j]) <= 0;
	
s.t. internal_2 {j in V}:
	a[j] + b[j] -1 - 0.5 * (1-x[j]) >= 0;
	
########################################

#data;

#param n := 7;
#param m := 4;

#set X[1] := 1;
#set X[2] := 2 3;
#set X[3] := 4 5;
#set X[4] := 5;

#set Y[1] := 2 3;
#set Y[2] := 4;
#set Y[3] := 6 7;
#set Y[4] := 7;

#option solver cbc;
#solve;
#display z;
#display x;
#display a;
#display b;
#display _solve_user_time;
