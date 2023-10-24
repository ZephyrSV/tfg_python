data "hsa01100.dat";

option solver cbc;
solve;
display inverted;
display is_internal;
display _solve_user_time;

reset;
end;