from Bio.KEGG import REST

def lmap(f, l):
    """ Short hand for list(map(f, l))

    Parameters
    ----------
    f : function
        The function to map the elements to

    l : generator
        The generator that gives the elements to apply the map() to
    """
    return list(map(f,l))

def get_pathway(organism = "hsa", filter_str = None):
    """ Returns pathways in the form of a list of dictionaries [{'entry' = STRING, 'description' = STRING}, ... ]

    Parameters
    ----------
    organism : str, optional
        An identifier declared by KEGG database that identifies a specific organism (default is 'hsa' for humans)

    filter_str : str, optional
        The descriptions of the result will contain this str, if left default, we return true to all
    """
    human_pathways = REST.kegg_list("pathway", organism).read().split("\n")
    human_pathways = map(lambda x: x.split("\t"), human_pathways)
    human_pathways = filter(lambda x: x[0] != '', human_pathways) # remove empty entries
    human_pathways = lmap(lambda x: {'entry': x[0], 'description': x[1]}, human_pathways) # entry - description  dictionary
    if filter_str is not None:
        human_pathways = list(filter(lambda x : filter_str in x['description'], human_pathways))
    return human_pathways


