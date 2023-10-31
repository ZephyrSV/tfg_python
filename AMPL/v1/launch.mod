data "hsa00051.dat";

option solver cbc;
solve;
display inverted;
display is_internal;
display _solve_user_time;
end;