from bioservices import KEGG
k = KEGG()
reactions = k.reactionIds
for reaction in reactions:
    data = k.parse(k.get(reaction))
    if 'PATHWAY' not in data.keys():
        continue
    for pathway in sorted(data['PATHWAY'].keys()):
        print("{}: {}: {}".format(
            reaction, 
            pathway,
            data['EQUATION']))
