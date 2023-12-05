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


class DatGenerator:
    data_loc = "persistant_data/dataset.json"
    reaction_ids = []
    reactions = {}
    _reactions_lock = threading.Lock()
    pathway_reactions = {}
    _pathway_reactions_lock = threading.Lock()
    unfetched_reactions = set()
    _unfetched_reactions_lock = threading.Lock()
    pathway_reactions_kgml = {}
    _pathway_reactions_kgml_lock = threading.Lock()

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
        data['pathways'] = self.pathway_reactions
        with open(self.data_loc, 'w') as file:
            json.dump(data, file)

    def recover_data(self):
        """
        Recovers the reaction_ids, reactions and pathway_reactions dictionaries
        """
        with open(self.data_loc, 'r') as file:
            data = json.load(file)
            self.reaction_ids = data['reaction_ids']
            self.reactions = data.get('reactions', {})
            self.pathway_reactions = data.get('pathways', {})
            print("reactions len : ", len(self.reactions))
            print("pathway_reactions len : ", len(self.pathway_reactions))


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
                pathways = id_regex.findall(match.group(0))
                self.add_pathway_reaction(reactionID, pathways) 
        #print("/!\\ pathway_reactions : ", self.pathway_reactions)
        #print("reactions : ", self.reactions)

    def add_pathway_reaction(self, reaction_id: str, pathway_ids: list):
        with self._pathway_reactions_lock:
            for p_id in pathway_ids:
                l = self.pathway_reactions.get(p_id, [])
                l.append(reaction_id)
                self.pathway_reactions[p_id] = l

#####################


    def add_unfetched_reaction(self, reaction):
        with self._unfetched_reactions_lock:
            self.unfetched_reactions.add(reaction)

    def add_pathway_reaction_kgml(self, pathway, reactions, kgml):
        with self._pathway_reactions_kgml_lock:
            self.pathway_reactions_kgml[pathway] = (reactions, kgml)

    def add_reaction(self, reaction_id, substrates, products):
        with self._reactions_lock:
            self.reactions[reaction_id] = (substrates, products)

    def get_reaction_ids_from_kgml(self, entry):
        kgml = next(KGML_parser.parse(REST.kegg_get(entry, 'kgml').read()))
        # fetch the actual reactions from the KEGG API
        reaction_identifiers = flatten([r.name.replace("rn:", "").split(" ") for r in kgml.reactions])
        self.add_pathway_reaction_kgml(entry, reaction_identifiers, kgml)
        unfetched = filter(lambda r_id: r_id not in self.reactions.keys(), reaction_identifiers)
        for reaction_id in unfetched:
            self.add_unfetched_reaction(reaction_id)
        print(f"Fetching {len(reaction_identifiers)} reactions for {entry}")

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

    def get_full_reactions(self, reaction_ids):
        if len(reaction_ids) == 0:
            raise ValueError("reaction_ids must not be empty")
        if len(reaction_ids) > 10:
            raise ValueError("reaction_ids must not be longer than 10")

        print("Fetching reactions " + "+".join(reaction_ids) + f" from the KEGG API...")

        regexStr = r"^ENTRY\s*(?P<reaction>\S*)|EQUATION\s+(?P<substrates>.*) <=> (?P<products>.*)"
        regex = re.compile(regexStr, re.MULTILINE)
        regexStr2 = r"\w\d+"
        regex2 = re.compile(regexStr2, re.MULTILINE)

        response = REST.kegg_get("+".join(reaction_ids)).read()
        matches = regex.finditer(response)
        current_reaction_id = None
        for match in matches:
            if match.group("reaction") is not None:
                current_reaction_id = match.group("reaction")
            if match.group("substrates") is not None:
                self.add_reaction(
                    current_reaction_id,
                    regex2.findall(match.group("substrates")),
                    regex2.findall(match.group("products"))
                )

    def _generate_dat(self, pathway_id, reaction_ids, kgml):
        dat_file = "dats/" + pathway_id + ".dat"
        f = open(dat_file, "w")

        generic_pathway_reactions = {k[-5:]:v for k,v in self.pathway_reactions.items()}

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
            print(type(reaction_ids))
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
        #
        f.write("set forced_externals := ;\n\nset forced_internals := ;\n\n")

        f.close()


    def generate_dats(self, entries, old=False):
        if old:
            return self.generate_dats_old(entries)            
            
        print("<>generating dat")
        for e in entries:
            self._generate_dat(e, None, None)
        print("</>generating dat")
        #futures = [self.executor.submit(self._generate_dat, e, None, None)
        #           for e in entries]
        #concurrent.futures.wait(futures)

        return [(entry, "dats/" + entry + ".dat") for entry in entries]
    def generate_dats_old(self, entries):
		
        """ Generates a dat file for each entry in the list

        Parameters
        ----------
        entries : list(str)
            A list of entry IDs
        """
        new_entries = [entry for entry in entries if not os.path.isfile("dats/" + entry + ".dat")]
        futures = [self.executor.submit(self.get_reaction_ids_from_kgml, entry) for entry in new_entries]
        concurrent.futures.wait(futures)

        lists_of_10_reactions = list(DatGenerator.split_into_smaller_sublist(list(self.unfetched_reactions), 10))
        futures = [self.executor.submit(self.get_full_reactions, l) for l in lists_of_10_reactions]
        concurrent.futures.wait(futures)

        futures = [self.executor.submit(self._generate_dat, entry, *self.pathway_reactions_kgml[entry])
                   for entry in new_entries]
        concurrent.futures.wait(futures)

        return [(entry, "dats/" + entry + ".dat") for entry in entries]

if __name__ == "__main__":
    d = DatGenerator()#test case
    d.generate_dats(["hsa00010", "hsa00020"])
