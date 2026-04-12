"""
Anthony Labarre © 2024-2026

A minimal implementation of an undirected graph that subclasses the Graph structure from networkx.

"""
from time import perf_counter
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
from typing import Hashable

# ----- Third-party imports -----------------------------------------------------------------------
from networkx import Graph, _clear_cache


class UndirectedGraph(Graph):
    """
    Implementation of an undirected graph. This is simply a stripped down version of networkx's
    Graph class, obtained by getting rid of node and edge properties, which will never be needed.

    Additionally, number_of_edges() and size() run in time O(1) instead of O(m+n).
    """
    def __init__(self, incoming_graph_data=None, **attr):
        self._num_edges = 0
        super().__init__(incoming_graph_data, **attr)

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
    # TODO: these are not, in fact, O(1), but O(m+n): len(self.edges) triggers EdgeView.__len__,
    #  which is reads all edges, so we need to redefine a field ourselves and keep it updated
    #  what to do about subgraphs???
    def number_of_edges(self, u: Hashable = None, v: Hashable = None) -> int:
        """
        Returns the number of edges in the graph. If neither u nor v are None, returns the number
        of edges between those vertices instead.

        :param u:
        :param v:
        :return:
        """
        #print(f"self._num_edges = {self._num_edges}, len(self.edges) = {len(self.edges)}")
        '''
        start = perf_counter()
        x = len(self.edges)
        end = perf_counter()
        print(f"computing len(self.edges) took {end-start} seconds")
        '''
        return len(self.edges) if u is None else int(self.has_edge(u, v))

    def size(self, weight: str = None) -> int:
        """
        Returns the number of edges in the graph.

        :param weight:
        :return:
        """
        # note: it would have been nice to just do:
        return len(self.edges)
        # unfortunately, while this returns the correct result, it entails iterating over an
        # EdgeView because of the way EdgeView.__len__ is implemented. So we keep track of the
        # number of edges in a variable instead, and return its value immediately
        # TODO implement that; this means that we have to reimplement all functions that add
        #   or remove edges from graph

    def to_undirected_class(self):
        """
        Returns the class to use for empty undirected copies.

        If you subclass the base classes, use this to designate what directed class to use for 
        `to_directed()` copies.
        """
        return UndirectedGraph


    def add_edges_from(self, ebunch_to_add, **attr):
        """
        Add all the edges in ebunch_to_add.

        :param ebunch_to_add:
        :param attr:
        :return:
        """
        for u, v, *_ in ebunch_to_add:
            for x in (u, v):
                if x not in self._node:
                    if x is None:
                        raise ValueError("None cannot be a node")
                    self._adj[x] = self.adjlist_inner_dict_factory()
                    self._node[x] = self.node_attr_dict_factory()

            if v not in self._adj[u]:
                datadict = self._adj[u].get(v, self.edge_attr_dict_factory())
                self._adj[u][v] = datadict
                self._adj[v][u] = datadict
                self._num_edges += 1

        _clear_cache(self)
