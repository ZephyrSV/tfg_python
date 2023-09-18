import tkinter as tk
from tkinter import ttk
from pathway_getter import get_pathway

def pad(x=10,y=10):
    return {'padx':x, 'pady':y}
def gridrc(r,c,rs=1,cs=1):
    return {'row':r, 'column':c, 'rowspan':rs, 'columnspan':cs}

class Pathway_selector(tk.Tk):
    def select_pathway_button_click(self):
        i = self.dropdown.current()
        self.description_label.config(text=f"Description:\n{self.human_pathways[i]['description']}")

    def initialize(self):
        self.human_pathways = get_pathway(organism="hsa")
        self.options = [hp['entry'] for hp in self.human_pathways]
        self.dropdown.config(values=self.options, state='normal')
        self.dropdown_var.set(self.options[0])
    def __init__(self):
        super().__init__()

        self.title("Orienting Biochemical Reactions GUI App")

        self.label = tk.Label(self, text='Select pathway: ')
        self.label.grid(**pad(), **gridrc(0,0))

        self.dropdown_var = tk.StringVar()
        self.dropdown = ttk.Combobox(self, textvariable=self.dropdown_var, state='readonly')
        self.dropdown_var.set("Downloading...")
        self.dropdown.grid(**pad(), **gridrc(0,1))

        self.button = tk.Button(self, text='Select', command=self.select_pathway_button_click)
        self.button.grid(**pad(), **gridrc(0,2))

        self.description_label = tk.Label(self, text='Description:\n', anchor='e')
        self.description_label.grid(**pad(), **gridrc(1,0, cs=3))

