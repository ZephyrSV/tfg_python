subject to is_internal_1 {i in V}:
        is_internal[i] * 2 <= has_incoming [i] + has_outgoing [i];

subject to is_internal_2 {i in V}:
        is_internal[i] >= has_incoming[i] + has_outgoing[i] - 1;