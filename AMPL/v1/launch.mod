#data "hsa00051.dat";

option solver cbc;
solve;
display inverted;
display source;
display sink;
display _solve_user_time;
end;