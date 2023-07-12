from Bio.KEGG import REST


def kgml_download(entries):
    """ Fetches and downloads the kgml files associated to the entries, stores them in kgmls/

    Parameters
    ---------
    entries : str, list(str)
        the KEGG identifier(s) of the pathway(s)
    """
    # ensure that entries is a list
    entries = entries if isinstance(entries, list) else [entries]

    for entry in entries:
        f = open("kgmls/" + entry + ".kgml", "w")
        f.write(REST.kegg_get(entry, 'kgml').read())
        f.close()


kgml_download("hsa01100")
