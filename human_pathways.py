import os
from Bio.KEGG import REST
from Bio.KEGG.KGML import KGML_parser
from pathway_getter import get_pathway 
from kgml_downloader import kgml_download

def lmap(f, l):
    return list(map(f,l))

human_pathways = get_pathway(organism="hsa", filter_str="Fructose")
human_pathways = human_pathways[0:1]
print(f"Using the first pathway {human_pathways[0]['entry']}")

for hp in human_pathways:
    if not os.path.exists("kgmls/" + hp['entry'] + ".kgml"):
        print(f"The kgml file for entry {hp['entry']} is being downloaded")
        kgml_download(hp['entry'])

def open_kgml(file_path):
    f = open(file_path, 'r')
    result = f.read()
    f.close()
    return result

kgmls = lmap(lambda x: open_kgml("kgmls/"+ x['entry'] + ".kgml"), human_pathways)


pathways = map(lambda x : KGML_parser.parse(x), kgmls)
pathways = lmap(lambda x : list(x)[0], pathways)
pathway_reactions = lmap(lambda x : x.reactions, pathways) 
for (i, pr) in enumerate(pathway_reactions):
    # Print general information about the pathway
    print("Pathway i:", i)
    for r in pr:
        print(r)

