import os

from Bio.KEGG import REST
from Bio.KEGG.KGML import KGML_parser
import tkinter as tk
from tkinter import ttk

from utils.kgml_dat_converter import kgml_to_dat


def get_kgml(entry):
    """
    Fetches and downloads the kgml files associated to the entries, stores them in kgmls/
    :param entry: the KEGG identifier of the pathway
    :rtype: Bio.KEGG.KGML.KGML_pathway.Pathway
    """
    if not os.path.exists("kgmls/" + entry + ".kgml"):
        print(f"The kgml file for entry {entry} is being downloaded...", end="")
        f = open("kgmls/" + entry + ".kgml", "w")
        f.write(REST.kegg_get(entry, 'kgml').read())
        f.close()
        print("done!")
    return next(KGML_parser.parse(open("kgmls/" + entry + ".kgml", "r")))


class Pathway_view(tk.Tk):
    def init_UI(self):
        """
        Initializes the UI
        """
        self.label = ttk.Label(self, text="Pathway View")
        self.label.pack()

    def __init__(self, entry):
        super().__init__()
        self.entry = entry
        self.kgml = get_kgml(entry)
        print(kgml_to_dat(entry, self.kgml))

        self.title(f"Pathway {entry}")


        self.init_UI()




if __name__ == "__main__":
    print("Running App.py")
    os.chdir("..")
    app = Pathway_view("hsa00051")
    app.mainloop()
        
