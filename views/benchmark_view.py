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
    ampls = {k: AMPL() for k in models.keys()}  # One ampl instance per model
    dats = {}
    _dats_lock = threading.Lock()
    result_count = 0
    current_test_id = ""

    def insert_to_treeview(self, parent, text, *values):
        self.result_count += 1
        self.treeview.insert(parent, "end", self.result_count.__str__(), text=text, values=tuple(values))

    def get_last_entry_treeview_id(self):
        return self.result_count.__str__()

    def add_to_dats(self, entry, dat):
        with self._dats_lock:
            self.dats[entry] = dat

    def prepare_dat(self, entry):
        dat = get_or_generate_dat(entry)
        self.add_to_dats(entry, dat)

    def solve_all_entries(self):
        solver_id = self.solver_selector.get()
        solver = self.solvers[solver_id]
        for entry, dat in self.dats.items(): # for each entry
            solve_duration_list = []
            for k, ampl in self.ampls.items(): # for each model
                ampl.read(self.models[k])  # prepare ampl instances
                ampl.option["solver"] = solver
                print(f"Reading dat for {entry} at {dat}")
                ampl.readData(dat)
                before_solve_time = time.time()
                text_output = ampl.getOutput("solve;")
                if "Sorry, a demo license" in text_output:
                    solve_duration = "Unavailable using demo license"
                else:
                    solve_duration = (time.time() - before_solve_time).__str__()
                solve_duration_list.append(solve_duration)
            print(solve_duration_list)
            self.after(0, self.insert_to_treeview, self.current_test_id, entry, solver_id, *solve_duration_list)

    def prepare_dats(self):
        """
        Prepares the dats for the benchmark and blocks until all dats are prepared
        :return:
        """
        futures = [self.executor.submit(self.prepare_dat, entry) for entry in self.entries]
        concurrent.futures.wait(futures)

    def run_benchmark(self):
        print(f"Running benchmark with {self.entries.__len__()} entries")
        self.start_button.config(text="Generating dats...", state=tkinter.DISABLED)
        self.prepare_dats()
        self.start_button.config(text="Solving...")
        self.solve_all_entries()
        self.start_button.config(text="Start benchmark", state=tkinter.NORMAL)
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

        self.treeview = ttk.Treeview(self, columns=["Solver"] + list(self.models.keys()))
        self.treeview.heading("Solver", text="Solver")
        for k in self.models.keys():
            self.treeview.heading(k, text=f" {k}'s solve duration")
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
