import time
import tkinter
import concurrent.futures

from amplpy import AMPL

from utils.kgml_dat_converter import get_or_generate_dat
from utils.ui_utils import GridUtil

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

    def append_to_results(self, text):
        self.results_text += text + "\n"
        self.results_label["text"] = self.results_text

    def add_to_dats(self, entry, dat):
        self.dats[entry] = dat

    def prepare_dat(self, entry):
        dat = get_or_generate_dat(entry)
        self.after(0, self.add_to_dats, entry, dat)

    def solve_all_entries(self):
        for entry, dat in self.dats.items():
            self.ampl.option["solver"] = self.solvers[self.solver_selector.get()]
            self.ampl.read(self.models["Nasini's"])
            self.ampl.readData(dat)
            before_solve_time = time.time()
            self.ampl.solve()
            self.append_to_results(f"{entry} - {self.ampl.getObjective('obj').value()} - {time.time() - before_solve_time}")



    @print_thread_name
    def prepare_dats(self):
        """
        Prepares the dats for the benchmark and blocks until all dats are prepared
        :return:
        """
        futures = [self.executor.submit(self.prepare_dat, entry) for entry in self.entries]
        print("Waiting for futures to finish")
        concurrent.futures.wait(futures)
        print("Futures finished")

    def run_benchmark(self):
        self.prepare_dats()
        self.solve_all_entries()



    def start_button_click(self):
        """
        Starts the benchmark
        """
        self.executor.submit(self.run_benchmark)
        print("main thread is not blocked")


    def init_UI(self):
        """
        Initializes the UI
        """
        g = GridUtil()
        self.select_solver_label = tkinter.Label(self, text="Select a solver")
        self.select_solver_label.grid(**g.place())
        self.solver_selector = tkinter.ttk.Combobox(self, values=[key for key in self.solvers.keys()])
        self.solver_selector.grid(**g.place())
        self.solver_selector.current(0)

        g.next_row()
        self.start_button = tkinter.Button(self, text="Start benchmark", command=self.start_button_click)
        self.start_button.grid(**g.place(cs=2))

        g.next_row()
        self.results_label = tkinter.Label(self, text="Results")
        self.results_label.grid(**g.place(cs=2))




    def __init__(self, entries):
        super().__init__()
        self.executor = concurrent.futures.ThreadPoolExecutor()
        self.title("Benchmark")
        self.entries = entries[:10]
        self.init_UI()
        self.mainloop()
