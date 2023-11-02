import time

from amplpy import AMPL
import tkinter as tk
from tkinter import ttk

from utils.kgml_dat_converter import get_or_generate_dat
from utils.ui_utils import pad, GridUtil


class Pathway_view(tk.Tk):
    ampl = AMPL()
    models = {
        "My model": "AMPL/models/my_model.mod",
        "My model 2": "AMPL/models/my_model2.mod",
        "Nasini's": "AMPL/models/nasini.mod",
        "Valiente": "AMPL/models/valiente.mod"
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
        print(type(self.ampl.getVariable("inverted").getValues()))

    def init_UI(self):
        """
        Initializes the UI
        """
        g = GridUtil()

        self.title_label = ttk.Label(self, text="Select a model and a solver")
        self.title_label.grid(**pad(), **g.place(cs=2))

        g.next_row()
        self.model_label = ttk.Label(self, text="Model")
        self.model_label.grid(**pad(), **g.place())

        self.model_selector = ttk.Combobox(self, values=[key for key in self.models.keys()])
        self.model_selector.grid(**pad(), **g.place())

        g.next_row()

        self.solver_label = ttk.Label(self, text="Solver")
        self.solver_label.grid(**pad(), **g.place())

        self.solver_selector = ttk.Combobox(self, values=[key for key in self.solvers.keys()])
        self.solver_selector.grid(**pad(), **g.place())

        g.next_row()

        self.solve_button = ttk.Button(self, text="Solve", command=self.solve)
        self.solve_button.grid(**pad(), **g.place(cs=2))

    def __init__(self, entry):
        super().__init__()
        self.entry = entry
        self.dat = get_or_generate_dat(entry)
        self.title(f"Pathway {entry}")
        self.init_UI()
