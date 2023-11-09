import time

from amplpy import AMPL
import tkinter as tk
from tkinter import ttk

from utils.kgml_dat_converter import get_or_generate_dat
from utils.ui_utils import pad, GridUtil


class PathwayView(tk.Toplevel):
    ampl = AMPL()
    models = {
        "Zephyr": "AMPL/models/zephyr.mod",
        #"Zephyr Optimized": "AMPL/models/my_model2.mod",
        "Nasini": "AMPL/models/nasini.mod",
        #"Valiente": "AMPL/models/valiente.mod"
    }
    solvers = {
        "cbc": "cbc",
        "CPLEX": "cplex",
        "Gurobi": "gurobi",
    }
    tickbox_labels = [
        "respect invertability",
        "force internals",
        "force externals",
    ]
    tickbox_models = {
        "respect invertability": "AMPL/models/restrictions/respect_invertability.mod",
        "force internals": "AMPL/models/restrictions/forced_internals.mod",
        "force externals": "AMPL/models/restrictions/forced_externals.mod",
    }
    tickbox_vars = {}
    tickbox_elements = {}

    def solve(self):
        """
        Solves the pathway
        """
        self.ampl.read(self.models[self.model_selector.get()])
        self.ampl.readData(self.dat)
        for k, v in self.tickbox_vars.items():
            print(k, v.get())
            if v.get() == 1:
                self.ampl.read(self.tickbox_models[k])
        self.ampl.option["solver"] = self.solvers[self.solver_selector.get()]
        before_solve_time = time.time()
        self.ampl.solve()
        print("--- %s seconds ---" % (time.time() - before_solve_time))
        print(self.ampl.getObjective("obj").value())
        print(self.ampl.getVariable("inverted").getValues())

    def create_checkboxes(self, parent):
        for t in self.tickbox_labels:
            self.tickbox_vars[t] = tk.IntVar(value=0)
            self.tickbox_elements[t] = ttk.Checkbutton(parent, text=t, variable=self.tickbox_vars[t])
            self.tickbox_elements[t].pack()

    def init_UI(self):
        """
        Initializes the UI
        """
        g = GridUtil()

        self.title_label = ttk.Label(self, text="Select a model and a solver")
        self.title_label.grid(**pad(), **g.place(cs=3))

        g.next_row()
        self.model_label = ttk.Label(self, text="Model")
        self.model_label.grid(**pad(), **g.place())

        self.model_selector = ttk.Combobox(self, values=[key for key in self.models.keys()])
        self.model_selector.current(0)
        self.model_selector.grid(**pad(), **g.place())

        g.next_row()

        self.solver_label = ttk.Label(self, text="Solver")
        self.solver_label.grid(**pad(), **g.place())

        self.solver_selector = ttk.Combobox(self, values=[key for key in self.solvers.keys()])
        self.solver_selector.current(0)
        self.solver_selector.grid(**pad(), **g.place())

        g.next_row()
        tickbox_frame = ttk.Frame(self)
        tickbox_frame.grid(**pad(), **g.place(cs=3))

        self.create_checkboxes(tickbox_frame)

        g.next_row()

        self.solve_button = ttk.Button(self, text="Solve", command=self.solve)
        self.solve_button.grid(**pad(), **g.place(cs=3))

    def __init__(self, master, entry):
        super().__init__(master)
        self.entry = entry
        self.dat = get_or_generate_dat(entry)
        self.title(f"Pathway {entry}")
        self.init_UI()
        self.mainloop()
