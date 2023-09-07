reset;
set V := 1..5;

# Define the sets substrates_in
set substrates_in{V};

# Declare a variable x indexed by V and an additional index
#var x{V, i in 1..max {k in V} card(substrates_in[k])};



# Populate the sets substrates_in
data;
set substrates_in[1] := 1;
set substrates_in[2] := 4 6 8;
set substrates_in[3] := 2;
set substrates_in[4] := 3;
set substrates_in[5] := 3 4;
display substrates_in[2];
end data;