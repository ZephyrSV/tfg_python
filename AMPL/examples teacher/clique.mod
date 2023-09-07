param n integer > 0;

set V := 1..n;
set E within V cross V;

var x {i in V} binary;

maximize target: sum {i in V} x[i];

subject to first {(i,j) in (V cross V) diff E: i < j}: x[i] + x[j] <= 1;

data;

param n := 9;

set E :=
(1,*) 3 5
(2,*) 4 6 8
(3,*) 5 7 9
(4,*) 6 8
(6,*) 8
(7,*) 9;

option solver cbc;
solve;
display x;
display _solve_user_time;

end;
