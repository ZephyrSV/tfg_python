import os

from Bio.KEGG import REST
from Bio.KEGG.KGML import KGML_parser
import re
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

def download_conf(entry):
    """
    Downloads the conf files associated to the entries, stores them in kgmls/conf/
    in the case they are not already downloaded
    :param entry: the KEGG identifier of the pathway
    :return: the path to the conf file
    """
    if not os.path.exists("kgmls/conf/" + entry + ".conf"):
        print(f"The conf file for entry {entry} is being downloaded...", end="")
        f = open("kgmls/conf/" + entry + ".conf", "w")
        f.write(REST.kegg_get(entry, 'xml').read())
        f.close()
        print("done!")

class Pathway_view(tk.Tk):
    def init_UI(self):
        """
        Initializes the UI
        """
        self.label = ttk.Label(self, text="Pathway View")
        self.label.pack()
        self.canvas = tk.Canvas(self, width=2000, height=2000)
        self.canvas.pack()



    def draw_graphics_object(self, g, circle_x_offset=23, circle_y_offset=8.5, text=None):
        if g.type == "rectangle":
            self.canvas.create_rectangle(
                g.x,
                g.y,
                g.x + g.width,
                g.y + g.height,
                width=1,
                fill="lightgreen",
            )
        elif g.type == "circle":
            self.canvas.create_oval(
                g.x + circle_x_offset,
                g.y + circle_y_offset,
                g.x + g.width + circle_x_offset,
                g.y + g.height + circle_y_offset,
                width=1,
                fill=g.fgcolor)
        if text is not None:
            self.canvas.create_text(
                g.x + g.width / 2,
                g.y + g.height / 2,
                text=text,
                font=("Arial", 8),
                fill="black",
            )


    def draw_pathway(self):
        for reaction in self.kgml.reactions:
            self.draw_graphics_object(reaction.entry.graphics[0], text=reaction.name.replace("rn:", ""))
            for substrate in reaction.substrates:
                self.draw_graphics_object(substrate.graphics[0])
            for product in reaction.products:
                self.draw_graphics_object(product.graphics[0])



    def __init__(self, entry):
        super().__init__()
        self.entry = entry
        self.kgml = get_kgml(entry)
        self.conf = download_conf(entry)
        print(kgml_to_dat(entry, self.kgml))

        self.title(f"Pathway {entry}")


        self.init_UI()
        self.draw_pathway()




if __name__ == "__main__":
    print("Running App.py")
    os.chdir("..")
    app = Pathway_view("hsa00051")
    app.mainloop()
        
