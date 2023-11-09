from Bio.KEGG import REST

def fetch_all_pathways(organism=None):
    """ Returns pathways in the form of a list of dictionaries [{'entry' = STRING, 'description' = STRING}, ... ]

    Parameters
    ----------
    organism : str, optional
        An identifier declared by KEGG database that identifies a specific organism ('hsa' for humans)
    """
    pathways = REST.kegg_list("pathway", org=organism).read().split("\n")
    pathways = [x.split("\t") for x in pathways]
    pathways = filter(lambda x: x[0] != '', pathways)  # remove empty entries
    pathways = [{'entry': x[0], 'description': x[1]} for x in pathways]
    return pathways
