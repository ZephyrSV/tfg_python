import time
import tkinter
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

    def insert_to_treeview(self, entry, obj_value, solve_time):
        self.result_count += 1
        self.treeview.insert("", "end", text=self.result_count, values=(entry, obj_value, solve_time))

    def add_to_dats(self, entry, dat):
        self.dats[entry] = dat

    def prepare_dat(self, entry):
        dat = get_or_generate_dat(entry)
        self.after(0, self.add_to_dats, entry, dat)

    def solve_all_entries(self):
        for entry, dat in self.dats.items():
            self.ampl.option["solver"] = self.solvers[self.solver_selector.get()]
            self.ampl.read(self.models["Nasini's"])
            print(f"Reading dat for {entry} at {dat}")
            self.ampl.readData(dat)
            before_solve_time = time.time()
            self.ampl.solve()
            objective_value = self.ampl.getObjective('obj').value()
            solve_duration = time.time() - before_solve_time
            self.after(0, self.insert_to_treeview, entry, objective_value, solve_duration)


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
        self.start_button = tkinter.Button(self, text="Start benchmark", command=self.start_button_click)
        self.start_button.grid(**g.place(cs=2), **pad())

        g.next_row()
        self.treeview = ttk.Treeview(self, columns=("Entry", "Objective value", "Solve time"))
        self.treeview.heading("Entry", text="Entry")
        self.treeview.heading("Objective value", text="Objective value")
        self.treeview.heading("Solve time", text="Solve time")
        self.treeview.grid(**g.place(cs=2))

        self.verticalScrollbar = ttk.Scrollbar(self, orient="vertical", command=self.treeview.yview)
        self.verticalScrollbar.grid(**g.place(sticky="ns"))


    def __init__(self, entries):
        super().__init__()
        self.executor = concurrent.futures.ThreadPoolExecutor()
        self.title("Benchmark")
        self.entries = entries[:10]
        self.init_UI()
        self.mainloop()
