    def compound_verbose_and_reaction_to_id(self, compound_verbose, reaction_id):
        """
        Returns the compound id that matches the verbose compound name

        Parameters:
            compound_verbose: a verbose compound name
            reaction_id: the reaction id that the compound belongs to

        Returns:
            a single compound id, or None if no match
        """

        synonym = re.sub(r'^\d+n? |^\(n\+\d+\) |^n ', '', compound_verbose)

        if synonym not in self.map_synonym_to_compound_id:
            print("Couldn't find the synonym :", synonym)
            return None
        candidates = [
            candidate # compound id
            for candidate in self.map_synonym_to_compound_id[synonym]
            if candidate in self.map_reaction_id_to_list_compound_id.get(reaction_id, [])
        ]
        if len(candidates) > 1:
            print("compound: ", synonym, " has multiple candidates: ", candidates,
                  " for reaction: ", reaction_id, ", marking as broken")
            return None
        if len(candidates) < 1:
            print("compound: ", synonym, "has no candidates in reaction", reaction_id, ", marking as broken")
            return None
        print("compound: ", synonym, " has id: ", candidates[0], " for reaction: ", reaction_id)
        return candidates[0]


    def fetch_reaction_substrates_products_ids(self):
        """ 
            Fetches the list of reactions and creates the map reaction_id to substrate_ids and product_ids:
            Uses the result from the KEGG api as well as :
            - self.map_reaction_id_to_list_compound_id
            - self.map_synonym_to_compound_id
        """
        for reaction in REST.kegg_list("reaction").read().split('\n')[:-1]:
            broken = False
            reaction_id, reaction_equation_verbose = reaction.split('\t')
            reaction_equation_verbose = reaction_equation_verbose.split("; ")[-1] # remove the name of the equation
            self.map_reaction_id_to_substrates_products_ids[reaction_id] = {"substrates": [], "products": []}
            substrates_verbose, product_verbose = reaction_equation_verbose.split(' <=> ')
            for substrate_verbose in substrates_verbose.split(' + '):
                substrate_id = self.__compound_verbose_and_reaction_to_id(substrate_verbose, reaction_id)
                if substrate_id is not None:
                    self.map_reaction_id_to_substrates_products_ids[reaction_id]\
                    ["substrates"].append(substrate_id)
                else:
                    self.broken_reaction_ids.append(reaction_id)
                    broken = True
                    break
            if broken:
                continue
            for product_verbose in product_verbose.split(' + '):
                product_id = self.__compound_verbose_and_reaction_to_id(product_verbose, reaction_id)
                if product_id is not None:
                    self.map_reaction_id_to_substrates_products_ids[reaction_id]\
                    ["products"].append(product_id)
                else:
                    self.broken_reaction_ids.append(reaction_id)
                    break