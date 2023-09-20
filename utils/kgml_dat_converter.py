

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
        :param string: 
        :return: 
        """
        return string.replace(":", "_")
    
    dat_file = "kgmls/" + entry + ".dat"
    f = open(dat_file, "w")

    # write the sets (V,E)
    reactants = set()
    f.write("set E :=")
    for reaction in kgml.reactions:
        f.write(" " + sc(reaction.name))
        for substrate in reaction.substrates:
            reactants.add(sc(substrate.name))
        for product in reaction.products:
            reactants.add(sc(product.name))
    f.write(";\n")
    f.write("set V :=")
    for reactant in reactants:
        f.write(" " + reactant)
    f.write(";\n\n")

    # write the sets X and Y
    for reaction in kgml.reactions:
        f.write("set X[" + sc(reaction.name) + "] :=")
        for substrate in reaction.substrates:
            f.write(" " + sc(substrate.name))
        f.write(";\n")
        f.write("set Y[" + sc(reaction.name) + "] :=")
        for product in reaction.products:
            f.write(" " + sc(product.name))
        f.write(";\n")
    f.write("\n")

    # determine the set of reversible reactions
    f.write("param invertible :=\n")
    for reaction in kgml.reactions:
        if reaction.type == "reversible":
            f.write(sc(reaction.name) + " 1\n")
        else:
            f.write(sc(reaction.name) + " 0\n")
    f.write(";\n\n")

    f.close()
    return dat_file




