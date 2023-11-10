#data "hsa00051.dat";

option solver cbc;
solve;
display inverted;
display source;
display sink;
display _solve_user_time;

for {i in E: inverted[i] == 1} {
	printf "%s: ", i;
	printf {j in X[i]} "%s ", j;
	printf "---> ";
	printf {j in Y[i]} "%s ", j;
	printf "\n" ;
}

#printf {i in E: inverted[i] == 1} "%s : %s --> %s \n", i, awk{j  >>> in  <<< Y[i]} j, {k in X[i]} k ; 
end;