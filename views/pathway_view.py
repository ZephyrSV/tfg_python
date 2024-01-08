import time

from amplpy import AMPL
import tkinter as tk
from tkinter import ttk, filedialog
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from utils.KEGGIntegration import KEGGIntegration
from utils.ui_utils import pad, GridUtil


class PathwayView(tk.Toplevel):
    ampl = AMPL()
    solvers = {
        "cbc (free)": "cbc",
        "CPLEX (requires licence for big models)": "cplex",
        "Gurobi (requires licence for big models)": "gurobi",
    }
    save_result_to_file_var = None
    save_result_to_file = None
    visualize_result_var = None
    visualize_result = None
    Use_extra_restrictions_var = None
    Use_extra_restrictions = None
    solve_5s_count = 0

    def five_secs_after_solve(self):
        self.solve_5s_count -= 1
        if self.solve_5s_count == 0:
            self.solved_label.config(text="")

    def solve(self):
        """
        Solves the pathway
        """
        self.ampl = AMPL()
        model = "AMPL/models/"
        model += "zephyr_dual_imply_extra_restrictions.mod" if self.use_extra_restrictions_var.get() else "model_A.mod"
        print("model: ", model)
        self.ampl.read(model)
        self.ampl.readData(self.dat)
        print("solver: ", self.solvers[self.solver_selector.get()])
        self.ampl.option["solver"] = self.solvers[self.solver_selector.get()]
        before_solve_time = time.time()
        self.ampl.solve()

        printers = [print]

        if self.save_result_to_file_var.get():
            file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                     initialdir="./output",
                                                     initialfile=f"{self.model_selector.get()}_{self.solver_selector.get()}_{self.entry}",
                                                     title="Save results to file",
                                                     filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
            if file_path:
                printers.append(self.build_save_to_file_printer(file_path))

        self.get_ampl_variables()
        self.print_result(time.time() - before_solve_time, printers=printers)
        if self.visualize_result_var.get():
            self.draw_canvas_frame()
        self.solved_label.config(text="Solved! Check console for results.")
        self.solve_5s_count += 1
        self.after(5000, self.five_secs_after_solve)

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
        if hasattr(self, "canvas_frame"):
            self.canvas_frame.destroy()
        self.canvas_frame = ttk.Frame(self)
        self.canvas_frame.grid(**pad(), rowspan=6, column=2, row=0, sticky=tk.NSEW)

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
        inverted_edges = \
            [(c, r) for r in inverted_reactions for c in self.Y[r]] + \
            [(r, c) for r in inverted_reactions for c in self.X[r]]
        edges = uninverted_edges + inverted_edges
        G.add_edges_from(edges)

        fig, ax = plt.subplots()
        pos = nx.spring_layout(G)
        add_yoffset = lambda pos, o: {k: (v[0], v[1] + o) for (k, v) in pos.items()}
        nx.draw_networkx_nodes(G, pos, nodelist=self.reactions, node_color='grey', node_size=20, alpha=0.8,
                               node_shape='s')
        nx.draw_networkx_nodes(G, pos, nodelist=internal, node_color='g', node_size=20, alpha=0.8)
        nx.draw_networkx_nodes(G, pos, nodelist=external, node_color='r', node_size=20, alpha=0.8)
        nx.draw_networkx_edges(G, pos, edgelist=uninverted_edges, width=1.0, alpha=0.5, arrows=True, arrowsize=10,
                               arrowstyle='->')
        nx.draw_networkx_edges(G, pos, edgelist=inverted_edges, edge_color='b', width=1.0, alpha=0.5, arrows=True,
                               arrowsize=10, arrowstyle='->')
        nx.draw_networkx_labels(G, add_yoffset(pos, 0.05), font_size=8)

        ax.plot([], [], color='grey', label='Reactions', linestyle='', marker='o', markersize=5, alpha=0.8)
        ax.plot([], [], color='g', label='Internal compounds', linestyle='', marker='o', markersize=5, alpha=0.8)
        ax.plot([], [], color='r', label='External compounds', linestyle='', marker='o', markersize=5, alpha=0.8)
        ax.plot([], [], color='b', label='Inverted reactions', markersize=5, alpha=0.8)
        ax.axis('off')
        ax.legend(loc='best', prop={'size': 8})

        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        canvas_widget = canvas.get_tk_widget()
        NavigationToolbar2Tk(canvas, self.canvas_frame)
        canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.resizable(True, True)

    def hide_show_extra_restrictions(self):
        if not self.use_extra_restrictions_var.get():
            self.extra_restrictions_frame.grid_remove()
        else:
            self.extra_restrictions_frame.grid(row=self.extra_restrictions_frame_row, columnspan=2, sticky=tk.W)

    def get_data_from_dat(self):
        with open(self.dat, "r") as f:
            for line in f.readlines():
                if line.startswith("set E :="):
                    line = line.replace("set E :=", "").strip()
                    self.reactions = line[:-1].split(" ")
                elif line.startswith("set V :="):
                    line = line.replace("set V :=", "").strip()
                    self.compounds = line[:-1].split(" ")
                elif line.startswith("set uninvertibles :="):
                    line = line.replace("set uninvertibles :=", "").strip()
                    self.uninvertibles = sorted(filter(lambda x: x != '', line[:-1].split(" ")))
                elif line.startswith("set forced_externals :="):
                    line = line.replace("set forced_externals :=", "").strip()
                    self.forced_externals = sorted(filter(lambda x: x != '', line[:-1].split(" ")))
                elif line.startswith("set forced_internals :="):
                    line = line.replace("set forced_internals :=", "").strip()
                    self.forced_internals = sorted(filter(lambda x: x != '', line[:-1].split(" ")))

    def rewrite_extra_restrictions_in_dat(self):
        with open(self.dat, "r") as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if line.startswith("set uninvertibles :="):
                    lines[i] = "set uninvertibles := " + " ".join(self.uninvertibles) + ";\n"
                elif line.startswith("set forced_externals :="):
                    lines[i] = "set forced_externals := " + " ".join(self.forced_externals) + ";\n"
                elif line.startswith("set forced_internals :="):
                    lines[i] = "set forced_internals := " + " ".join(self.forced_internals) + ";\n"
        with open(self.dat, "w") as f:
            f.writelines(lines)

    class ExtraRestrictionsModifier:
        def __init__(self, outer, my_list, g: GridUtil, parent, to_add_from):
            self.outer = outer
            self.my_list = my_list
            self.g = g
            self.parent = parent
            self.to_add_from = to_add_from

            self.dropdown = None
            self.add_button = None
            self.remove_button = None

        def init_ui(self):
            self.dropdown = ttk.Combobox(self.parent, values=self.my_list, state="readonly")
            self.dropdown.grid(**pad(y=(0, 10)), **self.g.place(sticky=tk.W))

            self.remove_button = ttk.Button(self.parent, text="Remove", command=self.remove)
            self.remove_button.grid(**pad(y=(0, 10), x=(0, 10)), **self.g.place(sticky=tk.W))

            seperator = ttk.Separator(self.parent, orient=tk.VERTICAL)
            seperator.grid(**pad(y=(0, 10)), **self.g.place(sticky=tk.NSEW))

            self.add_button = ttk.Button(self.parent, text="Add 🡕", command=self.add)
            self.add_button.grid(**pad(y=(0, 10)), **self.g.place(sticky=tk.W))
            self.reset_dropdown()

        def reset_dropdown(self):
            self.dropdown["values"] = self.my_list
            if len(self.my_list) > 0:
                self.dropdown.current(0)
                self.remove_button.config(state="enabled")
            else:
                self.dropdown.set("")
                self.remove_button.config(state="disabled")

        def remove(self):
            self.my_list.remove(self.dropdown.get())
            self.reset_dropdown()
            self.outer.rewrite_extra_restrictions_in_dat()

        def add(self):
            g = GridUtil()
            pop_up = tk.Toplevel(self.parent)
            pop_up.title("")
            pop_up.focus_set()
            label = ttk.Label(pop_up, text="Select elements to add to the list")
            label.grid(**pad(), **g.place(sticky=tk.NSEW, cs=2))

            g.next_row()

            listbox = tk.Listbox(pop_up, selectmode=tk.MULTIPLE)
            listbox.grid(**pad(x=(10, 0)), **g.place(sticky=tk.NSEW))
            for item in [item for item in self.to_add_from if item not in self.my_list]:
                listbox.insert(tk.END, item)

            scrollbar = ttk.Scrollbar(pop_up, orient=tk.VERTICAL, command=listbox.yview)
            scrollbar.grid(**pad(x=(0, 10)), **g.place(sticky=tk.NSEW))
            listbox.config(yscrollcommand=scrollbar.set)
            def add_from_listbox():
                for i in listbox.curselection():
                    self.my_list.append(listbox.get(i))
                self.reset_dropdown()
                self.outer.rewrite_extra_restrictions_in_dat()
                pop_up.destroy()

            g.next_row()
            ttk.Button(pop_up, text="Add", command=add_from_listbox).grid(**pad(), **g.place(cs=2, sticky=tk.NSEW))

    def create_extra_restrictions_frame(self, parent):
        g = GridUtil()
        self.extra_restrictions_label = ttk.Label(parent, text="Extra restrictions :",
                                                  font=("TkDefaultFont", 12, "bold"))
        self.extra_restrictions_label.grid(**pad(), **g.place(sticky=tk.W, cs=4))
        g.next_row()
        ############################################################
        self.uninvertibles_label = ttk.Label(parent, text="Prevent inversion of the reactions :")
        self.uninvertibles_label.grid(**pad(y=0), **g.place(sticky=tk.W, cs=4))

        g.next_row()
        self.uninvertibles_modifier = self.ExtraRestrictionsModifier(
            self,
            self.uninvertibles,
            g,
            parent,
            self.reactions,
        )
        self.uninvertibles_modifier.init_ui()
        ############################################################
        g.next_row()
        self.forced_externals_label = ttk.Label(parent, text="Mark these compounds as external :")
        self.forced_externals_label.grid(**pad(y=0), **g.place(sticky=tk.W, cs=4))

        g.next_row()
        self.forced_externals_modifier = self.ExtraRestrictionsModifier(
            self,
            self.forced_externals,
            g,
            parent,
            self.compounds,
        )
        self.forced_externals_modifier.init_ui()
        ############################################################
        g.next_row()
        self.forced_internals_label = ttk.Label(parent, text="Mark these compounds as internal :")
        self.forced_internals_label.grid(**pad(y=0), **g.place(sticky=tk.W, cs=4))

        g.next_row()
        self.forced_internals_modifier = self.ExtraRestrictionsModifier(
            self,
            self.forced_internals,
            g,
            parent,
            self.compounds,
        )
        self.forced_internals_modifier.init_ui()

    def create_tickboxes(self, parent):
        g = GridUtil()
        self.save_result_to_file_var = tk.IntVar(value=0)
        self.save_result_to_file = ttk.Checkbutton(parent, text="Save result to file",
                                                   variable=self.save_result_to_file_var)
        self.save_result_to_file.grid(**pad(y=0), **g.place(sticky=tk.W))

        self.visualize_result_var = tk.IntVar(value=0)
        self.visualize_result = ttk.Checkbutton(parent, text="Visualize result", variable=self.visualize_result_var)
        self.visualize_result.grid(**pad(y=0), **g.place(sticky=tk.W))
        g.next_row()

        self.use_extra_restrictions_var = tk.BooleanVar(value=False)
        self.use_extra_restrictions = ttk.Checkbutton(parent, text="Use extra restrictions",
                                                      variable=self.use_extra_restrictions_var)
        self.use_extra_restrictions.grid(**pad(y=0), **g.place(sticky=tk.W))
        self.use_extra_restrictions_var.trace("w", lambda *args: self.hide_show_extra_restrictions())

    def __init__(self, master, entry, mainloop=True):
        super().__init__(master)
        self.entry = entry
        d = KEGGIntegration()
        self.dat = d.generate_dats([entry])[0][1]
        self.get_data_from_dat()
        self.title("Solver and Visualizer")
        ####
        # The UI
        ####
        g = GridUtil()

        self.title_label = ttk.Label(self, text=f"Solving the {self.entry} pathway:", font=("Arial", 12, "bold", "underline"))
        self.title_label.grid(**pad(), **g.place(cs=2))

        g.next_row()
        g.do_not_resize_col()
        self.solver_label = ttk.Label(self, text="Solver")
        self.solver_label.grid(**pad(), **g.place())

        g.do_not_resize_col()
        self.solver_selector = ttk.Combobox(self, values=[key for key in self.solvers.keys()])
        max_length = len(max(self.solvers.keys(), key=len))
        self.solver_selector.config(width=max_length)
        self.solver_selector.current(0)
        self.solver_selector.grid(**pad(), **g.place())

        g.next_row()
        self.tickbox_frame = ttk.Frame(self)
        self.tickbox_frame.grid(**pad(), **g.place(cs=2))

        self.create_tickboxes(self.tickbox_frame)

        g.next_row()
        self.extra_restrictions_frame = ttk.Frame(self, borderwidth=2, relief=tk.GROOVE)
        self.extra_restrictions_frame_row = g.current_row
        self.extra_restrictions_frame.grid(**pad(y=0), **g.place(cs=2))

        self.create_extra_restrictions_frame(self.extra_restrictions_frame)
        self.hide_show_extra_restrictions()

        g.next_row()

        self.solved_label = ttk.Label(self, text="", foreground="green")
        self.solved_label.grid(**pad(y=0), **g.place(cs=2))

        g.next_row()

        self.solve_button = ttk.Button(self, text="Solve", command=self.solve)
        self.solve_button.grid(**pad(), **g.place(cs=2))

        self.bind("<Configure>", g.generate_on_resize())
        self.resizable(False, False)
        self.focus_set()

        if mainloop:
            try:
                self.mainloop()
            except KeyboardInterrupt:
                print("Interrupted by user")
                self.destroy()
                raise KeyboardInterrupt
                exit(0)


if __name__ == "__main__":
    root = tk.Tk()
    app = PathwayView(master=root, entry="hsa00010", mainloop=False)
    app.after(0, app.solve)
    app.mainloop()
