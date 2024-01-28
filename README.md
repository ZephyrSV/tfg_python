# Orientating Biochemical reactions in metabolic pathways and Networks.

This is the repostitory for Zephyr Serret Verbist's bachelor's thesis.  

This study proposes an approach to optimize a solution to the problem of minimizing the number of external vertices in a hypergraph, using the context of **Metabolic Pathways**.

### What's in this repository?

1. An easy to use UI to rapidly orient and visualize pathways from the [KEGG](https://www.kegg.jp/) database. 
2. The thesis' memoir and the source latex for the memoir.  
3. The slides that were used to present the thesis during the presentation.

## Using and setting up our GUI python program :

### Installing the requirements :

#### AMPL

This project revolves around the AMPL model created for the author's TFG (Bachelor's Thesis).

To run this program you will need to sign up and install [AMPL](https://portal.ampl.com/account/ampl/).

#### venv and python dependencies

Creating and activating the venv.

On windows

```bash
python -m venv venv
venv\Scripts\activate.bat
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

### Running the Program

```bash
python3 App.py
```
