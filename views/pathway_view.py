import time

from amplpy import AMPL
import tkinter as tk
from tkinter import ttk, filedialog
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from utils.DatGenerator import DatGenerator
from utils.functional_programming import lmap
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
        self.ampl = AMPL()
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

        self.get_ampl_variables()
        self.print_result(time.time() - before_solve_time, printers=printers)
        self.draw_canvas_frame()

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
            printer("### reactionID : [Substrates] : [Products]")
            uninverted_reactions = [r for r in self.X.keys() if self.inverted[r] == 0]
            inverted_reactions = [r for r in self.X.keys() if self.inverted[r] != 0]
            printer("")
            printer("### Reactions that were not inverted")
            for r in uninverted_reactions:
                printer(f"{r} : {' '.join(self.X[r])} : {' '.join(self.Y[r])}")
            printer("### Reactions that were inverted")
            for r in inverted_reactions:
                printer(f"{r} : {' '.join(self.Y[r])} : {' '.join(self.X[r])}")


    def get_ampl_variables(self):
        def _and(i1, i2):
            if i1 == 1 and i2 == 1:
                return 1
            return 0

        variables = dict(self.ampl.get_variables())
        sets = dict(self.ampl.get_sets())

        self.inverted = variables["inverted"].getValues().toDict()

        if "is_internal" in variables.keys():
            self.internal = variables["is_internal"].getValues().toDict()
        else:
            has_outgoint = variables["has_outgoing"].getValues().toDict()
            has_incoming = variables["has_incoming"].getValues().toDict()
            self.internal = {k: _and(has_outgoint[k], has_incoming[k]) for k in has_outgoint.keys()}

        self.X = {r_id: x.getValues().toList() for (r_id, x) in self.ampl.getSet("X").instances()}
        self.Y = {r_id: x.getValues().toList() for (r_id, x) in self.ampl.getSet("Y").instances()}
        self.reactions = self.ampl.getSet("E").getValues().toList()
        self.compounds = self.ampl.getSet("V").getValues().toList()

    def draw_canvas_frame(self):
        canvas_frame = ttk.Frame(self)
        canvas_frame.grid(**pad(), row=0, column=3, rowspan=5)
        G = nx.Graph()
        G.add_nodes_from(self.reactions)
        G.add_nodes_from(self.compounds)
        external = [c for c in self.compounds if self.internal[c] == 0]
        internal = [c for c in self.compounds if self.internal[c] != 0]
        uninverted_reactions = [r for r in self.X.keys() if self.inverted[r] == 0]
        inverted_reactions = [r for r in self.X.keys() if self.inverted[r] != 0]

        uninverted_edges = \
            [(c, r) for r in uninverted_reactions for c in self.X[r]] + \
            [(r, c) for r in uninverted_reactions for c in self.Y[r]]
        inverted_edges =  \
            [(c, r) for r in inverted_reactions for c in self.Y[r]] + \
            [(r, c) for r in inverted_reactions for c in self.X[r]]
        edges = uninverted_edges + inverted_edges
        G.add_edges_from(edges)

        fig, ax = plt.subplots()
        pos = nx.spring_layout(G)
        add_yoffset = lambda pos, o: {k: (v[0], v[1] + o) for (k, v) in pos.items()}
        nx.draw_networkx_nodes(G, pos, nodelist=self.reactions, node_color='grey', node_size=20, alpha=0.8, node_shape='s')
        nx.draw_networkx_nodes(G, pos, nodelist=internal, node_color='g', node_size=20, alpha=0.8)
        nx.draw_networkx_nodes(G, pos, nodelist=external, node_color='r', node_size=20, alpha=0.8)
        nx.draw_networkx_edges(G, pos, edgelist=uninverted_edges, width=1.0, alpha=0.5, arrows=True, arrowsize=10, arrowstyle='->')
        nx.draw_networkx_edges(G, pos, edgelist=inverted_edges, edge_color='b', width=1.0, alpha=0.5, arrows=True, arrowsize=10, arrowstyle='->')
        nx.draw_networkx_labels(G, add_yoffset(pos, 0.05), font_size=8)

        ax.plot([],[], color='grey', label='Reactions', linestyle='', marker='o', markersize=5, alpha=0.8)
        ax.plot([],[], color='g', label='Internal compounds', linestyle='', marker='o', markersize=5, alpha=0.8)
        ax.plot([],[], color='r', label='External compounds', linestyle='', marker='o', markersize=5, alpha=0.8)
        ax.plot([],[], color='b', label='Inverted reactions', markersize=5, alpha=0.8)
        ax.axis('off')
        ax.legend(loc='best', prop={'size': 8})


        canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
        canvas_widget = canvas.get_tk_widget()
        NavigationToolbar2Tk(canvas, canvas_frame)
        canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)





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

    def __init__(self, master, entry, mainloop=True):
        super().__init__(master)
        self.entry = entry
        d = DatGenerator()
        self.dat = d.generate_dats([entry])[0][1]
        self.title(f"{entry}")
        self.init_UI()
        if mainloop:
            self.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = PathwayView(master=root, entry="hsa00010", mainloop=False)
    app.after(0,app.solve)
    app.mainloop()
