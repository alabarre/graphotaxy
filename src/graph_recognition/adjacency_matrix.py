"""
Anthony Labarre © 2026

Implementation of an undirected, unweighted graph as a half-adjacency matrix: only the lower
triangle (including the diagonal to allow loops) is stored as a list of bitarrays.

Nodes can be of any hashable type. Loops are supported, parallel edges are ignored. The class
features the bare minimum for being compatible with the algorithms I need to run (mine or
networkx's), so don't hope for full compatibility yet.

This implementation turns out to be much more memory-efficient than networkx.Graph . I hope to be
eventually able to use only this class, but in the meantime it comes particularly handy in the
context of recognizers that need to sift through many subgraphs of an input graph, or deal with its
complement.


"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
from array import array
from typing import Iterable, Self, Any, Hashable

# ----- Third-party imports -----------------------------------------------------------------------
from bitarray import bitarray


class HalfAdjacencyMatrix:
    """
    Implementation of an undirected, unweighted graph as a half-adjacency matrix: only the lower
    triangle (including the diagonal to allow loops) is stored as a list of bitarrays.

    Nodes can be of any hashable type. Loops are supported, parallel edges are ignored.

    """

    def __init__(self, edge_data=None) -> None:
        """
        Initializes the relevant data structures.
        """
        # we map nodes to integer ids so vertices can be of any hashable type, and we can extract
        # subgraphs more easily
        #self.node_mapping = bidict()
        #self.nodes = self.node_mapping.keys()  # for nx algorithms that need to access this field
        # switching to two structures instead of bidict
        self.node_to_id = dict()
        self.id_to_node = list()
        self.nodes = self.node_to_id.keys()  # for nx algorithms that need to access this field

        # store the number of nodes and edges so we can return them in constant time
        self.num_edges = 0
        self.num_nodes = 0

        # the half-adjacency matrix is a list of bitarrays of variable sizes; to avoid calling len
        # each time we need to know their lengths, we store them in an array and update them as we
        # go
        self.adj_mat = []
        # choosing type 'I' allows to have a graph with at least 1,000,000,000 nodes; that should
        # be enough (otherwise, switch to a larger type)
        self.row_lengths = array('I', [])
        if edge_data is not None:
            self.add_edges_from(edge_data)

    # Node-related methods ------------------------------------------------------------------------
    def add_node(self, node: Any) -> None:
        """
        Adds a node to the graph.

        :param node:
        :return:
        """
        if node not in self.node_to_id:
            self.node_to_id[node] = self.num_nodes  # map node to identifier
            self.id_to_node.append(node)  # map id to node
            self.num_nodes += 1
            # add row to adjacency matrix
            self.adj_mat.append(bitarray())
            self.row_lengths.append(0)

    def add_nodes_from(self, nbunch: Iterable) -> None:
        """
        Adds all nodes from nbunch to the graph.

        :param nbunch:
        :return:
        """
        for node in nbunch:
            self.add_node(node)

    @property  # so we can use both graph.degree and graph.degree()
    def degree(self):
        """
        Returns a pairing of all nodes to their degree.

        :return:
        """
        for node, node_id in self.node_to_id.items():
            # as in the neighbors function, the degree of a vertex is the sum of 1's in its row
            # plus the number of rows after node's row that have a 1 in its column
            yield node, sum(self.adj_mat[node_id]) + sum(
                self.adj_mat[row_idx][node_id] for row_idx in range(node_id + 1, self.num_nodes)
                if node_id < self.row_lengths[row_idx]
            )

    def get_degree(self, v: Hashable) -> int:
        """
        Returns the degree of v in the graph.

        :param v:
        :return:
        """
        return sum(1 for _ in self.neighbors(v))

    def neighbors(self, v: Hashable):
        """
        Returns the neighbors of vertex v.

        >>> G = HalfAdjacencyMatrix()
        >>> G.add_edge("bla", "blou")
        >>> set(G.neighbors("bla"))
        {'blou'}
        >>> G = HalfAdjacencyMatrix()
        >>> G.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 4)])
        >>> sorted(G.neighbors(2))
        [1, 3]

        :param v:
        :return:
        """
        # since we only store the lower triangle of the adjacency matrix, the neighbors of a
        # vertex v are 1) the column indices with a True value in v's row, and 2) the row
        # indices with a True value in v's column for rows located after v's row

        # gather neighbors of type 1)
        v_id = self.node_to_id[v]
        for pos, val in enumerate(self.adj_mat[v_id]):
            if val:
                yield self.id_to_node[pos]

        # gather neighbors of type 2)
        for row_idx in range(v_id + 1, self.num_nodes):
            if v_id < self.row_lengths[row_idx] and self.adj_mat[row_idx][v_id]:
                yield self.id_to_node[row_idx]

    def non_neighbors(self, v: Hashable):
        """
        Returns the non-neighbors of vertex v (except v itself).

        >>> G = HalfAdjacencyMatrix()
        >>> G.add_edges_from([('0', '1'), ('1', '2'), ('2', '3'), ('3', '4')])
        >>> sorted(G.non_neighbors('2'))
        ['0', '4']

        :param v:
        :return:
        """
        # assert v in self.node_mapping, f"error: node {v} not in {self.node_mapping}" # BUG ICI
        # print(f"[debug] v = {v}, nodes = {set(self.node_mapping)}")
        for non_n in set(self.node_to_id).difference(self.neighbors(v)).difference({v}):
            yield non_n

    def number_of_nodes(self) -> int:
        """
        Returns the number of nodes in the graph.

        :return:
        """
        return self.num_nodes

    def __iter__(self):
        """
        Allows iterating over the graph's nodes (i.e.: "for node in graph").

        :return:
        """
        for node in self.node_to_id:
            yield node

    def __getitem__(self, v: Hashable) -> set:
        """
        Allows access to v's neighbors with brackets (i.e.: graph[v]).

        >>> G = HalfAdjacencyMatrix()
        >>> G.add_edges_from([("a", "b"), ("b", "c")])
        >>> sorted(G["b"])
        ['a', 'c']

        :param v:
        :return:
        """
        # note: I would yield, but some networkx algorithms have lines like "if len(G[n]) == 0", so
        # we need to return something that can support len()
        return {x for x in self.neighbors(v)}

    def __len__(self) -> int:
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
            self.add_node(node)

        # since we only store the lower triangle of the adjacency matrix, we only store
        # (u_id, v_id) if v_id <= u_id
        u_id, v_id = self.node_to_id[u], self.node_to_id[v]
        if u_id < v_id:
            u_id, v_id = v_id, u_id

        # if row too short: extend up to v_id and update length
        if v_id >= self.row_lengths[u_id]:
            self.adj_mat[u_id].extend(bitarray(v_id - self.row_lengths[u_id] + 1))
            self.row_lengths[u_id] = v_id + 1

        # mandatory check so we don't increase self.num_edges by mistake
        if not self.adj_mat[u_id][v_id]:
            self.num_edges += 1
            self.adj_mat[u_id][v_id] = 1

    def add_edges_from(self, ebunch: Iterable) -> None:
        """
        Adds a bunch of edges to the graph.

        :param ebunch:
        :return:
        """
        for u, v in ebunch:
            self.add_edge(u, v)

    def edges(self):
        """
        Generates all edges in the graph.

        >>> G = HalfAdjacencyMatrix()
        >>> G.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 4)])
        >>> sorted(map(sorted, G.edges()))
        [[0, 1], [1, 2], [2, 3], [3, 4]]

        :return:
        """
        for u in range(len(self.adj_mat)):
            for v, val in enumerate(self.adj_mat[u]):
                if val:
                    yield self.id_to_node[u], self.id_to_node[v]

    def has_edge(self, u: Hashable, v: Hashable) -> bool:
        """
        Returns True if the edge between u and v is in the graph.

        :param u:
        :param v:
        :return:
        """
        u_id, v_id = self.node_to_id[u], self.node_to_id[v]
        if u_id < v_id:
            u_id, v_id = v_id, u_id

        return v_id < self.row_lengths[u_id] and self.adj_mat[u_id][v_id]

    def number_of_edges(self) -> int:
        """
        Returns the number of edges in the graph.

        :return:
        """
        return self.num_edges

    def number_of_selfloops(self) -> int:
        """
        Returns the number of edges of the form (u, u) in the graph.

        :return:
        """
        return sum(self.adj_mat[i][i] for i in range(self.num_nodes) if i < self.row_lengths[i])

    # the following are needed by networkx.is_bipartite:
    @staticmethod
    def is_directed() -> bool:
        """
        Returns False since we don't allow directed graphs.

        :return:
        """
        return False

    def size(self) -> int:
        """
        Returns the number of edges in the graph.

        :return:
        """
        return self.number_of_edges()

    # Miscellaneous -------------------------------------------------------------------------------
    def subgraph(self, nbunch: Iterable[Hashable]) -> Self:
        """
        Returns the subgraph induced by nbunch.

        :param nbunch:
        :return:
        """
        nodes = set(nbunch)
        result = self.__class__()
        result.add_nodes_from(nodes)
        # add edges from the original graph whose endpoints are in nodes
        result.add_edges_from((u, v) for u in nodes for v in nodes.intersection(self.neighbors(u)))
        return result

    @staticmethod
    def is_multigraph() -> bool:
        """

        :return:
        """
        return False

    def __contains__(self, v: Hashable) -> bool:
        """
        Returns True if the vertex v exists in the graph.

        :param v:
        :return:
        """
        return v in self.node_to_id

    def order(self) -> int:
        """
        Returns the number of nodes in the graph.

        :return:
        """
        return self.num_nodes
