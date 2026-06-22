"""
Anthony Labarre © 2023-2026

O(n^4) algorithms.

"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
import os
from collections.abc import Hashable
from functools import lru_cache
from itertools import combinations

# ----- Third-party imports -----------------------------------------------------------------------
import networkx as nx

# ----- My imports --------------------------------------------------------------------------------
from graph_recognition.adjacency_matrix import HalfAdjacencyMatrix
from graph_recognition.directed_graph import DirectedGraph
from graph_recognition.domination import has_dominating_set_of_size_at_most_2
from graph_recognition.misc_algo import (
    complement,
    empty_graph_by_removing_vertices,
    is_connected,
    enumerate_all_p4s,
    co_connected_components, number_of_common_neighbors, complement_as_adj_mat, induced_subgraph_degrees,
)
from graph_recognition.online_algo import online_is_bipartite
from graph_recognition.profitable_hereditary_n import (
    is_planar,
    is_bipartite,
    is_chordal,
    is_co_bipartite,
    is_2k2_p4_free,
)
from graph_recognition.profitable_hereditary_n_2 import (
    is_co_chordal,
    is_dilworth_k,
)
from graph_recognition.profitable_hereditary_n_3 import (
    is_triangle_free,
)
from graph_recognition.profitable_hereditary_n_4 import (
    is_c4_free,
    is_4k1_free,
    is_k4_free,
)
from graph_recognition.recognizers_n_7 import is_hereditary_welsh_powell_perfect
from graph_recognition.recognizers_utils import (
    assign_class_id,
    current_module_recognizers, assign_inherited_fisc,
)
from graph_recognition.two_sat import Not, satisfiable


# Cache imported functions that are not already cached --------------------------------------------


# Auxiliary functions -----------------------------------------------------------------------------
@lru_cache(maxsize=None)
def vertex_is_pretty(graph: nx.Graph, v: Hashable) -> bool:
    """
    A vertex v is pretty if G[N(v)] is (2K_2, P_4)-free.

    Complexity: O(deg(v))

    :param v:
    :type graph: networkx.Graph
    :param graph:
    :return:
    @param graph:
    @param v:
    """
    return is_2k2_p4_free(graph.subgraph(graph[v]))


# Recognizers -------------------------------------------------------------------------------------
@assign_inherited_fisc()
@assign_class_id("gc_660")
@lru_cache(maxsize=None)
def is_cnplus4_k4_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_chordal(graph) and is_k4_free(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_2106")
@lru_cache(maxsize=None)
def is4_k1_co_cnplus4_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_co_chordal(graph) and is_4k1_free(graph)


@assign_class_id("gc_1191")
@lru_cache(maxsize=None)
def is_02_graph(graph: nx.Graph) -> bool:
    """
    A (0,2)-graph is a connected graph such that any two vertices have either 0 or 2 common
    neighbors.

    https://www.graphclasses.org/classes/gc_1191.html

    :param graph:
    :return:
    """
    if not is_connected(graph):
        return False

    # first search edges for a contradiction, in the hope that we can stop early
    if any(number_of_common_neighbors(graph, u, v) not in {0, 2} for u, v in graph.edges()):
        return False

    # then examine non-edges
    return all(number_of_common_neighbors(graph, u, v) in {0, 2} for u, v in nx.non_edges(graph))


@assign_inherited_fisc()
@assign_class_id("gc_1193")
@lru_cache(maxsize=None)
def is_02_graph_and_bipartite(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_bipartite(graph) and is_02_graph(graph)


@assign_inherited_fisc()
@assign_class_id("gc_912")
@lru_cache(maxsize=None)
def is_c4_triangle_free_and_planar(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_912.html

    @param graph:
    @return:
    """
    return is_planar(graph) and is_triangle_free(graph) and is_c4_free(graph)


@assign_class_id("gc_609")
@lru_cache(maxsize=None)
def is_pretty(graph: nx.Graph) -> bool:
    """
    A graph is pretty if every induced subgraph has a vertex whose neighborhood is
    (2K_2, P_4)-free.

    https://www.graphclasses.org/classes/gc_609.html

    :type graph: nx.Graph
    :param graph:
    :return:
    """
    # algo from https://doi.org/10.1002/(SICI)1097-0118(199610)23:2%3C203::AID-JGT11%3E3.0.CO;2-H
    return empty_graph_by_removing_vertices(graph, vertex_is_pretty)


@assign_inherited_fisc()
@assign_class_id("gc_1192")
@lru_cache(maxsize=None)
def is_rectagraph(graph: nx.Graph) -> bool:
    """
    A graph is a rectagraph iff it is triangle-free and a (0,2)-graph .

    https://www.graphclasses.org/classes/gc_1192.html

    @param graph:
    @return:
    """
    return is_triangle_free(graph) and is_02_graph(graph)


@assign_class_id("gc_1145")
@lru_cache(maxsize=None)
def is_almost_claw_free(graph: nx.Graph) -> bool:
    """
    Let A be the set of vertices in a graph G that are the centers of an induced claw. A graph G is
    almost claw-free if A is independent and for every x in A: the subgraph induced by N(x) has a
    dominating set of size at most 2.

    https://www.graphclasses.org/classes/gc_1145.html

    Complexity: at least O(n^4) since we iterate over all 4-tuples to retrieve claw centers.

    :type graph: nx.Graph
    :param graph:
    :return:
    """
    # extract all claw centers, checking independence as we go along
    claw_centers = set()

    for center in graph:
        for a, b, c in combinations(graph[center], 3):
            # since a, b, c are neighbors of center, we have an induced claw iff a, b, c are
            # pairwise non-adjacent
            if not graph.has_edge(a, b) and not graph.has_edge(a, c) and not graph.has_edge(b, c):
                # check whether subgraph induced by the center's neighbors has a dominating set of
                # size <= 2
                if not has_dominating_set_of_size_at_most_2(graph.subgraph(graph[center])):
                    return False

                # check whether adding center to claw_centers would still induce an independent set
                if any(graph.has_edge(center, v) for v in claw_centers):
                    return False

                # everything's fine for that center, record it and skip other combinations
                claw_centers.add(center)
                break

    return True


@assign_class_id("gc_487")
@lru_cache(maxsize=None)
def is_circular_arc_and_co_bipartite(graph: nx.Graph) -> bool:
    """
    Let G be a graph and let G* be the graph with V(G*) = E(G) and two vertices of G* are adjacent
    precisely when the endpoints of the corresponding edges of G induce a C4 in G. G is circular
    arc ∩ co-bipartite iff both the complement of G and G* are bipartite .

    https://www.graphclasses.org/classes/gc_487.html

    @param graph:
    @return:
    """
    if not is_co_bipartite(graph):
        return False

    def edge_generator():
        """
        Yields the edges of the graph that must be checked for bipartiteness in the original
        algorithm. This allows us to check bipartiteness as we go without building the whole graph.

        :return:
        """
        # connect each pair of edges that induce a C_4 in the original graph
        for e, f in combinations(graph.edges(), 2):
            endpoints = frozenset(e + f)
            if len(endpoints) == 4 and set(induced_subgraph_degrees(graph, endpoints).values()) == {2}:
                yield e, f

    return online_is_bipartite(edge_generator())


@assign_class_id("gc_174")
@lru_cache(maxsize=None)
def is_dilworth_4(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_dilworth_k(graph, 4)


@assign_class_id("gc_3")
@lru_cache(maxsize=None)
def is_p4_brittle(graph: nx.Graph | HalfAdjacencyMatrix) -> bool:
    """
    A graph is P4-brittle if it contains an independent set S such that either every P4 has a
    midpoint in S or every P4 has an endpoint in S.

    https://www.graphclasses.org/classes/gc_3

    @param graph:
    @return:
    """
    # algorithm from https://doi.org/10.1016/S0012-365X(99)00300-3, p 204
    implication_graph = DirectedGraph()
    # for each P_{4} (abcd) we have a clause (a or d) equivalent to (not a => d)
    for p4 in enumerate_all_p4s(graph):
        # we have a P_{4}, extract a and d and build clause
        a, d = [v for v in p4 if sum(graph.has_edge(v, u) for u in p4 if u != v) == 1]
        implication_graph.add_edge(Not(a), d)

    # for each edge (ab) we have a clause (not a or not b) equivalent to (a => not b)
    implication_graph.add_edges_from((a, Not(b)) for a, b in graph.edges())

    return satisfiable(implication_graph)


# -------------------------------------------------------------------------------------------------
# The following recognizers call another recognizer on the complement of the input graph. Since
# building the complement can be time- and memory-consuming on large instances, and since
# recognizers are loaded in the order in which they appear in a recognizer file, those recognizers
# should stay at the end of the file in the hope that they are not actually needed until we figure
# out a way to bypass the computation of the complement.
# -------------------------------------------------------------------------------------------------
@assign_class_id("gc_156")
@lru_cache(maxsize=None)
def is_co_p4_brittle(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_156

    @param graph:
    @return:
    """
    # iterate over co-connected components instead of complementing the whole graph, in the hope
    # that we can thereby stop early
    return all(
        is_p4_brittle(complement_as_adj_mat(graph, cc)) for cc in co_connected_components(graph)
    )


@assign_class_id("AUTO_2088")
@lru_cache(maxsize=None)
def is_co_hereditary_welsh_powell_perfect(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    # iterate over co-connected components instead of complementing the whole graph, in the hope
    # that we can thereby stop early
    return all(
        is_hereditary_welsh_powell_perfect(complement(graph.subgraph(cc)))
        for cc in co_connected_components(graph)
    )


# This code segment must always be at the END of a recognizer file --------------------------------
RECOGNIZERS = current_module_recognizers(
    ".".join(
        [
            os.path.basename(os.path.dirname(__file__)),
            os.path.basename(__file__).removesuffix(".py"),
        ]
    )
)
# -------------------------------------------------------------------------------------------------
