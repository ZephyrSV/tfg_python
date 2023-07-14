import os
from Bio.KEGG import REST
from Bio.KEGG.KGML import KGML_parser
from pathway_getter import get_pathway 
from kgml_downloader import kgml_download
from HyperVertex import HyperVertex
from functools import partial


def open_kgml(file_path):
    f = open(file_path, 'r')
    result = f.read()
    f.close()
    return result


def lmap(f, l):
    return list(map(f,l))

def flip(func):
    return lambda x, y: func(y, x)


# # human_pathways = get_pathway(organism="hsa", filter_str="Fructose")
# # human_pathways = human_pathways[0:1]
# print(f"Using the first pathway {human_pathways[0]['entry']}")
human_pathways =  [{"entry": "hsa00010", "description": "Glycolysis / Gluconeogenesis"}]

for hp in human_pathways:
    if not os.path.exists("kgmls/" + hp['entry'] + ".kgml"):
        print(f"The kgml file for entry {hp['entry']} is being downloaded")
        kgml_download(hp['entry'])


kgmls = lmap(lambda x: open_kgml("kgmls/"+ x['entry'] + ".kgml"), human_pathways)


pathways = map(KGML_parser.parse, kgmls)
pathways = lmap(lambda x: list(x)[0], pathways)
pathway_reactions = lmap(lambda x: x.reactions, pathways)

compounds = {}
for (i, pr) in enumerate(pathway_reactions):
    # Print general information about the pathway
    print("Pathway i:", i)
    for reaction in pr:
        for substrate in reaction.substrates:
            if substrate.name not in compounds:
                compounds[substrate.name] = HyperVertex(substrate.name)
            compounds[substrate.name].add_edge_tail(reaction)
        for product in reaction.products:
            if product.name not in compounds:
                compounds[product.name] = HyperVertex(product.name)
            compounds[product.name].add_edge_head(reaction)


# Print the compounds and how many reactions they are involved in
for compound in compounds:
    print(f"{compound} is involved is substrates in {len(compounds[compound].edges_tail)} reactions")
    print(f" -> products in {len(compounds[compound].edges_head)} reactions")
    if len(compounds[compound].edges_head) == 0 or len(compounds[compound].edges_tail) == 0:
        print(f" -> is an external compound")