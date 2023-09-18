import tkinter as tk
from tkinter import ttk
from pathway_getter import get_pathway

def pad(x=10,y=10):
    return {'padx':x, 'pady':y}
def gridrc(r,c,rs=1,cs=1):
    return {'row':r, 'column':c, 'rowspan':rs, 'columnspan':cs}

class Pathway_selector(tk.Tk):
    def filter_button_click(self):
        self.filter_entry.config(fg='black')
        options = [hp for hp in self.human_pathways if self.filter_entry.get() in hp['description']]
        if len(options) == 0:
            self.filter_entry.config(fg='red')
            return
        self.options = options
        self.dropdown.config(values= [hp['entry'] for hp in self.options])
        self.dropdown_var.set(self.options[0]['entry'])
        self.description_label.config(text=f"Description:\n{self.options[0]['description']}")

    def select_pathway_button_click(self):
        pass

    def on_dropdown_select(self, event):
        i = self.dropdown.current()
        self.description_label.config(text=f"Description:\n{self.human_pathways[i]['description']}")

    def initialize(self):
        self.human_pathways = get_pathway(organism="hsa")
        self.options = self.human_pathways
        self.dropdown.config(state='normal', values=[hp['entry'] for hp in self.options])
        self.dropdown_var.set(self.options[0]['entry'])
        self.description_label.config(text=f"Description:\n{self.options[0]['description']}")

    def __init__(self):
        super().__init__()

        self.title("Orienting Biochemical Reactions GUI App")

        self.filter_entry = tk.Entry(self)
        self.filter_entry.grid(**pad(), **gridrc(0,1))
	
        self.filter_button = tk.Button(self, text='Filter', command=self.filter_button_click)
        self.filter_button.grid(**pad(), **gridrc(0,2))

        self.label = tk.Label(self, text='Select pathway: ')
        self.label.grid(**pad(y=0), **gridrc(1,0))

        self.dropdown_var = tk.StringVar()
        self.dropdown = ttk.Combobox(self, textvariable=self.dropdown_var, state='readonly')
        self.dropdown_var.set("Downloading...")
        self.dropdown.grid(**pad(y=0), **gridrc(1,1))
        self.dropdown.bind("<<ComboboxSelected>>", self.on_dropdown_select)

        self.button = tk.Button(self, text='Select', command=self.select_pathway_button_click)
        self.button.grid(**pad(y=0), **gridrc(1,2))

        self.description_label = tk.Label(self, text='Description:\n', justify='left')
        self.description_label.grid(**pad(), **gridrc(2,0, cs=3))

