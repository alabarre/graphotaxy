"""
Anthony Labarre © 2024-2026

A minimal implementation of an undirected graph that subclasses the Graph structure from networkx.

"""
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


    # TODO trying to reimplement add_edges_from in the hope that it becomes faster
    def add_edges_from(self, ebunch_to_add, **attr):
        """
        Add all the edges in ebunch_to_add.

        Parameters
        ----------
        ebunch_to_add : container of edges
            Each edge given in the container will be added to the
            graph. The edges must be given as 2-tuples (u, v) or
            3-tuples (u, v, d) where d is a dictionary containing edge data.
        attr : keyword arguments, optional
            Edge data (or labels or objects) can be assigned using
            keyword arguments.

        See Also
        --------
        add_edge : add a single edge
        add_weighted_edges_from : convenient way to add weighted edges

        Notes
        -----
        Adding the same edge twice has no effect but any edge data
        will be updated when each duplicate edge is added.

        Edge attributes specified in an ebunch take precedence over
        attributes specified via keyword arguments.

        When adding edges from an iterator over the graph you are changing,
        a `RuntimeError` can be raised with message:
        `RuntimeError: dictionary changed size during iteration`. This
        happens when the graph's underlying dictionary is modified during
        iteration. To avoid this error, evaluate the iterator into a separate
        object, e.g. by using `list(iterator_of_edges)`, and pass this
        object to `G.add_edges_from`.

        Examples
        --------
        >>> G = UndirectedGraph()  # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G.add_edges_from([(0, 1), (1, 2)])  # using a list of edge tuples
        >>> e = zip(range(0, 3), range(1, 4))
        >>> G.add_edges_from(e)  # Add the path graph 0-1-2-3

        Associate data to edges

        >>> G.add_edges_from([(1, 2), (2, 3)], weight=3)
        >>> G.add_edges_from([(3, 4), (1, 4)], label="WN2898")

        Evaluate an iterator over a graph if using it to modify the same graph

        >>> G = UndirectedGraph([(1, 2), (2, 3), (3, 4)])
        >>> # Grow graph by one new node, adding edges to all existing nodes.
        >>> # wrong way - will raise RuntimeError
        >>> # G.add_edges_from(((5, n) for n in G.nodes))
        >>> # correct way - note that there will be no self-edge for node 5
        >>> G.add_edges_from(list((5, n) for n in G.nodes))
        """
        for u, v, *_ in ebunch_to_add:
            for x in (u, v):
                if x not in self._node:
                    if x is None:
                        raise ValueError("None cannot be a node")
                    self._adj[x] = self.adjlist_inner_dict_factory()
                    self._node[x] = self.node_attr_dict_factory()

            datadict = self._adj[u].get(v, self.edge_attr_dict_factory())
            self._adj[u][v] = datadict
            self._adj[v][u] = datadict

        _clear_cache(self)
