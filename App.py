import os
if os.path.isdir(r"/opt/ampl/"):
    from amplpy import add_to_path
    add_to_path(r"/opt/ampl/")
from views.pathway_selector import Pathway_selector


if __name__ == '__main__':
    print("Running App.py")
    app = Pathway_selector()
    app.mainloop()
