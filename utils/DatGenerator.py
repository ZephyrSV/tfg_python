import math
import os
import re
import json

import fontTools.ttx
from Bio.KEGG import REST
from Bio.KEGG.KGML import KGML_parser

from utils.functional_programming import flatten, compose
import threading
import concurrent.futures


class SingletonClass(object):
    """
    A singleton class that can be inherited by other classes

    source: https://www.geeksforgeeks.org/singleton-pattern-in-python-a-complete-guide/
    """
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(SingletonClass, cls).__new__(cls)
        return cls.instance

class DatGenerator(SingletonClass):
    data_loc = "persistant_data/dataset.json"
    reaction_ids = []
    reactions = {}
    _reactions_lock = threading.Lock()
    pathways = {}
    _pathways_lock = threading.Lock()

    def __init__(self, reactions=None):
        if reactions is None:
            reactions = {}

        self.reactions = reactions
        self.executor = concurrent.futures.ThreadPoolExecutor()
        # if the data file does not exist
        if not os.path.isfile(self.data_loc):
            # fetch the all reaction ids
            reaction_req = REST.kegg_list("reaction").read()
            self.reaction_ids = [r[:6] for r in reaction_req.split('\n')][:-1]
            self.dump_data()
        # now the data file exists
        self.recover_data()

        unfetched_reactions = [r for r in self.reaction_ids if r not in self.reactions.keys()]
        print("unfetched_reactions len : ", len(unfetched_reactions))
        fetching_tasks = self.split_into_smaller_sublist(unfetched_reactions, 10)
        futures = [self.executor.submit(self.fetch_reactions, ft) for ft in fetching_tasks]
        concurrent.futures.wait(futures)
        print("DONE")
        self.dump_data()

    def dump_data(self):
        data = {}
        data['reaction_ids'] = self.reaction_ids
        data['reactions'] = self.reactions
        data['pathways'] = self.pathways
        with open(self.data_loc, 'w') as file:
            json.dump(data, file)

    def recover_data(self):
        """
        Recovers the reaction_ids, reactions and pathway_reactions dictionaries
        """
        with open(self.data_loc, 'r') as file:
            data = json.load(file)
            for n in data.keys():
                setattr(self, n, data[n])
            print("reactions len : ", len(self.reactions))
            print("pathway_reactions len : ", len(self.pathways))


    def fetch_reactions(self, reactions):
        reactionID_regex_str = r"ENTRY\s*(?P<reactionID>R\d{5})"
        equation_regex_str = r"EQUATION\s*(?P<substrates>[^<]*)<=>(?P<products>.*)"

        reactionID_regex = re.compile(reactionID_regex_str, re.MULTILINE)
        equation_regex = re.compile(equation_regex_str, re.MULTILINE)
        id_regex = re.compile(r"\w*\d{5}", re.MULTILINE)
        pathway_regex = re.compile(r"PATHWAY(?P<all>[^\n]*(\s{2,}[^\n]*)*)", re.MULTILINE)

        for entry in REST.kegg_get(reactions).read().split("///")[:-1]:
            for match in reactionID_regex.finditer(entry):
                reactionID = id_regex.findall(match.group(0))[0]
            # Important to not that there will only be one reactionID
            for match in equation_regex.finditer(entry):
                substrates = id_regex.findall(match.group("substrates"))
                products = id_regex.findall(match.group("products"))
                self.add_reaction(reactionID, substrates, products)
            for match in pathway_regex.finditer(entry):
                p = id_regex.findall(match.group(0))
                self.add_pathway_reaction(reactionID, p)

    def add_pathway_reaction(self, reaction_id: str, pathway_ids: list):
        with self._pathways_lock:
            for p_id in pathway_ids:
                l = self.pathways.get(p_id, [])
                l.append(reaction_id)
                self.pathways[p_id] = l

    def add_reaction(self, reaction_id, substrates, products):
        with self._reactions_lock:
            self.reactions[reaction_id] = (substrates, products)

    @staticmethod
    def split_into_smaller_sublist(l, n):
        """ Splits a list into smaller sublists of size n

        Parameters
        ----------
        l : list
            The list to be split

        n : int
            The size of the sublists
        """
        for i in range(0, len(l), n):
            yield l[i:i + n]


    def _generate_dat(self, pathway_id):
        dat_file = "dats/" + pathway_id + ".dat"
        f = open(dat_file, "w")

        generic_pathway_reactions = {k[-5:]:v for k,v in self.pathways.items()}

        reactions = {r_id: self.reactions[r_id] for r_id in generic_pathway_reactions[pathway_id[-5:]]}

        substrates_products = set()
        for substrates, products in reactions.values():
            for substrate in substrates:
                substrates_products.add(substrate)
            for product in products:
                substrates_products.add(product)

        # write the se  ts (V,E)
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
        #seen = {}
        f.write("set uninvertibles :=\n")
        #for reaction in kgml.reactions:
        #    if reaction.type == "reversible":
        #        continue
        #    else:
        #        for r in reaction.name.split(" "):
        #            if r in seen:
        #                continue
        #            f.write(r.replace("rn:", "") + " ")
        #            seen[r] = True
        f.write(";\n\n")
        f.write("set forced_externals := ;\n\nset forced_internals := ;\n\n")

        f.close()


    def generate_dats(self, entries, old=False):
        print("<>  generating dat")
        for e in entries:
            self._generate_dat(e)
        print("</> generating dat")
        return [(entry, "dats/" + entry + ".dat") for entry in entries]

if __name__ == "__main__":
    d = DatGenerator()#test case
    d.generate_dats(["hsa00010", "hsa00020"])
