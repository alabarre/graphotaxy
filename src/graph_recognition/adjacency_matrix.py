"""
Anthony Labarre © 2026

Bitarray-based half-adjacency matrix representation of an undirected, unweighted graph.

This is the bare minimum for being compatible with the algorithms I need to run (mine or
networkx's).

"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
from itertools import combinations
from typing import Iterable, Hashable, Self

# ----- Third-party imports -----------------------------------------------------------------------
from bidict import bidict
from bitarray import bitarray
from tqdm import tqdm


class HalfAdjacencyMatrix:
    """
    Implementation of an undirected, unweighted graph as a half-adjacency matrix: only the lower
    triangle (including the diagonal to allow loops) is stored as a list of bitarrays.

    Nodes can be of any hashable type. Loops are supported, parallel edges are ignored.
    """

    def __init__(self) -> None:
        """
        Initializes the relevant data structures.
        """
        self.node_mapping = bidict()
        self.num_nodes = 0
        self.adj_mat = []

    # Node-related methods ------------------------------------------------------------------------
    def add_nodes_from(self, nbunch: Iterable) -> None:
        """
        Adds all nodes from nbunch to the graph.

        :param nbunch:
        :return:
        """
        for node in nbunch:
            self.node_mapping[node] = self.num_nodes  # map node to identifier
            self.num_nodes += 1
            self.adj_mat.append(bitarray(self.num_nodes))  # add row to adjacency matrix

    def degree(self):
        """
        Returns a pairing of all nodes to their degree.

        :return:
        """
        for node, node_id in self.node_mapping.items():
            # as in the neighbors function, the degree of a vertex is the sum of 1's in its row
            # plus the number of rows after node's row that have a 1 in its column
            yield node, sum(self.adj_mat[node_id]) + sum(
                self.adj_mat[row_idx][node_id] for row_idx in range(node_id + 1, self.num_nodes)
            )

    def neighbors(self, v: Hashable):
        """
        Returns the neighbors of vertex v.

        >>> G = HalfAdjacencyMatrix()
        >>> G.add_edge("bla", "blou")
        >>> set(G.neighbors("bla"))
        {'blou'}

        :param v:
        :return:
        """
        # since we only store the lower triangle of the adjacency matrix, the neighbors of a
        # vertex v are 1) the column indices with a True value in v's row, and 2) the row
        # indices with a True value in v's column for rows located after v's row

        # gather neighbors of type 1)
        v_id = self.node_mapping[v]
        for pos, val in enumerate(self.adj_mat[v_id]):
            if val:
                yield self.node_mapping.inverse[pos]

        # gather neighbors of type 2)
        for row_idx in range(v_id + 1, self.num_nodes):
            if self.adj_mat[row_idx][v_id]:
                yield self.node_mapping.inverse[row_idx]

    def non_neighbors(self, v: Hashable):
        """
        Returns the non-neighbors of vertex v (except v itself).

        :param v:
        :return:
        """
        # since we only store the lower triangle of the adjacency matrix, the non-neighbors of a
        # vertex v are 1) the column indices with a False value in v's row, and 2) the row
        # indices with a False value in v's column for rows located after v's row

        # gather neighbors of type 1)
        v_id = self.node_mapping[v]
        for pos, val in enumerate(self.adj_mat[v_id][:-1]):
            if not val:
                yield self.node_mapping.inverse[pos]

        # gather neighbors of type 2)
        for row_idx in range(v_id + 1, self.num_nodes):
            if not self.adj_mat[row_idx][v_id]:
                yield self.node_mapping.inverse[row_idx]

    def number_of_nodes(self) -> int:
        """
        Returns the number of nodes in the graph.

        :return:
        """
        return self.num_nodes

    def __iter__(self):
        """
        Allows iterating over the graph's nodes (i.e.: "for node in graph")

        :return:
        """
        for node in self.node_mapping:
            yield node

    def __getitem__(self, v: Hashable):
        """
        Allows access to v's neighbors with brackets (i.e.: graph[v]).

        >>> G = HalfAdjacencyMatrix()
        >>> G.add_edges_from([("a", "b"), ("b", "c")])
        >>> sorted(G["b"])
        ['a', 'c']

        :param v:
        :return:
        """
        for w in self.neighbors(v):
            yield w

    def __len__(self):
        """
        Returns the number of nodes in the graph.

        :return:
        """
        return self.num_nodes

    # Edge-related methods ------------------------------------------------------------------------
    def add_edge(self, u: Hashable, v: Hashable) -> None:
        """
        Adds an edge between vertices u and v, adding missing nodes along the way. No error is
        raised if edge already exists.

        :param u:
        :param v:
        :return:
        """
        for node in (u, v):
            if node not in self.node_mapping:
                self.add_nodes_from([node])

        u_id, v_id = self.node_mapping[u], self.node_mapping[v]
        if u_id < v_id:
            u_id, v_id = v_id, u_id

        self.adj_mat[u_id][v_id] = 1

    def add_edges_from(self, ebunch: Iterable[Hashable]) -> None:
        """
        Adds a bunch of edges to the graph.

        :param ebunch:
        :return:
        """
        for u, v in tqdm(ebunch, desc=f"{self.__class__.__name__}.add_edges_from"):
            self.add_edge(u, v)

    def edges(self):
        """
        Returns all edges in the graph.

        :return:
        """
        for u in range(len(self.adj_mat)):
            for v, val in enumerate(self.adj_mat[u]):
                if val:
                    yield self.node_mapping.inverse[u], self.node_mapping.inverse[v]

    def number_of_edges(self) -> int:
        """
        Returns the number of edges in the graph.

        :return:
        """
        # TODO maintain variable so we don't need to compute that
        return sum(map(sum, self.adj_mat))

    # the following are needed by networkx.is_bipartite:
    @staticmethod
    def is_directed() -> bool:
        """
        Returns False since we don't allow directed graphs.

        :return:
        """
        return False

    # Miscellaneous -------------------------------------------------------------------------------
    def subgraph(self, nbunch: Iterable[Hashable]) -> Self:
        """
        Returns the subgraph induced by nbunch.

        :param nbunch:
        :return:
        """
        result = self.__class__()
        result.add_nodes_from(nbunch)
        result.add_edges_from(
            (u, v) for u, v in combinations(result.node_mapping.keys(), 2) if self.has_edge(u, v)
        )
        return result

    def has_edge(self, u: Hashable, v: Hashable) -> bool:
        """
        Returns True if the edge between u and v is in the graph.

        :param u:
        :param v:
        :return:
        """
        u_id, v_id = self.node_mapping[u], self.node_mapping[v]
        if u_id < v_id:
            u_id, v_id = v_id, u_id

        return self.adj_mat[u_id][v_id]
