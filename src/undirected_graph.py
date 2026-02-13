"""
Anthony Labarre © 2024-2025

A minimal implementation of an undirected graph that subclasses the Graph structure from networkx.

"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
from typing import Hashable

# ----- Third-party imports -----------------------------------------------------------------------
from networkx import Graph


class UndirectedGraph(Graph):
    """
    Implementation of an undirected graph. This is simply a stripped down version of networkx's
    Graph class, obtained by getting rid of node and edge properties, which will never be needed.

    Additionally, number_of_edges() and size() run in time O(1) instead of O(m+n).
    """

    # we don't need edge attributes, so we remove them as in the example at
    # https://networkx.org/documentation/stable/reference/classes/graph.html
    all_edge_dict = dict()

    def single_edge_dict(self) -> dict:
        """

        @return:
        """
        return self.all_edge_dict

    edge_attr_dict_factory = single_edge_dict

    # likewise, we don't need node attributes either:
    all_node_dict = dict()

    def single_node_dict(self) -> dict:
        """

        @return:
        """
        return self.all_node_dict

    node_attr_dict_factory = single_node_dict

    # Graph.number_of_edges and Graph.size take time O(m+n); we reimplement them to have them call
    # len on the iterable of edges instead, which takes time O(1)
    def number_of_edges(self, u: Hashable = None, v: Hashable = None) -> int:
        return len(self.edges) if u is None else int(self.has_edge(u, v))

    def size(self, weight=None) -> int:
        return len(self.edges)
