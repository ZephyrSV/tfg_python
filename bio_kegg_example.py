from Bio.KEGG import REST

# Retrieve information about a specific pathway
pathway_id = "hsa00010"  # Example pathway ID for "Glycolysis / Gluconeogenesis"
pathway_data = REST.kegg_get(pathway_id).read()  # Retrieve pathway information

# Print the pathway data
print(pathway_data)

