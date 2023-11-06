import time
import tkinter
from datetime import datetime
from tkinter import ttk
import concurrent.futures

from amplpy import AMPL

from utils.kgml_dat_converter import get_or_generate_dat
from utils.ui_utils import GridUtil, pad

import threading

def print_thread_name(func):
    def wrapper(*args, **kwargs):
        current_thread = threading.current_thread()
        print(f"Thread name: {current_thread.name}, Function name: {func.__name__}")
        return func(*args, **kwargs)
    return wrapper


class Benchmark_view(tkinter.Tk):
    ampl = AMPL()
    solvers = {
        "CPLEX": "cplex",
        "Gurobi": "gurobi",
        "cbc": "cbc",
    }
    models = {
        "My model": "AMPL/models/my_model.mod",
        "My model 2": "AMPL/models/my_model2.mod",
        "Nasini's": "AMPL/models/nasini.mod",
        "Valiente": "AMPL/models/valiente.mod"
    }
    results_text = ""
    dats = {}
    result_count = 0
    current_test_id = ""

    def insert_to_treeview(self, parent, *values):
        self.result_count += 1
        self.treeview.insert(parent, "end", self.result_count.__str__(), values=tuple(values))

    def get_last_entry_treeview_id(self):
        return self.result_count.__str__()

    def add_to_dats(self, entry, dat):
        self.dats[entry] = dat

    def prepare_dat(self, entry):
        dat = get_or_generate_dat(entry)
        self.after(0, self.add_to_dats, entry, dat)

    def solve_all_entries(self):
        for entry, dat in self.dats.items():
            solver_id = self.solver_selector.get()
            self.ampl.option["solver"] = self.solvers[solver_id]
            model_id = self.model_selector.get()
            self.ampl.read(self.models[model_id])
            print(f"Reading dat for {entry} at {dat}")
            self.ampl.readData(dat)
            before_solve_time = time.time()
            text_output = self.ampl.getOutput("solve;")
            if "Sorry, a demo license" in text_output:
                objective_value = "Unavailable using demo license"
                solve_duration = "NA"
            else:
                objective_value = self.ampl.getObjective('obj').value()
                solve_duration = time.time() - before_solve_time
            self.after(0, self.insert_to_treeview, self.current_test_id, entry, solver_id, model_id, objective_value, solve_duration)


    def prepare_dats(self):
        """
        Prepares the dats for the benchmark and blocks until all dats are prepared
        :return:
        """
        futures = [self.executor.submit(self.prepare_dat, entry) for entry in self.entries]
        concurrent.futures.wait(futures)


    def run_benchmark(self):
        self.start_button.config(text="Generating dats...", state=tkinter.DISABLED)
        self.prepare_dats()
        self.start_button.config(text="Solving...")
        self.solve_all_entries()
        self.start_button.config(text="Start benchmark", state=tkinter.NORMAL)

    def start_button_click(self):
        """
        Starts the benchmark
        """
        now = datetime.now()
        self.insert_to_treeview(
            "",                                         # parent
            now.strftime("Benchmark %d/%m/%Y %H:%M"),   # entry name
            self.solver_selector.get(),                 # solver
            self.model_selector.get(),                  # model
            "",                                         # objective value
            ""                                          # solve duration
        )
        self.current_test_id = self.get_last_entry_treeview_id()
        self.executor.submit(self.run_benchmark)


    def init_UI(self):
        """
        Initializes the UI
        """
        g = GridUtil()
        self.select_solver_label = tkinter.Label(self, text="Select a solver")
        self.select_solver_label.grid(**g.place(), **pad())
        self.solver_selector = tkinter.ttk.Combobox(self, values=[key for key in self.solvers.keys()])
        self.solver_selector.grid(**g.place(), **pad())
        self.solver_selector.current(0)

        g.next_row()
        self.select_model_label = tkinter.Label(self, text="Select a model")
        self.select_model_label.grid(**g.place(), **pad())
        self.model_selector = tkinter.ttk.Combobox(self, values=[key for key in self.models.keys()])
        self.model_selector.grid(**g.place(), **pad())
        self.model_selector.current(0)

        g.next_row()
        self.start_button = tkinter.Button(self, text="Start benchmark", command=self.start_button_click)
        self.start_button.grid(**g.place(cs=2), **pad())

        g.next_row()
        self.treeview = ttk.Treeview(self, columns=("Entry", "Solver", "Model", "Objective value", "Solve time"))
        self.treeview.heading("Entry", text="Entry")
        self.treeview.heading("Solver", text="Solver")
        self.treeview.heading("Model", text="Model")
        self.treeview.heading("Objective value", text="Objective value")
        self.treeview.heading("Solve time", text="Solve time (ms)")
        self.treeview.grid(**g.place(cs=2, sticky="nsew"))

        self.verticalScrollbar = ttk.Scrollbar(self, orient="vertical", command=self.treeview.yview)
        self.verticalScrollbar.grid(**g.place(sticky="ns"))
        self.treeview.configure(yscrollcommand=self.verticalScrollbar.set)

        self.grid_rowconfigure(g.current_row, weight=1)
        self.grid_columnconfigure(g.current_row, weight=1)

    def __init__(self, entries):
        super().__init__()
        self.executor = concurrent.futures.ThreadPoolExecutor()
        self.title("Benchmark")
        self.entries = entries[:10]
        self.init_UI()
        self.mainloop()
