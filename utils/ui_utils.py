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
