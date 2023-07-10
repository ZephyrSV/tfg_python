import sys
from Bio.KEGG import REST
from Bio.KEGG.KGML import KGML_parser

def lmap(f, l):
    return list(map(f,l))

human_pathways = REST.kegg_list("pathway", "hsa").read().split("\n")
human_pathways = map(lambda x: x.split("\t"), human_pathways)
human_pathways = filter(lambda x: x[0] != '', human_pathways) # remove empty entries
human_pathways = map(lambda x: {'entry': x[0], 'description': x[1]}, human_pathways) # entry - description  dictionary
human_pathways = list(human_pathways)


if len(sys.argv) > 1:
    human_pathways = list(filter(lambda x : sys.argv[1] in x['description'], human_pathways))
    print("Filtered down to the following pathways : ")
    print(human_pathways)
else:
    human_pathways = human_pathways[0:1]
    print(f"Using the first pathway {human_pathways[0]['entry']}")

kgmls = map(lambda x: REST.kegg_get(x['entry'], 'kgml').read(), human_pathways)
#pathway_file = list(map(lambda x: Map.parse(REST.kegg_get(x['entry']).read()), human_pathways))

pathways = list(lmap(lambda x : KGML_parser.parse(x), kgmls)[0])
pathway_reactions = lmap(lambda x : x.reactions, pathways) 
for (i, pr) in enumerate(pathway_reactions):
    # Print general information about the pathway
    print("Pathway i:", i)
    for r in pr:
        print(r)

