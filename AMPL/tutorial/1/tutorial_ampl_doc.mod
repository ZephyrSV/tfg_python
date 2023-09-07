## This is a comment
## AMPL is case-sensitive
## names are unique (even between vars and constraints)
## A line of code always ends with ';'

var PaintB;  # This is a variable that we will try to optimize
var PaintG;  

## The objective starts with 
##  (maximize|minimize) (?<name>\w+) ?:
maximize profit: 10*PaintB + 15*PaintG;

# The constraints start with 
# subject to (?<name>\w+) ?:
subject to time: (1/40)*PaintB + (1/30)*PaintG <= 40;
subject to blue_limit: 0 <= PaintB <= 1000;
subject to gold_limit: 0 <= PaintG <= 860;
 
## To get the results you run
option solver cplex;
solve;

## To display the values
display PaintB;
display PaintG;