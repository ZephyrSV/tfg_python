import concurrent.futures
import json
import os
import re
import threading

from Bio.KEGG import REST


class SingletonClass(object):
    """
    A singleton class that can be inherited by other classes

    source: https://www.geeksforgeeks.org/singleton-pattern-in-python-a-complete-guide/
    """

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(SingletonClass, cls).__new__(cls)
        return cls.instance


class KEGGIntegration(SingletonClass):
    """
    A class that handles the integration with KEGG

    Some of the methods are static (to avoid using state)

    Here are some definitions:
        - compound: a chemical compound, can be identified by a compound id or by a list of synonyms
            example: C00001 or ['H2O', 'Water']
        - reaction: a chemical reaction, can be identified by a reaction id
    Here are some programming shorthands used in this class:
        - 'var_name'_verbose: means that the object is made up of a collection of synonyms
            example: equation_verbose is something like "Maltose + H2O <=> 2 D-Glucose"
    """
    data_loc = "persistent_data/data.json"

    def __init__(self):
        self.reaction_substrate_product_ids = {}
        self.compound_synonym_id = {}
        self.broken_reaction_ids = []
        self.fetched_breaking_reaction_ids = []
        self.reaction_compound_ids = {}
        self.pathway_reaction_ids = {}
        self.pathway_descriptions = {}
        if os.path.exists(self.data_loc):
            self.load_data()
        else:
            self.compound_synonym_id = KEGGIntegration.fetch_compound_synonym_id()
            self.reaction_compound_ids = KEGGIntegration.fetch_reaction_compound_ids()
            self.dump_data()

        if len(self.reaction_substrate_product_ids) == 0:
            print("fetching reactions and their substrate product ids")
            self.fetch_reaction_substrates_ids()
            self.dump_data()
        if len(self.pathway_reaction_ids) == 0:
            print("fetching pathways and their reaction ids")
            self.pathway_reaction_ids = KEGGIntegration.fetch_pathway_reaction_ids()
            self.dump_data()
        if len(self.get_remaing_breaking_reaction_ids()) != 0:
            print("broken reaction ids: ", self.get_remaing_breaking_reaction_ids())
            self.fetch_broken_reactions()
            self.dump_data()
        if len(self.pathway_descriptions) == 0:
            print("fetching pathways and their descriptions")
            self.pathway_descriptions = KEGGIntegration.fetch_pathway_descriptions()
            self.dump_data()

    def get_remaing_breaking_reaction_ids(self):
        return [x for x in self.broken_reaction_ids if x not in self.fetched_breaking_reaction_ids]

    def dump_data(self):
        """
        Dumps the data to a json file
        :return:
        """
        data = {
            "compound_synonym_id": self.compound_synonym_id,
            "reaction_substrate_product_ids": self.reaction_substrate_product_ids,
            "broken_reaction_ids": self.broken_reaction_ids,
            "fetched_breaking_reaction_ids": self.fetched_breaking_reaction_ids,
            "reaction_compound_ids": self.reaction_compound_ids,
            "pathway_reaction_ids": self.pathway_reaction_ids,
            "pathway_descriptions": self.pathway_descriptions,
        }
        with open(self.data_loc, 'w') as f:
            json.dump(data, f)

    def load_data(self):
        """
        Loads the data from a json file
        :return:
        """
        with open(self.data_loc, 'r') as f:
            data = json.load(f)
        self.compound_synonym_id = data["compound_synonym_id"]
        self.reaction_substrate_product_ids = data["reaction_substrate_product_ids"]
        self.broken_reaction_ids = data["broken_reaction_ids"]
        self.fetched_breaking_reaction_ids = data["fetched_breaking_reaction_ids"]
        self.reaction_compound_ids = data["reaction_compound_ids"]
        self.pathway_reaction_ids = data["pathway_reaction_ids"]
        self.pathway_descriptions = data["pathway_descriptions"]
        
    @staticmethod
    def fetch_reaction_compound_ids():
        """
        Creates a dictionary of reaction ids to compound ids
        A reaction can have multiple compounds, we can't know which are substrates and which are products
        Returns:
            a dictionary of reaction ids to compound ids
        """
        reaction_coumpound_ids = {}
        reaction_compound_ids_req = REST.kegg_link("compound", "reaction").read()
        for reaction_compound_id in reaction_compound_ids_req.split('\n')[:-1]:
            reaction_id, compound_id = [type_and_id.split(':')[1] for type_and_id in reaction_compound_id.split('\t')]
            if reaction_id in reaction_coumpound_ids.keys():
                reaction_coumpound_ids[reaction_id].append(compound_id)
            else:
                reaction_coumpound_ids[reaction_id] = [compound_id]
        return reaction_coumpound_ids
        

    @staticmethod
    def fetch_compound_synonym_id():
        """
        Creates a dictionary of compound synonyms to compound ids
        A synonym can have multiple ids
        Returns:
            a dictionary of compound synonyms to compound ids
        """
        compound_names_id = {}
        compound_req = REST.kegg_list("compound").read()
        for compound in compound_req.split('\n')[:-1]:
            compound_id, compound_name_list = compound.split('\t')
            for compound_synonym in compound_name_list.split('; '):
                print("compound_synonym: ", compound_synonym, compound_synonym in compound_names_id.keys())
                if compound_synonym in compound_names_id.keys():
                    compound_names_id[compound_synonym].append(compound_id)
                else:
                    compound_names_id[compound_synonym] = [compound_id]
                print("I stored: ", compound_synonym, compound_names_id[compound_synonym])

        return compound_names_id
    @staticmethod
    def fetch_pathway_reaction_ids():
        """
        Creates a dictionary of pathway ids to reaction ids
        A pathway can have multiple reactions
        Returns:
            a dictionary of pathway ids to reaction ids
        """
        pathway_reaction_ids = {}
        pathway_reaction_ids_req = REST.kegg_link("reaction", "pathway").read()
        for pathway_reaction_id in pathway_reaction_ids_req.split('\n')[:-1]:
            pathway_verbose, reaction_verbose = pathway_reaction_id.split('\t')
            pathway_id = pathway_verbose.split(':')[1]
            reaction_id = reaction_verbose.split(':')[1]
            if pathway_id in pathway_reaction_ids.keys():
                pathway_reaction_ids[pathway_id].append(reaction_id)
            else:
                pathway_reaction_ids[pathway_id] = [reaction_id]
        return pathway_reaction_ids


    @staticmethod
    def split_into_smaller_sublist(list_to_split, n):
        """ Splits a list into smaller sublists of size n

        Parameters
        ----------
        list_to_split : list
            The list to be split

        n : int
            The size of the sublists
        """
        for i in range(0, len(list_to_split), n):
            yield list_to_split[i:i + n]

    @staticmethod
    def fetch_pathway_descriptions(organism=None):
        """ Returns pathways in the form of a dictionary of the form {pathway_id: pathway_description}
        """
        pathways = REST.kegg_list("pathway", org=organism).read().split("\n")
        pathways = [x.split("\t") for x in pathways]
        pathways = filter(lambda x: x[0] != '', pathways)  # remove empty entries
        pathways = {x[0]: x[1] for x in pathways}
        return pathways

    def compound_synonym_to_ids(self, synonyms: list, reaction_id: str):
        """
        Returns the compound ids that matches the synonym

        Parameters:
            synonyms: list of synonyms

        Returns:
            list of compound ids, or empty list if no match
        """
        for synonym in synonyms:
            if synonym in self.compound_synonym_id:
                result = self.compound_synonym_id[synonym]
                if len(result) > 1:
                    print("compound: ", synonym, " has multiple ids: ", result, " for reaction: ", reaction_id)
                    result = [
                        compound_id 
                        for compound_id in result 
                        if compound_id in self.reaction_compound_ids[reaction_id]
                    ]
                    if len(result) > 1:
                        print("compound: ", synonym, " STILL has multiple ids: ", result, " for reaction: ", reaction_id)
                        return []
                    else :
                        print("compound: ", synonym, " has id: ", result, " for reaction: ", reaction_id)
                
                return result
        return []

    def compound_verbose_and_reaction_to_id(self, compound_verbose, reaction_id):
        """
        Returns the compound id that matches the verbose compound name

        Parameters:
            compound_verbose: a verbose compound name
            reaction_id: the reaction id that the compound belongs to

        Returns:
            a single compound id, or None if no match
        """
        compound_synonyms = compound_verbose.split('; ')
        # remove the number at the beginning of the synonym, that may signify the number of molecules in the equation
        for i in range(len(compound_synonyms)):
            compound_synonyms[i] = re.sub(r'^\d+n? |^\(n\+\d+\) |^n ', '', compound_synonyms[i])

        compound_id = self.compound_synonym_to_ids(compound_synonyms, reaction_id)
        if len(compound_id) == 0:
            return None

        return compound_id[0]

    def fetch_reaction_substrates_ids(self):
        for reaction in REST.kegg_list("reaction").read().split('\n')[:-1]:
            broken = False
            reaction_id, reaction_equation_verbose = reaction.split('\t')
            self.reaction_substrate_product_ids[reaction_id] = {"substrates": [], "products": []}
            substrates_verbose, product_verbose = reaction_equation_verbose.split(' <=> ')
            for substrate_verbose in substrates_verbose.split(' + '):
                substrate_id = self.compound_verbose_and_reaction_to_id(substrate_verbose, reaction_id)
                if substrate_id is not None:
                    self.reaction_substrate_product_ids[reaction_id]["substrates"].append(substrate_id)
                else:
                    self.broken_reaction_ids.append(reaction_id)
                    broken = True
                    break
            if broken:
                continue
            for product_verbose in product_verbose.split(' + '):
                product_id = self.compound_verbose_and_reaction_to_id(product_verbose, reaction_id)
                if product_id is not None:
                    self.reaction_substrate_product_ids[reaction_id]["products"].append(product_id)
                else:
                    self.broken_reaction_ids.append(reaction_id)
                    break

        for reaction_id in self.broken_reaction_ids:
            self.reaction_substrate_product_ids.pop(reaction_id)
            # remove the reaction from the dictionary, or else we won't know which reactions are broken upon
            # relaunching the script

    def fetch_broken_reactions(self):
        unfetched_reaction_ids = [
            reaction_id
            for reaction_id in self.broken_reaction_ids
            if reaction_id not in self.fetched_breaking_reaction_ids
        ]
        for to_query in KEGGIntegration.split_into_smaller_sublist(unfetched_reaction_ids, 10):
            self.query_for_reactions(to_query)
            self.fetched_breaking_reaction_ids.extend(to_query)



    def query_for_reactions(self, reactions: list):
        """
        Queries the KEGG database (GET of REST) for the reactions (by groups of 10) and adds them to the reactions dictionary

        Parameters
        ----------
        reactions : list
            A list of reaction ids to be fetched
        """
        reaction_id_regex = re.compile(r"ENTRY\s*(?P<reaction_id>R\d{5})", re.MULTILINE)
        equation_regex = re.compile(r"EQUATION\s*(?P<substrates>[^<]*)<=>(?P<products>.*)", re.MULTILINE)
        id_regex = re.compile(r"\w*\d{5}", re.MULTILINE)

        for entry in REST.kegg_get(reactions).read().split("///")[:-1]:
            reaction = {"substrates": [], "products": []}
            for match in reaction_id_regex.finditer(entry):
                reaction_id = id_regex.findall(match.group(0))[0]
            # Important to not that there will only be one reaction_id
            for match in equation_regex.finditer(entry):
                reaction["substrates"] = id_regex.findall(match.group("substrates"))
                reaction["products"] = id_regex.findall(match.group("products"))

            self.reaction_substrate_product_ids[reaction_id] = reaction

    def generate_dats(self, entries: list):
        """
        Generates the .dat files for the pathways

        Parameters
        ----------
        entries : list
            A list of pathway ids for which the .dat files are to be generated

        Returns
        -------
        list
            A list of tuples containing the pathway id and the path to the .dat file
        """
        print("<>  generating dat")
        for e in entries:
            self._generate_dat(e)
        print("</> generating dat")
        return [(entry, "dats/" + entry + ".dat") for entry in entries]

    def _generate_dat(self, pathway_id: str):
        """
        Generates the .dat file for the pathway

        Parameters
        ----------
        pathway_id : str
            The id of the pathway for which the .dat file is to be generated
        """
        dat_file = "dats/" + pathway_id + ".dat"
        f = open(dat_file, "w")

        generic_pathway_reactions = {k[-5:]: v for k, v in self.pathway_reaction_ids.items()}

        reactions = {r_id: self.reaction_substrate_product_ids[r_id].values() for r_id in generic_pathway_reactions[pathway_id[-5:]]}

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
        # seen = {}
        f.write("set uninvertibles :=\n")
        # for reaction in kgml.reactions:
        #     if reaction.type == "reversible":
        #         continue
        #     else:
        #         for r in reaction.name.split(" "):
        #             if r in seen:
        #                 continue
        #             f.write(r.replace("rn:", "") + " ")
        #             seen[r] = True
        f.write(";\n\n")
        f.write("set forced_externals := ;\n\nset forced_internals := ;\n\n")

        f.close()








