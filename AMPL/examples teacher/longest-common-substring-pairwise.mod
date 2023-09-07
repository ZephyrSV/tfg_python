param S {1..2} symbolic;

/* longest common prefix */
param lcp {p in 1..length(S[1]),q in 1..length(S[2])} := max {k in 0..min(length(S[1])-p+1,length(S[2])-q+1): substr(S[1],p,k) = substr(S[2],q,k)} k;

param lcs := max {p in 1..length(S[1]),q in 1..length(S[2])} lcp[p,q];

# 1 iff a solution appears at position p of S[1] and position q of S[2]
var x {p in 1..length(S[1]),q in 1..length(S[2])} binary;

maximize target: sum {p in 1..length(S[1]),q in 1..length(S[2])} lcp[p,q]*x[p,q];

subject to first: sum {p in 1..length(S[1]),q in 1..length(S[2])} x[p,q] = 1;

data;

param S :=
1 "GCTTCCGGCTCGTATAATGTGTGG"
2 "TGCTTCTGACTATAATAG";

option solver cbc;
solve;

for {p in 1..length(S[1]),q in 1..length(S[2]): x[p,q] != 0} display p,q,substr(S[1],p,lcs),substr(S[2],q,lcs);

# p = 13
# q = 11
# substr(S[1], p, lcs) = TATAAT
# substr(S[2], q, lcs) = TATAAT
