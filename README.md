# Orientating Biochemical pathways.

A easy to use UI to rapidly orient and visualize pathways from the KEGG database.

Select a pathway based on its id or description.

Select constraints and solve the optimization problem and visualize/save the results.

## Installing the requirements

### AMPL

This project revolves around the AMPL model created for the author's TFG (Bachelor's Thesis).

To run this program you will need to sign up and install [AMPL](https://portal.ampl.com/account/ampl/).

### venv and python dependencies

Creating and activating the venv.

On windows

```bash
python -m venv venv
venv\Scripts\activate
```

On Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

Your terminal should look like this

```
(venv) tfg_python>
```

Then install the depencies

```bash
pip install -r requirements.txt
```

