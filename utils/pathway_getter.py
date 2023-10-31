from Bio.KEGG import REST
from utils.functional_programming import lmap

def get_pathway(organism=None):
    """ Returns pathways in the form of a list of dictionaries [{'entry' = STRING, 'description' = STRING}, ... ]

    Parameters
    ----------
    organism : str, optional
        An identifier declared by KEGG database that identifies a specific organism (default is 'hsa' for humans)
    """
    pathways = REST.kegg_list("pathway", org=organism).read().split("\n")
    pathways = map(lambda x: x.split("\t"), pathways)
    pathways = filter(lambda x: x[0] != '', pathways) # remove empty entries
    pathways = lmap(lambda x: {'entry': x[0], 'description': x[1]}, pathways) # entry - description  dictionar
    return pathways


