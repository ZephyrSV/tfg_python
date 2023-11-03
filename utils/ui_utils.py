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


class GridUtil:
    current_row = 0
    current_column = 0

    def __init__(self, row=0, column=0):
        self.current_row = row
        self.current_column = column

    def set_row(self, row):
        self.current_row = row
        return self.current_row

    def set_column(self, column):
        self.current_column = column
        return self.current_column

    def next_row(self):
        self.current_row += 1
        self.current_column = 0
        return self.current_row

    def place(self, rs=1, cs=1, sticky="we"):
        """
        Returns a dictionary with the grid parameters to use for tkinter widgets
        Advances the current column by cs
        :param rs: row span
        :param cs: column span
        :return: {'row': self.current_row, 'column': self.current_column, 'rowspan': rs, 'columnspan': cs}
        """
        result = {
            'row': self.current_row,
            'column': self.current_column,
            'rowspan': rs,
            'columnspan': cs,
            'sticky': sticky
        }
        self.current_column += cs
        return result
