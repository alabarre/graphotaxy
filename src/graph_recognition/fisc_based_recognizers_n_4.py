"""Anthony Labarre © 2023-2026

This file contains all naïve recognizers with complexity O(n^4) for those graph classes in ISGCI
that admit a FISC (forbidden induced subgraph characterisation).

Recognizers are sorted first on the basis of the order of their largest pattern, then by number of
patterns. Additionally, every pattern in a given set will be examined by increasing size.

For now, only "fixed" subgraphs are taken into account. This excludes general configurations like
C_{n+4}, XC, XZ, ...

Unless you have a much better recognition algorithm than exhaustive search, calling is_h_free is
usually much faster.

"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
import os
from functools import lru_cache

import networkx
# ----- Third-party imports -----------------------------------------------------------------------
import networkx as nx
from pyroaring import BitMap

# ----- My imports --------------------------------------------------------------------------------
from graph_recognition.adjacency_matrix import HalfAdjacencyMatrix
from graph_recognition.misc_algo import (
    is_h_u_k1_free,
    complement_as_adj_mat, degree_sequence, number_of_edges, neighbors, number_of_nodes, explicit_triangles,
    non_neighbors, )
from graph_recognition.profitable_hereditary_n import (
    is_cograph,
    is_forest, is_2k2_free, is_planar, )
from graph_recognition.profitable_hereditary_n_2 import is_co_chordal, is_co_gem_free
from graph_recognition.profitable_hereditary_n_3 import (
    is_paw_free, is_co_paw_free,
)
from graph_recognition.recognizers_n_3 import explicit_independent_triplets
from graph_recognition.recognizers_utils import (
    assign_class_id,
    current_module_recognizers,
    assign_fisc, assign_inherited_fisc,
)
from graph_recognition.subgraphs import is_h_free


# Recognizers -------------------------------------------------------------------------------------

# All recognizers for patterns on at most 4 vertices ----------------------------------------------
@assign_class_id("gc_674")
@lru_cache(maxsize=None)
def is_4k1_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is 4K_{1}-free.

    See https://www.graphclasses.org/classes/gc_674

    Complexity of naïve matching: O(n^4)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["4K_{1}"])  # is_even_co_clique_free(graph, 4)


@assign_fisc(["diamond"])
@assign_class_id("gc_441")
@lru_cache(maxsize=None)
def is_diamond_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is diamond-free.

    See https://www.graphclasses.org/classes/gc_441

    Complexity of naïve matching: O(n^4)

    :type graph: networkx.Graph
    """
    if number_of_nodes(graph) < 4 or number_of_edges(graph) < 5:
        return True

    adj = {v: neighbors(graph, v) for v in graph}

    # search for an edge uv with two common neighbors a, b of these extremities such that ab is
    # not an edge
    for u, v in graph.edges():
        common = adj[u] & adj[v]

        if len(common) >= 2 and any(common - adj[x] - BitMap([x]) for x in common):
            return False

    return True
    # much faster than:
    #return is_h_free(graph, ["diamond"])


@assign_fisc(["C_{4}"])
@assign_class_id("gc_360")
@lru_cache(maxsize=None)
def is_c4_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is C_{4}-free.

    See https://www.graphclasses.org/classes/gc_360

    Complexity: O(m^2) <= O(n^4) (naïve)

    :type graph: networkx.Graph
    """
    # naïve algorithm, but much faster than GSS for large graphs
    if number_of_nodes(graph) < 4:
        return True

    adj = {v: neighbors(graph, v) for v in graph}

    for u, v in nx.non_edges(graph):
        common = adj[u] & adj[v]

        if len(common) >= 2:
            # look for two non-adjacent common neighbors
            for x in common:
                witnesses = common - adj[x]
                witnesses.discard(x)

                # found -> there is a C_{4}
                if witnesses:
                    return False

    return True
    # much faster than:
    #return is_h_free(graph, ["C_{4}"])


@assign_fisc(["diamond", "C_{4}"])
@assign_class_id("gc_473")
@lru_cache(maxsize=None)
def is_c4_diamond_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{4}, diamond)-free.

    See https://www.graphclasses.org/classes/gc_473

    Complexity: O(m^2) <= O(n^4) (naïve)

    :type graph: networkx.Graph
    """
    return is_c4_free(graph) and is_diamond_free(graph)


@assign_fisc(["diamond", "paw", "P_{4}"])
@assign_class_id("gc_1375")
@lru_cache(maxsize=None)
def is_p4_diamond_paw_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{4}, diamond, paw)-free.

    See https://www.graphclasses.org/classes/gc_1375

    Complexity of naïve matching: O(n^4)

    :type graph: networkx.Graph
    """
    return is_cograph(graph) and is_paw_free(graph) and is_diamond_free(graph)


@assign_fisc(["C_{4}", "P_{4}", "diamond", "paw"])
@assign_class_id("gc_1376")
@lru_cache(maxsize=None)
def is_gc_1376(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return (
            is_cograph(graph)
            and is_paw_free(graph)
            and is_c4_free(graph)
            and is_diamond_free(graph)
    )


@assign_inherited_fisc([
    "co-claw",  # C_{3} U K_{1}
    "co-butterfly",  # C_{4} U K_{1}
    "co(W_{5})",  # C_{5} U K_{1}
])  # partial fisc for (C_{n+3} U K_{1})-free, no larger such configuration in ISGCI yet
@assign_class_id("gc_1020")
@lru_cache(maxsize=None)
def is_cnplus3_u_k1_diamond_paw_free(graph: nx.Graph | HalfAdjacencyMatrix) -> bool:
    """

    https://www.graphclasses.org/classes/gc_1020.html


    Complexity: O(n^4).

    :param graph:
    :return:
    """
    # checking (C_{n+3} U K_{1})-freeness amounts to checking cycle-freeness of the graph obtained
    # by removing v U N(v) for every v in the graph
    return is_h_u_k1_free(graph, is_forest) and is_paw_free(graph) and is_diamond_free(graph)


@assign_inherited_fisc([
    "claw",  # co(C_{3} U K_{1})
    "butterfly",  # co(C_{4} U K_{1})
    "W_{5}",  # co(C_{5} U K_{1})
])  # partial fisc for co(C_{n+3} U K_{1})-free, no larger such configuration in ISGCI yet
@assign_class_id("AUTO_2276")
@lru_cache(maxsize=None)
def is_co_cnplus3_u_k1_co_diamond_co_paw_free(graph: nx.Graph | HalfAdjacencyMatrix) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_2276.html


    Complexity: O(n^4).

    :param graph:
    :return:
    """
    return is_cnplus3_u_k1_diamond_paw_free(complement_as_adj_mat(graph))


@assign_fisc([
    "claw",  # co(C_{3} U K_{1})
    "butterfly",  # co(C_{4} U K_{1})
    "W_{5}",  # co(C_{5} U K_{1})
    "co-diamond",
    "co-paw",
])  # partial fisc for co(C_{n+3} U K_{1})-free, no larger such configuration in ISGCI yet
@assign_class_id("AUTO_2276")
@lru_cache(maxsize=None)
def is_cnplus3_u_k1_co_diamond_co_paw_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_2276

    Complexity: O(n^4).

    :param graph:
    :return:
    """
    return is_cnplus3_u_k1_diamond_paw_free(complement_as_adj_mat(graph))


@assign_inherited_fisc()
@assign_class_id("AUTO_1479")
@lru_cache(maxsize=None)
def is_auto_1479(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (4K_{1}, P_{4})-free.

    See https://www.graphclasses.org/classes/AUTO_1479

    Complexity of naïve matching: O(n^4)
    :type graph: networkx.Graph
    """
    return is_cograph(graph) and is_4k1_free(graph)


@assign_fisc(["co-claw"])
@assign_class_id("AUTO_79")
@lru_cache(maxsize=None)
def is_co_claw_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is co-claw-free.

    See https://www.graphclasses.org/classes/AUTO_79

    Complexity of naïve matching: O(n^4)

    >>> from networkx import Graph; G=Graph(); G.add_edges_from([(0, 1), (0, 2), (1, 2)]); G.add_node(3)
    >>> is_co_claw_free(G)
    False

    :type graph: networkx.Graph
    """
    for u, v, w in explicit_triangles(graph):
        if non_neighbors(graph, u) & non_neighbors(graph, v) & non_neighbors(graph, w):
            return False

    return True
    # much faster than
    #return is_h_free(graph, ["co-claw"])


@assign_fisc(["claw"])
@assign_class_id("gc_62")
@lru_cache(maxsize=None)
def is_claw_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is claw-free.

    See https://www.graphclasses.org/classes/gc_62

    Complexity of naïve matching: O(n^4)

    :type graph: networkx.Graph
    """
    # in a claw-free graph the maximum degree is 2 * sqrt(|E|)
    # (see https://doi.org/10.1016/S0020-0190(00)00047-8)
    if graph and degree_sequence(graph)[0] > 2 * number_of_edges(graph) ** 0.5:
        return False

    # note: commenting the trick below, issues getting it to work with HalfAdjacencyMatrix
    """
    # every claw-free graph of even order has a perfect matching
    # https://www.combinatorics.org/ojs/index.php/eljc/article/download/v13i1r59/pdf/, thm. 5 p. 4
    # Note: they don't mention connectedness in this quoted result, but obviously it is required:
    # otherwise, we can simply add singletons, which by definition cannot be paired
    if is_connected(graph) and not number_of_nodes(graph) % 2 and not is_perfect_matching(
            graph, maximum_matching(graph)
    ):
        return False

    """
    for u, v, w in explicit_independent_triplets(graph):
        if neighbors(graph, u) & neighbors(graph, v) & neighbors(graph, w):
            return False
    return True
    # faster than:
    #return is_h_free(graph, ["claw"])


@assign_fisc(["co-diamond"])
@assign_class_id("AUTO_77")
@lru_cache(maxsize=None)
def is_co_diamond_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is co-diamond-free.

    See https://www.graphclasses.org/classes/AUTO_77

    Complexity: O(m^2) <= O(n^4).

    :type graph: networkx.Graph
    """
    nodes = BitMap(graph)
    adj = {v: neighbors(graph, v) for v in graph}

    # a co-diamond is an edge a-b and two independent vertices x and y, so let's search all edges
    for a, b in graph.edges:
        # consider all their common non-neighbors
        common_non_neighbors = nodes - adj[a] - adj[b]
        common_non_neighbors.discard(a)
        common_non_neighbors.discard(b)

        # we need at least 2 non-neighbors
        if len(common_non_neighbors) >= 2:
            # for each common non-neighbor x, check if it has a non-neighbor y that is also
            # non-adjacent to a and b
            for x in common_non_neighbors:
                if common_non_neighbors - adj[x] - BitMap([x]):
                    return False

    return True


@assign_inherited_fisc()
@assign_class_id("AUTO_1939")
@lru_cache(maxsize=None)
def is_p4_co_diamond_co_paw_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{4}, co-diamond, co-paw)-free.

    See https://www.graphclasses.org/classes/AUTO_1939

    Complexity: O(m^2) <= O(n^4) (naïve)

    :type graph: networkx.Graph
    """
    return is_cograph(graph) and is_co_paw_free(graph) and is_co_diamond_free(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_1940")
@lru_cache(maxsize=None)
def is_auto_1940(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, P_{4}, co-diamond, co-paw)-free.

    See https://www.graphclasses.org/classes/AUTO_1940

    Complexity: O(m^2) <= O(n^4) (naïve)

    @param graph:
    @return:
    """
    return (
            is_cograph(graph)
            and is_co_paw_free(graph)
            and is_2k2_free(graph)
            and is_co_diamond_free(graph)
    )


@assign_inherited_fisc()
@assign_class_id("AUTO_2768")
@lru_cache(maxsize=None)
def is_co_cnplus4_co_claw_co_gem_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_co_chordal(graph) and is_co_gem_free(graph) and is_co_claw_free(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_1500")
@lru_cache(maxsize=None)
def is_auto_1500(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{4}, co-claw)-free.

    See https://www.graphclasses.org/classes/AUTO_1500

    Complexity of naïve matching: O(n^4)
    :type graph: networkx.Graph
    """
    return is_co_claw_free(graph) and is_c4_free(graph)


@assign_fisc(["K_{4}"])
@assign_class_id("gc_455")
@lru_cache(maxsize=None)
def is_k4_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is K_{4}-free.

    See https://www.graphclasses.org/classes/gc_455

    Complexity of naïve matching: O(n^4)

    :type graph: networkx.Graph
    """
    if number_of_nodes(graph) < 4 or number_of_edges(graph) < 6:
        return True

    adj = {v: neighbors(graph, v) for v in graph}

    # search for an edge uv with two common neighbors a, b of these extremities such that ab is
    # also an edge
    for u, v in graph.edges():
        common = adj[u] & adj[v]

        if len(common) >= 2 and any(adj[x] & common for x in common):
            return False

    return True
    # much faster than:
    #return is_h_free(graph, ["K_{4}"])


@assign_inherited_fisc()
@assign_class_id("gc_1367")
@lru_cache(maxsize=None)
def is_k4_free_and_planar(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is K_{4}-free and planar.

    See https://www.graphclasses.org/classes/gc_1367

    Complexity of naïve matching: O(n^4)

    :type graph: networkx.Graph
    """
    return is_planar(graph) and is_k4_free(graph)


# This code segment must always be at the END of a recognizer file --------------------------------
RECOGNIZERS = current_module_recognizers(
    ".".join(
        [
            os.path.basename(os.path.dirname(__file__)),
            os.path.basename(__file__).strip(".py"),
        ]
    )
)
# -------------------------------------------------------------------------------------------------
