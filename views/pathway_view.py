import os

from Bio.KEGG import REST
from Bio.KEGG.KGML import KGML_parser
import tkinter as tk
from tkinter import ttk



def get_kgml(entry):
    if not os.path.exists("kgmls/" + entry + ".kgml"):
        print(f"The kgml file for entry {entry} is being downloaded...", end="")
        f = open("kgmls/" + entry + ".kgml", "w")
        f.write(REST.kegg_get(entry, 'kgml').read())
        f.close()
        print("done!")
    return KGML_parser.parse(open("kgmls/" + entry + ".kgml", "r"))


class Pathway_view(tk.Tk):
    def __init__(self, entry):
        super().__init__()
        self.entry = entry
        self.kgml = next(get_kgml(entry))
        print(type(self.kgml))

        self.title(f"Pathway {entry}")

        self.label = ttk.Label(self, text=f"Pathway {entry}")
        self.label.pack()
        print(self.kgml.image)



if __name__ == "__main__":
    print("Running App.py")
    os.chdir("..")
    app = Pathway_view("hsa00051")
    app.mainloop()
        
