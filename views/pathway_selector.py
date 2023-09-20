import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
import requests
from io import BytesIO
from pathway_getter import get_pathway
from views.pathway_view import Pathway_view


def pad(x=10, y=10):
    """
    Returns a dictionary with the padding parameters to use for tkinter widgets
    :param x: padx
    :param y: pady
    :return: {'padx': x, 'pady': y}
    """
    return {'padx': x, 'pady': y}


def gridrc(r, c, rs=1, cs=1):
    """
    Returns a dictionary with the grid parameters to use for tkinter widgets

    Stands for grid row column.
    :param r: row
    :param c: column
    :param rs: rowspan
    :param cs: columnspan
    :return: {'row': r, 'column': c, 'rowspan': rs, 'columnspan': cs}
    """
    return {'row': r, 'column': c, 'rowspan': rs, 'columnspan': cs}


class Pathway_selector(tk.Tk):
    def filter_button_click(self):
        """
        This function is called when the filter button is clicked.

        The filter Entry is used to filter the options in the dropdown based on their respective description.
        """
        self.filter_entry.config(fg='black')
        options = [hp for hp in self.human_pathways if self.filter_entry.get() in hp['description']]
        if len(options) == 0:
            self.filter_entry.config(fg='red')
            return
        self.options = options
        self.dropdown.config(values=[hp['entry'] for hp in self.options])
        self.dropdown_var.set(self.options[0]['entry'])
        self.description_label.config(text=f"Description:\n{self.options[0]['description']}")

    def on_entry_filter_click(self, event):
        """
        Called when the filter entry is clicked.

        Serves to clear the default text in the filter entry when clicked.
        """
        if self.filter_entry.get() == "Enter filter here":
            self.filter_entry.delete(0, "end")  # Clear the default text when clicked
        self.filter_entry.config(fg="black")  # Change the text color to black

    def on_entry_filter_leave(self, event):
        """
        Called when the filter entry looses the focus.

        Serves to add the default text in the filter entry if nothing is entered.
        """
        if self.filter_entry.get() == "":
            self.filter_entry.insert(0, "Enter filter here")  # Add the default text if nothing entered
            self.filter_entry.config(fg="gray")  # Change the text color to gray

    def set_image(self):
        """
        Sets the image in the image_label to the selected pathway.
        """
        i = self.dropdown.current()
        self.image_label.config(text="Loading image...")
        self.image_label.image = None
        url = f"http://rest.kegg.jp/get/{self.options[i]['entry']}/image"
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        img.thumbnail((1000, 1000), Image.LANCZOS)
        img = ImageTk.PhotoImage(img)
        self.image_label.config(image=img)
        self.image_label.image = img

    def select_pathway_button_click(self):
        """
        **Opens a new window with the selected pathway.**


        This function is called when the select pathway button is clicked.
        """
        Pathway_view(self.options[self.dropdown.current()]['entry'])

    def on_dropdown_select(self, event):
        """
        This function is called when an option is selected in the dropdown.

        Updates the description label with the description of the selected pathway.
        """
        i = self.dropdown.current()
        self.description_label.config(text=f"Description:\n{self.human_pathways[i]['description']}")

    def initialize(self):
        """
        Initializes the window.
        :todo: remove this function and call the functions directly
        :return:
        """
        self.human_pathways = get_pathway(organism="hsa")
        self.options = self.human_pathways
        self.dropdown.config(state='normal', values=[hp['entry'] for hp in self.options])
        self.dropdown_var.set(self.options[0]['entry'])
        self.description_label.config(text=f"Description:\n{self.options[0]['description']}")

    def __init__(self):
        super().__init__()

        self.title("Orienting Biochemical Reactions")
        self.resizable(False, False)

        row = 0 ### First row ###

        self.filter_entry = tk.Entry(self)
        self.filter_entry.insert(0, "Enter filter here")
        self.filter_entry.config(fg="gray")
        self.filter_entry.bind("<FocusIn>", self.on_entry_filter_click)
        self.filter_entry.bind("<FocusOut>", self.on_entry_filter_leave)
        self.filter_entry.grid(**pad(), **gridrc(row, 1))

        self.filter_button = tk.Button(self, text='Filter', command=self.filter_button_click)
        self.filter_button.grid(**pad(), **gridrc(row, 2))

        row += 1 ### Second row ###
        self.label = tk.Label(self, text='Select pathway: ', font=("Arial", 12, "bold", "underline"))
        self.label.grid(**pad(), **gridrc(row, 0))

        self.dropdown_var = tk.StringVar()
        self.dropdown = ttk.Combobox(self, textvariable=self.dropdown_var, state='readonly')
        self.dropdown_var.set("Downloading...")
        self.dropdown.grid(**pad(y=0), **gridrc(row, 1))
        self.dropdown.bind("<<ComboboxSelected>>", self.on_dropdown_select)

        self.show_img_button = tk.Button(self, text='Show preview', command=self.set_image)
        self.show_img_button.grid(**pad(y=0), **gridrc(row, 2))

        self.select_button = tk.Button(self, text='Select', command=self.select_pathway_button_click)
        self.select_button.grid(**pad(y=0), **gridrc(row, 3))

        row += 1  ### Third row ###
        self.description_label = tk.Label(self, text='Description:\n', justify='left', anchor='w')
        self.description_label.grid(**pad(), **gridrc(row, 0, cs=4))

        row += 1  ### Fourth row ###
        self.image_label = tk.Label(self)
        self.image_label.grid(**pad(), **gridrc(row, 0, cs=4))

