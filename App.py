import tkinter as tk
from tkinter import ttk


class App(tk.Tk):
    def select_pathway_button_click(self):
        selected_option = self.dropdown_var.get()
        self.label.config(text=f'Select pathway: {selected_option}')

    def initialize(self):
        from pathway_getter import get_pathway
        self.human_pathways = get_pathway(organism="hsa")
        self.options = [hp['entry'] for hp in self.human_pathways]
        self.dropdown.config(values=self.options, state='normal')
        self.dropdown_var.set(self.options[0])
    def __init__(self):
        super().__init__()

        self.title("Orienting Biochemical Reactions GUI App")
        self.geometry("500x500")

        self.label = tk.Label(self, text='Select pathway: ')
        self.label.pack(pady=10, side='left')
        self.dropdown_var = tk.StringVar()
        self.dropdown = ttk.Combobox(self, textvariable=self.dropdown_var, state='readonly')
        self.dropdown_var.set("Downloading...")
        self.dropdown.pack(padx=10, pady=10, side='left')
        self.button = tk.Button(self, text='Select', command=self.select_pathway_button_click)
        self.button.pack(padx=10, pady=10, side='left')

if __name__ == '__main__':
    print("Running App.py")
    app = App()
    #wait a second
    
    app.initialize()
    app.mainloop()
