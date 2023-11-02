import time
import tkinter

from utils.ui_utils import GridUtil


class Benchmark_view(tkinter.Tk):
    solvers = {
        "CPLEX": "cplex",
        "Gurobi": "gurobi",
        "cbc": "cbc",
    }
    def append_to_results(self, text):
        """
        Appends text to the results label
        """
        self.results_label.config(text=self.results_label.cget("text") + "\n" + text)

    def start_benchmark(self):
        """
        Starts the benchmark
        """
        print(self.solvers[self.solver_selector.get()])
        print(self.entries)
        print("Starting benchmark")
        for entry in self.entries:
            self.append_to_results("Starting benchmark for " + entry)
            time.sleep(1)


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
        self.start_button = tkinter.Button(self, text="Start benchmark", command=self.start_benchmark)
        self.start_button.grid(**g.place(cs=2))

        g.next_row()
        self.results_label = tkinter.Label(self, text="Results")
        self.results_label.grid(**g.place(cs=2))




    def __init__(self, entries):
        super().__init__()
        self.title("Benchmark")
        self.entries = entries[:10]
        self.init_UI()
