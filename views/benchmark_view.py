import os
import time
import tkinter
from datetime import datetime
import tkinter as tk
from tkinter import ttk
import concurrent.futures
import numpy as np

from amplpy import AMPL

from utils.KEGGIntegration import KEGGIntegration
from utils.ui_utils import GridUtil, pad

import threading



class Benchmark_view(tk.Toplevel):
    solvers = {
        "cbc (free)": "cbc",
        "CPLEX (requires licence for big models)": "cplex",
        "Gurobi (requires licence for big models)": "gurobi",
    }
    models = {
        "Serret old": "AMPL/models/serret_old.mod",
        "Serret DualImply": "AMPL/models/serret_dual_imply.mod",
        "Serret UniImply": "AMPL/models/serret_uni_imply.mod",
        "Model A": "AMPL/models/model_A.mod", # Nasini
        "Model B": "AMPL/models/model_B.mod", # Valiente
    }
    dats = {}
    _dats_lock = threading.Lock()
    result_count = 0
    current_test_id = ""
    file = None

    def insert_to_treeview(self, parent, text, *values):
        self.result_count += 1
        self.treeview.insert(parent, "end", self.result_count.__str__(), text=text, values=tuple(values))

    def get_last_entry_treeview_id(self):
        return self.result_count.__str__()

    def add_to_dats(self, entry, dat):
        with self._dats_lock:
            self.dats[entry] = dat

    def set_benchmark_average(self, entry, solver_id, valid_duration_lists):
        print(f"Setting benchmark average of {len(valid_duration_lists)} entries with solver {solver_id}")
        self.treeview.item(entry, values=[solver_id] + list(np.average(valid_duration_lists, axis=0)))


    def solve_all_entries(self):
        solver_id = self.solver_selector.get()
        solver = self.solvers[solver_id]
        valid_duration_lists = []
        for entry, dat in self.dats.items():  # for each entry
            solve_duration_list = []
            is_valid = True
            for model_path in self.models.values():  # for each model
                ampl = AMPL()
                ampl.read(model_path)  # prepare ampl instances
                ampl.option["solver"] = solver
                print(f"Reading dat for {entry} at {dat}")
                ampl.readData(dat)
                before_solve_time = time.time()
                text_output = ampl.getOutput("solve;")
                if "Sorry, a demo license" in text_output:
                    solve_duration = "Unavailable using demo license"
                    is_valid = False
                else:
                    solve_duration = (time.time() - before_solve_time)
                solve_duration_list.append(solve_duration)
            if is_valid:
                valid_duration_lists.append(solve_duration_list)
            self.after(0, self.insert_to_treeview, self.current_test_id, entry, solver_id, *solve_duration_list)
            solve_duration_list_str = '\t'.join(map(lambda x: x.__str__(), solve_duration_list))
            self.file.write(f"{entry}\t{solver_id}\t{solve_duration_list_str}\n")
        self.after(0, self.set_benchmark_average, self.current_test_id, solver_id, valid_duration_lists)

    def prepare_dats(self):
        """
        Prepares the dats for the benchmark and blocks until all dats are prepared
        :return:
        """

        for entry, dat in self.kegg_integration.generate_dats(self.entries):
            self.add_to_dats(entry, dat)

    def run_benchmark(self):
        print(f"Running benchmark with {self.entries.__len__()} entries")
        if not os.path.isdir("output"):
            os.mkdir("output")
        self.file = open(f"output/benchmark_{datetime.now().strftime('%d_%m_%Y_%H_%M')}.txt", "w")
        models_names_for_file = '\t'.join(map(lambda x: x+"'s solve duration", self.models.keys()))
        self.file.write(f"entry\tsolver\t{models_names_for_file}\n")
        self.start_button.config(text="Generating dats...", state=tkinter.DISABLED)
        self.prepare_dats()
        self.start_button.config(text="Solving...")
        self.solve_all_entries()
        self.start_button.config(text="Start benchmark", state=tkinter.NORMAL)
        self.file.close()
        print("Benchmark finished")

    def start_button_click(self):
        """
        Starts the benchmark
        """
        now = datetime.now()
        self.insert_to_treeview(
            "",  # parent
            now.strftime("Benchmark %d/%m/%Y %H:%M"),  # entry name
            self.solver_selector.get(),  # solver
        )
        self.current_test_id = self.get_last_entry_treeview_id()
        print(f"Current test id: {self.current_test_id}")
        threading.Thread(target=self.run_benchmark).start()

    def create_tickboxes(self, parent):
        self.tickbox_var_UseInstalledBenchmarkData = tk.IntVar(value=0)
        self.tickbox_UseInstalledBenchmarkData = ttk.Checkbutton(
            parent,
            text="Use Installed Benchmark Data (Recommended)",
            variable=self.tickbox_var_UseInstalledBenchmarkData)
        self.tickbox_UseInstalledBenchmarkData.pack()
        pass

    def __init__(self, master):
        super().__init__(master)
        self.kegg_integration = KEGGIntegration()
        self.executor = concurrent.futures.ThreadPoolExecutor()
        self.title("Benchmark")
        self.entries = list(self.kegg_integration.map_pathway_id_to_description.keys())[:25]
        g = GridUtil()
        g.do_not_resize_row()

        self.select_solver_label = tkinter.Label(self, text="Select a solver")
        self.select_solver_label.grid(**g.place(sticky="nsew"), **pad())
        self.solver_selector = tkinter.ttk.Combobox(self, values=[key for key in self.solvers.keys()], state="readonly")
        self.solver_selector.grid(**g.place(sticky="nsew"), **pad())
        self.solver_selector.current(0)

        g.next_row()
        g.do_not_resize_row()
        self.start_button = tkinter.Button(self, text="Start benchmark", command=self.start_button_click)
        self.start_button.grid(**g.place(cs=2, sticky="nsew"), **pad())

        g.next_row()
        self.treeview = ttk.Treeview(self, columns=["Solver"] + list(self.models.keys()))
        self.treeview.heading("Solver", text="Solver")
        for k in self.models.keys():
            self.treeview.heading(k, text=f"{k}'s solve duration")
        self.treeview.grid(**g.place(cs=2, sticky="nsew"))
        self.verticalScrollbar = ttk.Scrollbar(self, orient="vertical", command=self.treeview.yview)
        g.do_not_resize_col()
        self.verticalScrollbar.grid(**g.place(sticky="nsew"))
        self.treeview.configure(yscrollcommand=self.verticalScrollbar.set)

        self.bind("<Configure>", g.generate_on_resize())
        self.focus_set()
        try:
            self.mainloop()
        except KeyboardInterrupt:
            print("Interrupted by user")
            self.destroy()
            exit(0)


