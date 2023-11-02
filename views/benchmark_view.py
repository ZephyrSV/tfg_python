import time
import tkinter
import concurrent.futures
from utils.ui_utils import GridUtil

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
    results_text = ""

    @print_thread_name
    def append_to_results(self, text):
        self.results_text += text + "\n"
        self.results_label["text"] = self.results_text

    @print_thread_name
    def run_benchmark(self, entry):
        time.sleep(0.1)
        self.after(0, self.append_to_results, "Starting benchmark for " + entry)


    @print_thread_name
    def start_button_click(self):
        """
        Starts the benchmark
        """
        print(self.solvers[self.solver_selector.get()])
        print(self.entries)
        print("Starting benchmark")
        self.append_to_results("Starting benchmark")
        for entry in self.entries:
            self.executor.submit(self.run_benchmark, entry)


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
