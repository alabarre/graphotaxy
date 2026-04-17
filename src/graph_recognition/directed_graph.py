"""
Anthony Labarre © 2023-2025

A minimal implementation of a directed graph that subclasses the DiGraph structure from networkx.

"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
from typing import Set

# ----- Third party imports -----------------------------------------------------------------------
import networkx as nx

# ----- My imports --------------------------------------------------------------------------------
from isgci.isgci_base import reduced_isgci_inclusion_graph
from isgci.vars import OPEN, HARD, EASY


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

    def __init__(self) -> None:
        """
        Initializes the DirectedGraph. Its value defaults to the whole, simplified ISGCI
        graph class inclusion graph, albeit without directed graph classes.
        """
        super().__init__()  # TODO check signature
