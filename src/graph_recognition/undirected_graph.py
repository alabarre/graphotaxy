"""
Anthony Labarre © 2024-2026

A minimal implementation of an undirected graph that subclasses the Graph structure from networkx.

"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------

# ----- Third-party imports -----------------------------------------------------------------------
from networkx import Graph, _clear_cache


class UndirectedGraph(Graph):
    """
    Implementation of an undirected graph. This is simply a stripped down version of networkx's
    Graph class, obtained by getting rid of node and edge properties, which will never be needed.
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

    # Note: we would like Graph.number_of_edges and Graph.size to take time O(1), but they take
    # time O(m+n) because len(self.edges) triggers EdgeView.__len__, which reads all edges.
    # A simple solution would be to keep track of the number of edges and nodes in the graph
    # whenever an update occurs, but unfortunately this entails reimplementing many methods. In
    # particular, what to do for methods like subgraph() is not obvious to me.
    # Instead, I provide cached versions of these methods as functions in the misc_algo module.

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
                if x not in self._node:  # noqa (self._node exists in parent class)
                    if x is None:
                        raise ValueError("None cannot be a node")
                    self._adj[x] = self.adjlist_inner_dict_factory()  # noqa (self._adj exists in parent class)
                    self._node[x] = self.node_attr_dict_factory()  # noqa (self._node exists in parent class)

            if v not in self._adj[u]:  # noqa (self._adj exists in parent class)
                datadict = self._adj[u].get(v, self.edge_attr_dict_factory())  # noqa (self._adj exists in parent class)
                self._adj[u][v] = datadict  # noqa (self._adj exists in parent class)
                self._adj[v][u] = datadict  # noqa (self._adj exists in parent class)

        _clear_cache(self)
