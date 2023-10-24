import os
import time

from Bio.KEGG import REST
from Bio.KEGG.KGML import KGML_parser
from amplpy import AMPL
import tkinter as tk
from tkinter import ttk

from utils.kgml_dat_converter import kgml_to_dat
from utils.ui_utils import pad, gridrc


def get_kgml(entry):
    """
    Fetches and downloads the kgml files associated to the entries, stores them in kgmls/
    :param entry: the KEGG identifier of the pathway
    :rtype: Bio.KEGG.KGML.KGML_pathway.Pathway
    """
    if not os.path.exists("kgmls/" + entry + ".kgml"):
        print(f"The kgml file for entry {entry} is being downloaded...", end="")
        f = open("kgmls/" + entry + ".kgml", "w")
        f.write(REST.kegg_get(entry, 'kgml').read())
        f.close()
        print("done!")
    return next(KGML_parser.parse(open("kgmls/" + entry + ".kgml", "r")))

class Pathway_view(tk.Tk):
    ampl = AMPL()
    models = {
        "My model": "AMPL/models/my_model.mod",
        "Teacher's Version": "AMPL/models/teacherversion.mod"
    }
    solvers = {
        "CPLEX": "cplex",
        "Gurobi": "gurobi",
        "cbc": "cbc",
    }

    def solve(self):
        """
        Solves the pathway
        """
        self.ampl.read(self.models[self.model_selector.get()])
        self.ampl.readData(self.dat)
        self.ampl.option["solver"] = self.solvers[self.solver_selector.get()]
        before_solve_time = time.time()
        self.ampl.solve()
        print("--- %s seconds ---" % (time.time() - before_solve_time))
        print(self.ampl.getObjective("obj").value())
        print(self.ampl.getVariable("inverted").getValues())


    def init_UI(self):
        """
        Initializes the UI
        """
        row = 0
        self.title_label = ttk.Label(self, text="Select a model and a solver")
        self.title_label.grid(**pad(), **gridrc(row, 0, cs = 2))

        row += 1
        self.model_label = ttk.Label(self, text="Model")
        self.model_label.grid(**pad(), **gridrc(row, 0))

        self.model_selector = ttk.Combobox(self, values=[key for key in self.models.keys()])
        self.model_selector.grid(**pad(), **gridrc(row, 1))

        row += 1

        self.solver_label = ttk.Label(self, text="Solver")
        self.solver_label.grid(**pad(), **gridrc(row, 0))

        self.solver_selector = ttk.Combobox(self, values=[key for key in self.solvers.keys()])
        self.solver_selector.grid(**pad(), **gridrc(row, 1))

        row += 1

        self.solve_button = ttk.Button(self, text="Solve", command=self.solve)
        self.solve_button.grid(**pad(), **gridrc(row, 0, cs = 2))



    def __init__(self, entry):
        super().__init__()
        self.entry = entry
        self.kgml = get_kgml(entry)

        self.dat = kgml_to_dat(entry, self.kgml)

        self.title(f"Pathway {entry}")


        self.init_UI()



