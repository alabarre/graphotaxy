"""
Anthony Labarre © 2024-2026

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
    # TODO these implementations should form a PR for networkx too ...
    def number_of_edges(self, u: Hashable = None, v: Hashable = None) -> int:
        """
        Returns the number of edges in the graph. If neither u nor v are None, returns the number
        of edges between those vertices instead.

        :param u:
        :param v:
        :return:
        """
        return len(self.edges) if u is None else int(self.has_edge(u, v))

    def size(self, weight: str = None) -> int:
        """
        Returns the number of edges in the graph.

        :param weight:
        :return:
        """
        return len(self.edges)

    def to_undirected_class(self):
        """
        Returns the class to use for empty undirected copies.

        If you subclass the base classes, use this to designate what directed class to use for 
        `to_directed()` copies.
        """
        return UndirectedGraph
