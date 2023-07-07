from Bio.KEGG.REST import kegg_link

# Define the pathway ID
pathway_id = "hsa00051"

# Retrieve the pathway information
pathway_data = kegg_link("pathway", pathway_id).read()

print(pathway_data)
# Extract the reactions from the pathway data
reactions = []
for line in pathway_data.rstrip().split("\n"):
    if line.startswith("reaction:"):
        reaction_id = line.split()[1]
        reactions.append(reaction_id)

# Print the reactions
for reaction in reactions:
    print(reaction)
print("done")
