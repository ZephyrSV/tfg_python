## Here we see how to represent more general problems

## Instead of creating a model with data, we'll create two files :
##  - a '.mod' model file 
##  - a '.dat' data file
## The model file holds the interpretation of the data as well as 
## the problem definition.
## The data file holds the data.
## All this is fed into the AMPL pipeline and we obtain a solution.

## Example 2 (a more general representation of the first model)

## here we declare parameters with the keyword 'param'
param n; # how many different paints we can make
param t; # how many productive hours we can spend in a week
param p{i in 1..n}; # profit for paint i
param r{i in 1..n}; # rate of production of paint i
param m{i in 1..n}; # max amount of paint i we can sell

var paint{i in 1..n};

maximize profit: sum{i in 1..n} p[i]*paint[i];
subject to time: sum{i in 1..n} (1/r[i])*paint[i] <= t;
subject to capacity{i in 1..n}: 0 <= paint[i] <= m[i];

