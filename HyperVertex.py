class HyperVertex:
    """ HyperVertex class

    Attributes:
        data: the data of the vertex (unique among all vertices)
        edges_head: the edges that have this vertex as head
        edges_tail: the edges that have this vertex as tail
    """
    def __init__(self, data):
        self.data = data
        self.edges_head = []
        self.edges_tail = []

    def add_edge_head(self, edge):
        self.edges_head.append(edge)

    def add_edge_tail(self, edge):
        self.edges_tail.append(edge)

    def __str__(self):
        return str(self.data)

    def __eq__(self, other):
        return self.data == other.data

    def __hash__(self):
        return hash(self.data)

    def __repr__(self):
        return str(self)

    def __lt__(self, other):
        return self.data < other.data
