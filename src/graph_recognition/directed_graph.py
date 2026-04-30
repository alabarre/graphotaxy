"""
Anthony Labarre © 2023-2025

A minimal implementation of a directed graph that subclasses the DiGraph structure from networkx.

"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------

# ----- Third party imports -----------------------------------------------------------------------
import networkx as nx

# ----- My imports --------------------------------------------------------------------------------


# Classes -----------------------------------------------------------------------------------------
class DirectedGraph(nx.DiGraph):
    """
    Implementation of a directed graph. This is simply a stripped down version of networkx's
    DiGraph class, obtained by getting rid of node and edge properties, which will never be needed.
    """
    # we don't need edge attributes, so we remove them as in the example at
    # https://networkx.org/documentation/stable/reference/classes/digraph.html
    all_edge_dict = dict()

    def single_edge_dict(self) -> dict:
        """

        @return:
        """
        return self.all_edge_dict

    edge_attr_dict_factory = single_edge_dict

    def __init__(self, incoming_graph_data=None, **attr):
        """
        Initializes the DirectedGraph.
        """
        super().__init__(incoming_graph_data, **attr)