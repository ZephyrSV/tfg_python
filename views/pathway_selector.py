import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
import requests
from io import BytesIO

from utils.KEGGIntegration import KEGGIntegration
from views.pathway_view import PathwayView
from views.benchmark_view import Benchmark_view
from utils.ui_utils import *
import concurrent.futures



class Pathway_selector(tk.Tk):
    default_filter_text = "Search by description..."

    def filter_enter_action(self, event=None):
        """
        This function is called when enter is pressed in the filter box.

        The filter Entry is used to filter the search_pool in the dropdown based on their respective description.
        """
        self.filter_entry.config(fg='black')
        search_pool = {entry: desc for entry, desc in self.kegg_integration.pathway_descriptions.items() if self.filter_entry.get().upper() in desc.upper()}
        if len(search_pool) == 0:
            self.filter_entry.config(fg='red')
            return
        self.search_pool = search_pool
        self.dropdown_set_values()

    def dropdown_enter_action(self, event=None):
        """
        This function is called when enter is pressed in the dropdown.

        The dropdown is used to select the pathway to be viewed.
        """
        search_pool = {entry: desc for entry, desc in self.kegg_integration.pathway_descriptions.items() if self.dropdown_var.get().upper() in desc.upper()}
        if len(search_pool) == 0:
            self.dropdown.config(foreground="red")
            return
        self.dropdown.config(foreground="black")
        self.search_pool = search_pool
        self.dropdown_set_values()

    def dropdown_id_enter_action(self, event=None):
        """
        This function is called when enter is pressed in the dropdown.

        The dropdown is used to select the pathway to be viewed.
        """
        search_pool = {entry: desc for entry, desc in self.kegg_integration.pathway_descriptions.items() if self.dropdown_var_id.get().upper() in entry.upper()}
        if len(search_pool) == 0:
            self.dropdown_id.config(foreground="red")
            return
        self.dropdown_id.config(foreground="black")
        self.search_pool = search_pool
        self.dropdown_set_values()

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
        url = f"http://rest.kegg.jp/get/{self.dropdown_var_id.get()}/image"
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
        PathwayView(self, self.dropdown_var_id.get())

    def benchmark_button_click(self):
        """
        **Opens a new window with the selected pathway.**

        This function is called when the benchmark button is clicked.
        """
        Benchmark_view(master=self)


    def on_dropdown_select(self, event=None):
        """
        This function is called when an option is selected in the dropdown for descriptions.

        Updates the description label with the description of the selected pathway.
        """
        reversed_search_pool = {desc: entry for entry, desc in self.search_pool.items()}
        self.dropdown_var_id.set(reversed_search_pool[self.dropdown.get()])

    def on_dropdown_id_select(self, event=None):
        """
        This function is called when an option is selected in the dropdown for ids.

        Updates the description label with the description of the selected pathway.
        """
        self.dropdown_var.set(self.search_pool[self.dropdown_id.get()])

    def clear_description_label(self, event=None):
        """
        Clears the description label.
        """
        self.description_label.config(text="")
        self.description_label.update()

    def set_description_label_func(self, text):
        """
        Returns a function that sets the description label to the given text.
        """
        def set_description_label(event=None):
            self.description_label.config(text=text)
            self.description_label.update()
        return set_description_label

    def dropdown_set_values(self):
        """
        Sets the values of the dropdown.
        """

        values = sorted(list(self.search_pool.keys()))
        max_length = len(max(values, key=len))
        self.dropdown_id.config(values=values, width=max_length+5)
        self.dropdown_var_id.set(values[0])

        values = sorted(list(self.search_pool.values()))
        max_length = len(max(values, key=len))
        self.dropdown.config(values=values, width=max_length+5)
        self.dropdown_var.set(self.search_pool[self.dropdown_id.get()])



    def __init__(self):
        super().__init__()
        self.kegg_integration = KEGGIntegration()
        self.executor = concurrent.futures.ThreadPoolExecutor()
        g = GridUtil()


        self.title("Orienting Biochemical Reactions")
        self.resizable(False, False)

        self.label = tk.Label(self, text='Select pathway: ', font=("Arial", 12, "bold", "underline"))
        self.label.grid(**pad(), **g.place())

        self.dropdown_var_id = tk.StringVar()
        self.dropdown_id = ttk.Combobox(self, textvariable=self.dropdown_var_id, state='readonly')
        self.dropdown_var_id.set('Downloading...')
        self.dropdown_id.grid(**pad(y=0), **g.place())
        self.dropdown_id.bind("<<ComboboxSelected>>", self.on_dropdown_id_select)
        self.dropdown_id.bind("<Return>", self.dropdown_id_enter_action)
        self.dropdown_id.bind("<Enter>", self.set_description_label_func(
            "Select a pathway. You can also search for one by typing its pathway id and pressing enter."))
        self.dropdown_id.bind("<Leave>", self.clear_description_label)

        self.dropdown_var = tk.StringVar()
        self.dropdown = ttk.Combobox(self, textvariable=self.dropdown_var, state='readonly')
        self.dropdown_var.set("Downloading...")
        self.dropdown.grid(**pad(y=0), **g.place())
        self.dropdown.bind("<<ComboboxSelected>>", self.on_dropdown_select)
        self.dropdown.bind("<Return>", self.dropdown_enter_action)
        self.dropdown.bind("<Enter>", self.set_description_label_func(
            "Select a pathway. You can also search for one by typing its name and pressing enter."))
        self.dropdown.bind("<Leave>", self.clear_description_label)



        self.show_img_button = tk.Button(self, text='Show Image', command=self.show_image_button_click)
        self.show_img_button.grid(**pad(y=0),**g.place())
        self.show_img_button.bind("<Enter>", self.set_description_label_func(
            "Show the image of the selected pathway. This may take a while. (Requires internet connection)"))
        self.show_img_button.bind("<Leave>", self.clear_description_label)

        self.select_button = tk.Button(self, text='Select 🡕', command=self.select_pathway_button_click)
        self.select_button.grid(**pad(y=0), **g.place())
        self.select_button.bind("<Enter>", self.set_description_label_func(
            "Open the pathway window of the selected pathway."))
        self.select_button.bind("<Leave>", self.clear_description_label)

        g.next_row()
        self.description_label = tk.Label(self, foreground="gray")
        self.description_label.grid(**pad(y=0), **g.place(cs=4))

        self.benchmark_button = tk.Button(self, text='Benchmark 🡕', command=self.benchmark_button_click)
        self.benchmark_button.grid(**pad(y=0), **g.place())
        self.benchmark_button.bind("<Enter>", self.set_description_label_func(
            "Open the benchmark window."))
        self.benchmark_button.bind("<Leave>", self.clear_description_label)



        g.next_row()
        self.image_label = tk.Label(self)
        self.image_label.grid(**pad(), **g.place(cs=4))

        self.human_pathways = self.kegg_integration.pathway_descriptions
        self.search_pool = self.human_pathways
        self.dropdown_id.config(state='normal')
        self.dropdown.config(state='normal')
        self.dropdown_set_values()

        self.bind("<Configure>", g.generate_on_resize())



