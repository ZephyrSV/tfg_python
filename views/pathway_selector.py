import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
import requests
from io import BytesIO
from utils.pathway_getter import fetch_all_pathways
from views.pathway_view import PathwayView
from views.benchmark_view import Benchmark_view
from utils.ui_utils import *
import concurrent.futures



class Pathway_selector(tk.Tk):
    default_filter_text = "Search by description..."

    def filter_enter_action(self, event=None):
        """
        This function is called when enter is pressed in the filter box.

        The filter Entry is used to filter the options in the dropdown based on their respective description.
        """
        self.filter_entry.config(fg='black')
        options = [hp for hp in self.human_pathways if self.filter_entry.get() in hp['description']]
        if len(options) == 0:
            self.filter_entry.config(fg='red')
            return
        self.options = options
        self.dropdown_set_values()
        self.description_label.config(text=f"Description:\n{self.options[0]['description']}")

    def on_entry_filter_click(self, event):
        """
        Called when the filter entry is clicked.

        Serves to clear the default text in the filter entry when clicked.
        """
        if self.filter_entry.get() == self.default_filter_text:
            self.filter_entry.delete(0, "end")  # Clear the default text when clicked
        self.filter_entry.config(fg="black")  # Change the text color to black

    def on_entry_filter_leave(self, event):
        """
        Called when the filter entry looses the focus.

        Serves to add the default text in the filter entry if nothing is entered.
        """
        if self.filter_entry.get() == "":
            self.filter_entry.insert(0, self.default_filter_text)  # Add the default text if nothing entered
            self.filter_entry.config(fg="gray")  # Change the text color to gray

    def set_image(self):
        """
        Sets the image in the image_label to the selected pathway.
        """
        i = self.dropdown.current()
        url = f"http://rest.kegg.jp/get/{self.options[i]['entry']}/image"
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        img.thumbnail((1000, 1000), Image.LANCZOS)
        img = ImageTk.PhotoImage(img)
        self.image_label.config(image=img)
        self.image_label.image = img
        self.show_img_button.config(state="normal")

    def show_image_button_click(self):
        self.image_label.config(text="Loading image...")
        self.image_label.image = None
        self.show_img_button.config(state="disabled")
        self.executor.submit(self.set_image)

    def select_pathway_button_click(self):
        """
        **Opens a new window with the selected pathway.**


        This function is called when the select pathway button is clicked.
        """
        PathwayView(self, self.options[self.dropdown.current()]['entry'])

    def benchmark_button_click(self):
        """
        **Opens a new window with the selected pathway.**

        This function is called when the benchmark button is clicked.
        """
        Benchmark_view(self, [x['entry'] for x in self.options])


    def on_dropdown_select(self, event):
        """
        This function is called when an option is selected in the dropdown for descriptions.

        Updates the description label with the description of the selected pathway.
        """
        self.description_label.config(text=f"Description:\n{self.options[self.dropdown.current()]['description']}")
        self.dropdown_var_id.set(self.options[self.dropdown.current()]['entry'])

    def on_dropdown_id_select(self, event):
        """
        This function is called when an option is selected in the dropdown for ids.

        Updates the description label with the description of the selected pathway.
        """
        self.description_label.config(text=f"Description:\n{self.options[self.dropdown_id.current()]['description']}")
        self.dropdown_var.set(self.options[self.dropdown_id.current()]['description'])

    def dropdown_set_values(self):
        """
        Sets the values of the dropdown.
        """
        values = [hp['entry'] for hp in self.options]
        max_length = len(max(values, key=len))
        self.dropdown_id.config(values=values, width=max_length+5)
        self.dropdown_var_id.set(values[0])
        values = [hp['description'] for hp in self.options]
        max_length = len(max(values, key=len))
        self.dropdown.config(values=values, width=max_length+5)
        self.dropdown_var.set(values[0])


    def initialize(self):
        """
        Initializes the window.
        :todo: remove this function and call the functions directly
        :return:
        """
        self.human_pathways = fetch_all_pathways(organism="hsa")
        self.options = self.human_pathways
        self.dropdown_id.config(state='normal')
        self.dropdown.config(state='normal')
        self.dropdown_set_values()
        self.description_label.config(text=f"Description:\n{self.options[0]['description']}")

    def __init__(self):
        super().__init__()
        self.executor = concurrent.futures.ThreadPoolExecutor()
        g = GridUtil()

        self.title("Orienting Biochemical Reactions")
        self.resizable(False, False)

        g.set_column(2)

        self.filter_entry = tk.Entry(self)
        self.filter_entry.insert(0, self.default_filter_text)
        self.filter_entry.config(fg="gray")
        self.filter_entry.bind("<FocusIn>", self.on_entry_filter_click)
        self.filter_entry.bind("<FocusOut>", self.on_entry_filter_leave)
        self.filter_entry.bind("<Return>", self.filter_enter_action)
        self.filter_entry.grid(**pad(), **g.place())

        self.filter_button = tk.Button(self, text='Filter', command=self.filter_enter_action)
        self.filter_button.grid(**pad(y=0), **g.place())

        g.next_row()

        self.label = tk.Label(self, text='Select pathway: ', font=("Arial", 12, "bold", "underline"))
        self.label.grid(**pad(), **g.place())

        self.dropdown_var_id = tk.StringVar()
        self.dropdown_id = ttk.Combobox(self, textvariable=self.dropdown_var_id, state='readonly')
        self.dropdown_var_id.set('Downloading...')
        self.dropdown_id.grid(**pad(y=0), **g.place())
        self.dropdown_id.bind("<<ComboboxSelected>>", self.on_dropdown_id_select)

        self.dropdown_var = tk.StringVar()
        self.dropdown = ttk.Combobox(self, textvariable=self.dropdown_var, state='readonly')
        self.dropdown_var.set("Downloading...")
        self.dropdown.grid(**pad(y=0), **g.place())
        self.dropdown.bind("<<ComboboxSelected>>", self.on_dropdown_select)

        self.show_img_button = tk.Button(self, text='Show Image', command=self.show_image_button_click)
        self.show_img_button.grid(**pad(y=0),**g.place())

        self.select_button = tk.Button(self, text='Select 🡕', command=self.select_pathway_button_click)
        self.select_button.grid(**pad(y=0), **g.place())

        g.next_row()
        g.set_column(3)
        self.benchmark_button = tk.Button(self, text='Benchmark 🡕', command=self.benchmark_button_click)
        self.benchmark_button.grid(**pad(y=0), **g.place())

        g.next_row()
        self.description_label = tk.Label(self, text='Description:\n', justify='left', anchor='w')
        self.description_label.grid(**pad(), **g.place(cs=4))

        g.next_row()
        self.image_label = tk.Label(self)
        self.image_label.grid(**pad(), **g.place(cs=4))



