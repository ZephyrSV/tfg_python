import math
import os
import re

import fontTools.ttx
from Bio.KEGG import REST
from Bio.KEGG.KGML import KGML_parser

from utils.functional_programming import flatten, compose
import threading
import concurrent.futures


class DatGenerator:
    _reactions = {}
    _reactions_lock = threading.Lock()
    _unfetched_reactions = set()
    _unfetched_reactions_lock = threading.Lock()
    _pathway_reactions_kgml = {}
    _pathway_reactions_kgml_lock = threading.Lock()

    def __init__(self, reactions=None):
        if reactions is None:
            reactions = {}
        self._reactions = reactions
        self.executor = concurrent.futures.ThreadPoolExecutor()

    def _add_unfetched_reaction(self, reaction):
        with self._unfetched_reactions_lock:
            self._unfetched_reactions.add(reaction)

    def _add_pathway_reaction_kgml(self, pathway, reactions, kgml):
        with self._pathway_reactions_kgml_lock:
            self._pathway_reactions_kgml[pathway] = (reactions, kgml)

    def _add_reaction(self, reaction_id, substrates, products):
        with self._reactions_lock:
            self._reactions[reaction_id] = (substrates, products)

    def _get_reaction_ids_from_kgml(self, entry):
        kgml = next(KGML_parser.parse(REST.kegg_get(entry, 'kgml').read()))
        # fetch the actual reactions from the KEGG API
        reaction_identifiers = flatten([r.name.replace("rn:", "").split(" ") for r in kgml.reactions])
        self._add_pathway_reaction_kgml(entry, reaction_identifiers, kgml)
        unfetched = filter(lambda r_id: r_id not in self._reactions.keys(), reaction_identifiers)
        for reaction_id in unfetched:
            self._add_unfetched_reaction(reaction_id)
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

    def _get_full_reactions(self, reaction_ids):
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
                self._add_reaction(
                    current_reaction_id,
                    regex2.findall(match.group("substrates")),
                    regex2.findall(match.group("products"))
                )

    def _generate_dat(self, entry, reaction_ids, kgml):
        dat_file = "dats/" + entry + ".dat"
        f = open(dat_file, "w")

        reactions = {r_id: self._reactions[r_id] for r_id in reaction_ids}

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
        seen = {}
        f.write("set uninvertible :=\n")
        for reaction in kgml.reactions:
            if reaction.type == "reversible":
                continue
            else:
                for r in reaction.name.split(" "):
                    if r in seen:
                        continue
                    f.write(r.replace("rn:", "") + " ")
                    seen[r] = True
        f.write(";\n\n")

        f.write("set forced_externals := ;\n\nset forced_internals := ;\n\n")

        f.close()

    def generate_dats(self, entries):
        """ Generates a dat file for each entry in the list

        Parameters
        ----------
        entries : list(str)
            A list of entry IDs
        """
        new_entries = [entry for entry in entries if not os.path.isfile("dats/" + entry + ".dat")]
        futures = [self.executor.submit(self._get_reaction_ids_from_kgml, entry) for entry in new_entries]
        concurrent.futures.wait(futures)

        lists_of_10_reactions = list(DatGenerator.split_into_smaller_sublist(list(self._unfetched_reactions), 10))
        futures = [self.executor.submit(self._get_full_reactions, l) for l in lists_of_10_reactions]
        concurrent.futures.wait(futures)

        futures = [self.executor.submit(self._generate_dat, entry, *self._pathway_reactions_kgml[entry])
                   for entry in new_entries]
        concurrent.futures.wait(futures)

        return [(entry, "dats/" + entry + ".dat") for entry in entries]

if __name__ == "__main__":
    d = DatGenerator()#test case
    d.generate_dats(["hsa00010", "hsa00020"])
