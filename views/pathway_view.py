import time

from amplpy import AMPL
import tkinter as tk
from tkinter import ttk, filedialog

from utils.DatGenerator import DatGenerator
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
        "Save results to file"
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
            if v.get() == 1 and k in self.tickbox_models:
                self.ampl.read(self.tickbox_models[k])
        self.ampl.option["solver"] = self.solvers[self.solver_selector.get()]
        before_solve_time = time.time()
        self.ampl.solve()

        printers = [print]

        if self.tickbox_vars["Save results to file"].get() == 1:
            file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                     initialdir="./output",
                                                     initialfile=f"{self.model_selector.get()}_{self.solver_selector.get()}_{self.entry}",
                                                     title="Save results to file",
                                                     filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
            if file_path:
                printers.append(self.build_save_to_file_printer(file_path))

        self.print_result(time.time() - before_solve_time, printers=printers)

    def build_save_to_file_printer(self, file_path):
        class Printer:
            def __init__(self, file_path):
                self.file = open(file_path, 'w')

            def __call__(self, *sa, end='\n'):
                for s in sa:
                    self.file.write(s.__str__())
                self.file.write(end)

            def __del__(self):
                self.file.close()
        return Printer(file_path)

    def print_result(self, execution_time, printers=None):
        if printers is None:
            printers = [print]
        for printer in printers:
            printer("###############################################")
            printer("### Computed in %s seconds" % (execution_time))
            printer("### Number of internal vertices ", int(self.ampl.getObjective("internal").value()))
            printer("###############################################")
            printer("")
            printer("### reactionID : [Substrates] -----> [Products]")
            printer("")
            printer("### Reactions that were not inverted")
            query = "for  {i in E: inverted[i] == 0} { " \
                    "printf \"%s: \", i;" \
                    "printf {j in X[i]} \"%s \", j;" \
                    "printf \"-----> \", i;" \
                    "printf {j in Y[i]} \"%s \", j;" \
                    "printf \"\\n\", i;}"
            printer(self.ampl.getOutput(query))
            printer("### Reactions that were inverted")
            query = "for  {i in E: inverted[i] == 1} { " \
                    "printf \"%s: \", i;" \
                    "printf {j in Y[i]} \"%s \", j;" \
                    "printf \"-----> \", i;" \
                    "printf {j in X[i]} \"%s \", j;" \
                    "printf \"\\n\", i;}"
            printer(self.ampl.getOutput(query))


    def create_checkboxes(self, parent):
        for i, t in enumerate(self.tickbox_labels):
            self.tickbox_vars[t] = tk.IntVar(value=0)
            self.tickbox_elements[t] = ttk.Checkbutton(parent, text=t, variable=self.tickbox_vars[t])
            self.tickbox_elements[t].grid(row=i, column=0, sticky=tk.W)

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
        d = DatGenerator()
        self.dat = d.generate_dats([entry])[0][1]
        self.title(f"Pathway {entry}")
        self.init_UI()
        self.mainloop()
