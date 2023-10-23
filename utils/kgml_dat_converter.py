from functools import reduce
import re
from Bio.KEGG import REST

from utils.functional_programming import flatten, compose


def split_into_smaller_sublist(l, n):
    """ Splits a list into smaller sublists of size n

    Parameters
    ----------
    l : list
        The list to be split

    n : int
        The size of the sublists
    """
    for i in range(0, len(l), n):
        yield l[i:i + n]

def get_full_reaction(reaction_ids):
    """ Queries the KEGG API for the full reactions corresponding to the reaction IDs

    Parameters
    ----------
    reaction_ids : list(str)
        A list of reaction IDs

    Returns
    -------
    dict
        A dictionary of the form {reaction_id: (substrates, products)}
    """
    result = {}
    regexStr = r"^ENTRY\s*(?P<reaction>\S*)|EQUATION\s+(?P<substrates>.*) <=> (?P<products>.*)"
    regex = re.compile(regexStr, re.MULTILINE)
    regexStr2 = r"\w\d+"
    regex2 = re.compile(regexStr2, re.MULTILINE)
    dropUntilC = lambda y: "C" + y.split("C",1)[-1]

    for sublist in split_into_smaller_sublist(reaction_ids, 10): # 10 is the maximum number of reactions that can be fetched at once
        print("Fetching reactions " + "+".join(sublist) + " from the KEGG API...", end="")
        response = REST.kegg_get("+".join(sublist)).read()
        print("Done")
        matches = regex.finditer(response)
        current_reaction_id = None
        for match in matches:
            if match.group("reaction") is not None:
                current_reaction_id = match.group("reaction")
            if match.group("substrates") is not None:
                result[current_reaction_id] = (
                    regex2.findall(match.group("substrates")),
                    regex2.findall(match.group("products"))
                )
    return result


def kgml_to_dat(entry, kgml):
    """
    Converts a kgml file to a dat file that can be used by the solver
    :param entry: the KEGG identifier of the pathway
    :type entry: str
    :param kgml: the kgml file to be converted
    :type kgml: Bio.KEGG.KGML.KGML_pathway.Pathway
    :return: the path to the dat file
    :rtype: str
    """
    def sc(string):
        """
        Replaces the colons in a string with underscores
        
        Stands for "substitute colons" 
        :param string: the string to be processed
        """
        return string.replace("cpd:", "").replace("rn:", "").replace(" ", "_")

    dat_file = "kgmls/" + entry + ".dat"
    f = open(dat_file, "w")


    # fetch the actual reactions from the KEGG API
    get_name = lambda reaction: reaction.name
    isolate_reaction_id = lambda reaction_name: reaction_name.replace("rn:", "") # isolate_reaction_id("rn:R00001") = "R00001"
    separate_words = lambda string: string.split(" ") # separate_words("hello world") = ["hello", "world"]

    reaction_identifiers = flatten(map(compose(get_name, isolate_reaction_id, separate_words), kgml.reactions))

    reactions = get_full_reaction(reaction_identifiers)

    substrates_products = set()
    for substrates, products in reactions.values():
        for substrate in substrates:
            substrates_products.add(substrate)
        for product in products:
            substrates_products.add(product)

    # write the sets (V,E)
    f.write("set E :=")
    for r_id in reactions.keys():
        f.write(" " + r_id)
    f.write(";\n")

    f.write("set V :=")
    for sp_id in substrates_products:
        f.write(" " + sp_id)
    f.write(";\n\n")

    # write the sets X and Y
    for r_id, (subs, prods) in reactions.items():
        f.write("set X[" + r_id + "] :=")
        for s_id in subs:
            f.write(" " + s_id)
        f.write(";\n")
        f.write("set Y[" + r_id + "] :=")
        for p_id in prods:
            f.write(" " + p_id)
        f.write(";\n")
    f.write("\n")

    # determine the set of reversible reactions
    seen  = {}
    f.write("param invertible :=\n")
    for reaction in kgml.reactions:
        if reaction.type == "reversible":
            for r in reaction.name.split(" "):
                if r in seen:
                    continue
                f.write(sc(r) + " 1\n")
                seen[r] = True
        else:
            for r in reaction.name.split(" "):
                if r in seen:
                    continue
                f.write(sc(r) + " 0\n")
                seen[r] = True
    f.write(";\n\n")

    f.close()
    return dat_file




