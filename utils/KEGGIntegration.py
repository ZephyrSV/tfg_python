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
        if os.path.exists(self.data_loc):
            self.load_data()
        else:
            self.compound_synonym_id = KEGGIntegration.fetch_compound_synonym_id()
        self.dump_data()

        if len(self.reaction_substrate_product_ids) == 0:
            self.fetch_reaction_substrates_ids()
            self.dump_data()



    def dump_data(self):
        """
        Dumps the data to a json file
        :return:
        """
        data = {
            "compound_synonym_id": self.compound_synonym_id,
            "reaction_substrate_product_ids": self.reaction_substrate_product_ids
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

    @staticmethod
    def fetch_compound_synonym_id():
        """
        Creates a dictionary of compound synonyms to compound ids
        A synonym can have multiple ids
        :return: a dictionary of compound synonyms to compound ids
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

    def compound_synonym_to_ids(self, synonyms: list):
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
                    print("compound: ", synonym, " has multiple ids: ", result)
                return result
        return []

    def compound_verbose_and_reaction_to_id(self, compound_verbose, reaction_id):
        """
        Returns the compound id that matches the verbose compound name

        Parameters:
            compound_verbose: a verbose compound name
            reaction_id: the reaction id that the compound belongs to

        Returns:
            a single compound id
        """
        compound_synonyms = compound_verbose.split('; ')
        # remove the number at the beginning of the synonym, that may signify the number of molecules in the equation
        for i in range(len(compound_synonyms)):
            compound_synonyms[i] = re.sub(r'^\d+n? |^\(n\+\d+\) |^n ', '', compound_synonyms[i])

        compound_id = self.compound_synonym_to_ids(compound_synonyms)
        if compound_id is None:
            return None

        return compound_id[0]

    def fetch_reaction_substrates_ids(self):
        broken_reaction_ids = []

        for reaction in REST.kegg_list("reaction").read().split('\n')[:-1]:
            reaction_id, reaction_equation_verbose = reaction.split('\t')
            self.reaction_substrate_product_ids[reaction_id] = {"substrates": [], "products": []}
            substrates_verbose, product_verbose = reaction_equation_verbose.split(' <=> ')
            for substrate_verbose in substrates_verbose.split(' + '):
                substrate_id = self.compound_verbose_and_reaction_to_id(substrate_verbose, reaction_id)
                if substrate_id is not None:
                    self.reaction_substrate_product_ids[reaction_id]["substrates"].append(substrate_id)
                else:
                    broken_reaction_ids.append(reaction_id)
                    break
            for product_verbose in product_verbose.split(' + '):
                product_id = self.compound_verbose_and_reaction_to_id(product_verbose, reaction_id)
                if product_id is not None:
                    self.reaction_substrate_product_ids[reaction_id]["products"].append(product_id)
                else:
                    broken_reaction_ids.append(reaction_id)
                    break

        print("broken reaction ids: ", len(broken_reaction_ids), ",", broken_reaction_ids)
        # for to_query in KEGGIntegration.split_into_smaller_sublist(broken_reaction_ids, 10):
        #    self.query_for_reactions(to_query)
        # TODO: run this only at university campus



    def query_for_reactions(self, reactions: list):
        """
        Queries the KEGG database for the reactions and adds them to the reactions dictionary

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







class _KEGGIntegration(SingletonClass):
    data_loc = "persistent_data/dataset.json"
    reaction_ids = []
    reactions = {}
    _reactions_lock = threading.Lock()
    pathways = {}
    _pathways_lock = threading.Lock()
    pathway_description = {}

    def __init__(self, reactions=None):
        if reactions is None:
            reactions = {}

        self.reactions = reactions
        self.executor = concurrent.futures.ThreadPoolExecutor()

        # if the data file does not exist, fetch the list of all reaction ids
        if not os.path.isfile(self.data_loc):
            # fetch the all reaction ids
            reaction_req = REST.kegg_list("reaction").read()
            self.reaction_ids = [r[:6] for r in reaction_req.split('\n')][:-1]
            self.dump_data()

        # now the data file exists
        self.recover_data()

        # fetch the reactions that have not been fully fetched
        unfetched_reactions = [r for r in self.reaction_ids if r not in self.reactions.keys()]
        print("Reactions left to query : ", len(unfetched_reactions))
        fetching_tasks = self.split_into_smaller_sublist(unfetched_reactions, 10)
        futures = [self.executor.submit(self.fetch_reactions, ft) for ft in fetching_tasks]
        concurrent.futures.wait(futures)
        self.dump_data()

        # Check if all the reactions have successfully been fetched
        unfetched_reactions = [r for r in self.reaction_ids if r not in self.reactions.keys()]
        if len(unfetched_reactions) > 0:
            raise Exception(
                f"Some reactions could not be fetched ({len(unfetched_reactions)} left)!\nThe KEGG REST API probably "
                f"IP-banned your network, please "
                "continue later (the progress has been saved). \nIf you are not trying to redownload the dataset, "
                "please make sure the persistent_data/dataset.json file has not been corrupted. \nA working version "
                "(complete as of December 2023) of the persitent_data/dataset.json file can be found in the repository."
            )
        # fetch the pathway_descriptions
        if len(self.pathway_description) == 0:
            self.pathway_description = self.fetch_pathway_descriptions()
            self.dump_data()

    def dump_data(self):
        """
        Dumps the reaction_ids, reactions and pathway_reactions dictionaries to the persistent data file
        """
        data = {
            'reaction_ids': self.reaction_ids,
            'reactions': self.reactions,
            'pathways': self.pathways,
            'pathways_description': self.pathway_description,
        }
        with open(self.data_loc, 'w') as file:
            json.dump(data, file)

    def recover_data(self):
        """
        Recovers the reaction_ids, reactions and pathway_reactions dictionaries from the persistent data file
        """
        with open(self.data_loc, 'r') as file:
            data = json.load(file)
            for n in data.keys():
                setattr(self, n, data[n])
            print("reactions len : ", len(self.reactions))
            print("pathways len : ", len(self.pathways))

    def fetch_reactions(self, reactions: list):
        """
        Queries the KEGG database for the reactions and adds them to the reactions dictionary

        Parameters
        ----------
        reactions : list
            A list of reaction ids to be fetched
        """
        reaction_id_regex = re.compile(r"ENTRY\s*(?P<reaction_id>R\d{5})", re.MULTILINE)
        equation_regex = re.compile(r"EQUATION\s*(?P<substrates>[^<]*)<=>(?P<products>.*)", re.MULTILINE)
        id_regex = re.compile(r"\w*\d{5}", re.MULTILINE)
        pathway_regex = re.compile(r"PATHWAY(?P<all>[^\n]*(\s{2,}[^\n]*)*)", re.MULTILINE)

        for entry in REST.kegg_get(reactions).read().split("///")[:-1]:
            for match in reaction_id_regex.finditer(entry):
                reaction_id = id_regex.findall(match.group(0))[0]
            # Important to not that there will only be one reaction_id
            for match in equation_regex.finditer(entry):
                substrates = id_regex.findall(match.group("substrates"))
                products = id_regex.findall(match.group("products"))
                self.add_reaction(reaction_id, substrates, products)
            for match in pathway_regex.finditer(entry):
                p = id_regex.findall(match.group(0))
                self.add_pathway_reaction(reaction_id, p)

    def add_pathway_reaction(self, reaction_id: str, pathway_ids: list):
        """
        Assigns a reaction to multiple pathways

        This method is thread safe

        Parameters
        ----------
        reaction_id : str
            The id of the reaction to be added to the pathway

        pathway_ids : list
            The ids of the pathways to which the reaction is to be added
        """
        with self._pathways_lock:
            for p_id in pathway_ids:
                reactions_of_the_pathway = self.pathways.get(p_id, [])
                reactions_of_the_pathway.append(reaction_id)
                self.pathways[p_id] = reactions_of_the_pathway

    def add_reaction(self, reaction_id: str, substrates: list, products: list):
        """
        Adds a reaction to the reactions dictionary

        This method is thread safe

        Parameters
        ----------
        reaction_id : str
            The id of the reaction to be added

        substrates : list
            The ids of the substrates of the reaction

        products : list
            The ids of the products of the reaction
        """
        with self._reactions_lock:
            self.reactions[reaction_id] = (substrates, products)

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

        generic_pathway_reactions = {k[-5:]: v for k, v in self.pathways.items()}

        reactions = {r_id: self.reactions[r_id] for r_id in generic_pathway_reactions[pathway_id[-5:]]}

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

    def fetch_pathway_descriptions(self, organism=None):
        """ Returns pathways in the form of a list of dictionaries [{'entry' = STRING, 'description' = STRING}, ... ]

        Parameters
        ----------
        organism : str, optional
            An identifier declared by KEGG database that identifies a specific organism ('hsa' for humans)
        """
        pathways = REST.kegg_list("pathway", org=organism).read().split("\n")
        pathways = [x.split("\t") for x in pathways]
        pathways = filter(lambda x: x[0] != '', pathways)  # remove empty entries
        pathways = [{'entry': x[0], 'description': x[1]} for x in pathways]
        return pathways


if __name__ == "__main__":
    d = KEGGIntegration()  # test case
    d.generate_dats(["hsa00010", "hsa00020"])
