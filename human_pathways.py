import sys
from Bio.KEGG import REST

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

pathway_file = map(lambda x: REST.kegg_get(x['entry'], 'kgml').read(), human_pathways)

for e in pathway_file:
    print(e)
    
