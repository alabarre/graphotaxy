"""Anthony Labarre © 2023-2026

This file contains recognizers for profitable hereditary classes, i.e. classes that admit a
forbidden induced subgraph characterization, but can be recognized with a faster-than-naïve
algorithm.

Recognizers in this file have running time O(n^4).

"""

# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
import os
from array import array
from collections import defaultdict
from functools import lru_cache
from itertools import combinations

# ----- Third-party imports -----------------------------------------------------------------------
import networkx as nx

# ----- My imports --------------------------------------------------------------------------------
from graph_recognition.misc_algo import (
    number_of_common_neighbours,
    degree_sequence,
    complement,
    is_even_clique_free,
    is_even_co_clique_free,
    explicit_triangles,
    co_connected_components,
)
from graph_recognition.profitable_hereditary_n import (
    is_bipartite,
    is_cograph,
    is_co_bipartite,
    is_planar,
    is_chordal,
    is_split,
    is_co_maximum_degree_4,
    is_2k2_free, is_mock_threshold,
)
from graph_recognition.profitable_hereditary_n_2 import (
    is_comparability,
    is_co_chordal,
    is_co_diamond_free,
    is_co_paw_free,
    is_co_gem_free,
)
from graph_recognition.profitable_hereditary_n_3 import (
    is_triangle_free,
    is_co_at_free,
    my_is_at_free,
    is_3k1_free,
    is_paw_free,
    is_locally_connected,
    is_claw_diamond_free,
    is_co_p3_free,
)
from graph_recognition.recognizers_utils import (
    current_module_recognizers,
    assign_class_id,
    assign_fisc,
)


# Recognizers -------------------------------------------------------------------------------------
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
    # equivalent to https://www.graphclasses.org/classes/gc_196.html
    # A graph is weakly geodetic if for every pair of vertices of distance 2 there is a unique
    # common neighbor of them.
    # iterate over the extremities of all non-edges; either they are at distance 2, and therefore
    # must have exactly one common neighbor, or they are at distance > 2, in which case they have
    # no common neighbor
    return all(number_of_common_neighbours(graph, u, v) <= 1 for u, v in nx.non_edges(graph))


@assign_fisc(
    [
        "K_{5} - e",
        "K_{5}",
        "W_{4}",
        "co(P_{3} U 2K_{1})",
        "co(K_{3} U 2K_{1})",
        "co(P_{2} U P_{3})",
        "K_{2,3}",
    ]
)
@assign_class_id("gc_1190")
@lru_cache(maxsize=None)
def is_xc_13_free(graph: nx.Graph) -> bool:
    """
    A graph is XC_{13}-free iff any two vertices have at most two common neighbors.

    Complexity: O(n^4) < O(n^5) (naïve)

    :param graph:
    :return:
    """
    return all(
        number_of_common_neighbours(graph, u, v) <= 2 for u, v in combinations(graph, 2)
    )


@assign_fisc(["co-claw"])
@assign_class_id("AUTO_79")
@lru_cache(maxsize=None)
def is_co_claw_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is co-claw-free.

    See https://www.graphclasses.org/classes/AUTO_79

    Complexity: O(mn^2) <= O(n^4) (naïve)

    >>> from networkx import Graph; G=Graph(); G.add_edges_from([(0, 1), (0, 2), (1, 2)]); G.add_node(3)
    >>> is_co_claw_free(G)
    False

    :type graph: networkx.Graph
    """
    # much faster than return is_h_free(graph, ["co-claw"]) when measured with timeit: return True
    # iff graph contains no "triangle + independent vertex"
    return all(
        not set.intersection(
            set(nx.non_neighbors(graph, u)),
            nx.non_neighbors(graph, v),
            nx.non_neighbors(graph, w),
        )
        for u, v, w in explicit_triangles(graph)
    )


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
    if graph and degree_sequence(graph)[0] > 2 * graph.size() ** 0.5:
        return False

    # for each vertex u, check whether u and any 3 of its neighbors induce a claw
    claw_deg_seq = array("b", [3, 1, 1, 1])
    return all(
        degree_sequence(graph.subgraph({u, v, w, x})) != claw_deg_seq
        for u in graph
        for v, w, x in combinations(graph[u], 3)
    )


@assign_fisc(
    ["C_{5}", "C_{6}", "C_{7}", "C_{8}"]
)  # partial since holes include all cycles of length >= 5
@assign_class_id("gc_437")
@lru_cache(maxsize=None)
def is_hole_free(graph: nx.Graph) -> bool:
    """
    Returns true if G is hole-free, false otherwise.

    https://www.graphclasses.org/classes/gc_437.html

    Complexity: O(n^4).

    :param graph:
    :return:
    """

    # first algorithm in https://www.cs.uoi.gr/~palios/pubs/D5.pdf
    # O(n+m^2) = O(n^4)
    @lru_cache(maxsize=None)
    def process(a: int, b: int, c: int) -> bool:
        """
        The auxiliary process procedure from https://www.cs.uoi.gr/~palios/pubs/D5.pdf
        used in the algorithm that test hole-freeness.

        :param a:
        :param b:
        :param c:
        :return:
        """
        in_path[c] = True
        for d in graph[c]:
            if not graph.has_edge(a, d) and not graph.has_edge(b, d):
                if in_path[d]:
                    return True
                if not not_in_hole[(b, c, d)]:
                    if process(b, c, d):
                        return True

        in_path[c] = False
        not_in_hole[(a, b, c)] = True
        not_in_hole[(c, b, a)] = True

        return False

    in_path = defaultdict(lambda: False)
    not_in_hole = defaultdict(lambda: False)
    for u in graph.nodes:
        in_path[u] = True
        for v, w in graph.edges:
            if (
                graph.has_edge(u, v)
                and not graph.has_edge(u, w)
                and not not_in_hole[(u, v, w)]
            ):
                in_path[v] = True
                if process(u, v, w):
                    return False
                in_path[v] = False

        in_path[u] = False

    return True


# fisc built through calls to constituent recognizers
@assign_class_id("AUTO_2758")
@lru_cache(maxsize=None)
def is_anti_hole_odd_anti_cycle_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_co_bipartite(graph) and is_anti_hole_free(graph)


# the fisc will be obtained through calls to constituent class recognizers
@assign_class_id("gc_126")
@lru_cache(maxsize=None)
def is_comparability_and_weakly_chordal(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_126

    @param graph:
    @return:
    """
    return is_comparability(graph) and is_weakly_chordal(graph)


# the fisc will be obtained through calls to constituent class recognizers
@assign_class_id("AUTO_773")
@lru_cache(maxsize=None)
def is_hole_odd_cycle_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_bipartite(graph) and is_hole_free(graph)


# the fisc will be obtained through calls to constituent class recognizers
@assign_class_id("gc_1277")
@lru_cache(maxsize=None)
def is_hole_free_and_planar(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_planar(graph) and is_hole_free(graph)


# the fisc will be obtained through calls to constituent class recognizers
@assign_class_id("gc_14")
@lru_cache(maxsize=None)
def is_weakly_chordal(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_hole_free(graph) and is_anti_hole_free(graph)


# the fisc will be obtained through calls to constituent class recognizers
@assign_class_id("AUTO_2760")
@lru_cache(maxsize=None)
def is_co_chordal_and_co_claw_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_co_claw_free(graph) and is_co_chordal(graph)


# the fisc will be obtained through calls to constituent class recognizers
@assign_class_id("AUTO_2129")
@lru_cache(maxsize=None)
def is_co_at_free_and_co_claw_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_co_claw_free(graph) and is_co_at_free(graph)


# the fisc will be obtained through calls to constituent class recognizers
@assign_class_id("AUTO_2764")
@lru_cache(maxsize=None)
def is_co_bipartite_and_co_claw_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_co_claw_free(graph) and is_co_bipartite(graph)


# the fisc will be obtained through calls to constituent class recognizers
@assign_class_id("gc_60")
@lru_cache(maxsize=None)
def is_at_free_and_claw_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_claw_free(graph) and my_is_at_free(graph)


# the fisc will be obtained through calls to constituent class recognizers
@assign_class_id("gc_525")
@lru_cache(maxsize=None)
def is_bipartite_and_claw_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_claw_free(graph) and is_bipartite(graph)


# the fisc will be obtained through calls to constituent class recognizers
@assign_class_id("gc_303")
@lru_cache(maxsize=None)
def is_chordal_and_claw_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_claw_free(graph) and is_chordal(graph)


# the fisc will be obtained through calls to constituent class recognizers
@assign_class_id("gc_1292")
@lru_cache(maxsize=None)
def is_claw_free_and_mock_threshold(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_claw_free(graph) and is_mock_threshold(graph)


# the fisc will be obtained through calls to constituent class recognizers
@assign_class_id("AUTO_1452")
@lru_cache(maxsize=None)
def is_auto_1452(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, 3K_{1})-free.

    See https://www.graphclasses.org/classes/AUTO_1452

    Complexity of naïve matching: O(n^4)
    :type graph: networkx.Graph
    """
    #      3K_{1}                 2K_{2}
    return is_3k1_free(graph) and is_2k2_free(graph)


# the fisc will be obtained through calls to constituent class recognizers
@assign_class_id("gc_509")
@lru_cache(maxsize=None)
def is_gc_509(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (claw, paw)-free.

    See https://www.graphclasses.org/classes/gc_509

    Complexity of naïve matching: O(n^4)
    :type graph: networkx.Graph
    """
    return is_paw_free(graph) and is_claw_free(graph)


# the fisc will be obtained through calls to constituent class recognizers
@assign_class_id("AUTO_1761")
@lru_cache(maxsize=None)
def is_auto_1761(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, co-claw, co-diamond)-free.

    See https://www.graphclasses.org/classes/AUTO_1761

    Complexity of naïve matching: O(n^4)
    :type graph: networkx.Graph
    """
    return is_co_diamond_free(graph) and is_co_claw_free(graph) and is_2k2_free(graph)


# the fisc will be obtained through calls to constituent class recognizers
@assign_class_id("gc_1144")
@lru_cache(maxsize=None)
def is_claw_free_and_locally_connected(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_1144.html

    @param graph:
    @return:
    """
    return is_claw_free(graph) and is_locally_connected(graph)


# the fisc will be obtained through calls to constituent class recognizers
@assign_class_id("AUTO_1506")
@lru_cache(maxsize=None)
def is_auto_1506(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, co-diamond)-free.

    See https://www.graphclasses.org/classes/AUTO_1506

    Complexity of naïve matching: O(n^4)
    :type graph: networkx.Graph
    """
    return is_co_diamond_free(graph) and is_2k2_free(graph)


# the fisc will be obtained through calls to constituent class recognizers
@assign_class_id("gc_508")
@lru_cache(maxsize=None)
def is_gc_508(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, claw)-free.

    See https://www.graphclasses.org/classes/gc_508

    Complexity of naïve matching: O(n^4)
    :type graph: networkx.Graph
    """
    return is_claw_free(graph) and is_2k2_free(graph)


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
    # computing girth takes too long for large graphs, let's try the naive algo, except we iterate
    # over pairs of edges instead of all 4-tuples of vertices
    c4_deg_seq = array("b", [2, 2, 2, 2])
    # note: the following might contain sets of size 3, but it's probably faster *not* to check
    # their size
    return all(
        degree_sequence(graph.subgraph(set(e + f))) != c4_deg_seq
        for e, f in combinations(graph.edges, 2)
    )


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


@assign_class_id("gc_911")
@lru_cache(maxsize=None)
def is_gc_911(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{4}, triangle)-free.

    See https://www.graphclasses.org/classes/gc_911

    Complexity of naïve matching: O(n^4)
    :type graph: networkx.Graph
    """
    return is_triangle_free(graph) and is_c4_free(graph)


@assign_class_id("AUTO_1467")
@lru_cache(maxsize=None)
def is_auto_1467(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co-claw, co-diamond)-free.

    See https://www.graphclasses.org/classes/AUTO_1467

    Complexity of naïve matching: O(n^4)
    :type graph: networkx.Graph
    """
    return is_co_claw_free(graph) and is_co_diamond_free(graph)


@assign_class_id("AUTO_1499")
@lru_cache(maxsize=None)
def is_auto_1499(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co-claw, co-paw)-free.

    See https://www.graphclasses.org/classes/AUTO_1499

    Complexity of naïve matching: O(n^4)
    :type graph: networkx.Graph
    """
    return is_co_paw_free(graph) and is_co_claw_free(graph)


@assign_class_id("gc_426")
@lru_cache(maxsize=None)
def is_gc_426(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (claw, co-claw)-free.

    See https://www.graphclasses.org/classes/gc_426

    Complexity of naïve matching: O(n^4)
    :type graph: networkx.Graph
    """
    return is_claw_free(graph) and is_co_claw_free(graph)


@assign_class_id("gc_1")
@lru_cache(maxsize=None)
def is_gc_1(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, C_{4})-free.

    See https://www.graphclasses.org/classes/gc_1

    Complexity of naïve matching: O(n^4)
    :type graph: networkx.Graph
    """
    return is_c4_free(graph) and is_2k2_free(graph)


@assign_class_id("gc_1232")
@lru_cache(maxsize=None)
def is_gc_1232(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{4}, claw, diamond)-free.

    See https://www.graphclasses.org/classes/gc_1232

    Complexity of naïve matching: O(n^4)
    :type graph: networkx.Graph
    """
    #      (diamond, claw)      C_{4}
    return is_claw_diamond_free(graph) and is_c4_free(graph)


@assign_class_id("gc_674")
@lru_cache(maxsize=None)
def is_4k1_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is 4K_{1}-free.

    See https://www.graphclasses.org/classes/gc_674

    Complexity of naïve matching: O(n^4)
    :type graph: networkx.Graph
    """
    return is_even_co_clique_free(graph, 4)


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


@assign_class_id("AUTO_1449")
@lru_cache(maxsize=None)
def is_auto_1449(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (4K_{1}, co-claw, co-diamond)-free.

    See https://www.graphclasses.org/classes/AUTO_1449

    Complexity of naïve matching: O(n^4)
    :type graph: networkx.Graph
    """
    return is_co_diamond_free(graph) and is_co_claw_free(graph) and is_4k1_free(graph)


@assign_class_id("AUTO_1501")
@lru_cache(maxsize=None)
def is_auto_1501(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, 4K_{1}, co-claw, co-diamond)-free.

    See https://www.graphclasses.org/classes/AUTO_1501

    Complexity of naïve matching: O(n^4)
    :type graph: networkx.Graph
    """
    return (
        is_co_diamond_free(graph)
        and is_co_claw_free(graph)
        and is_2k2_free(graph)
        and is_4k1_free(graph)
    )


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
    return is_even_clique_free(graph, 4)


@assign_class_id("gc_1367")
@lru_cache(maxsize=None)
def is_k4_free_and_planar(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is K_{4}-free and planar.

    See https://www.graphclasses.org/classes/gc_1367

    Complexity of naïve matching: O(n^4)

    :type graph: networkx.Graph
    """
    return is_planar(graph) and is_even_clique_free(graph, 4)


@assign_fisc(["diamond", "co-diamond"])
@assign_class_id("gc_425")
@lru_cache(maxsize=None)
def is_diamond_co_diamond_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co-diamond, diamond)-free.

    See https://www.graphclasses.org/classes/gc_425

    Complexity of naïve matching: O(n^4)

    :type graph: networkx.Graph
    """
    # co-diamond: for each non edge, go through all edges, and check degree
    # sequence of induced subgraph
    #                     diamond       co-diamond
    forbidden_deg_seqs = (array("b", [3, 3, 2, 2]), array("b", [1, 1, 0, 0]))
    return all(
        degree_sequence(graph.subgraph(set(e + f))) not in forbidden_deg_seqs
        for e in nx.non_edges(graph)
        for f in graph.edges
    )


@assign_fisc(["4K_{1}", "K_{4}"])
@assign_class_id("gc_515")
@lru_cache(maxsize=None)
def is_gc_515(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (4K_{1}, K_{4})-free.

    See https://www.graphclasses.org/classes/gc_515

    Complexity of naïve matching: O(n^4)

    :type graph: networkx.Graph
    """
    return is_4k1_free(graph) and is_k4_free(graph)


@assign_fisc(["P_{4}", "K_{4}"])
@assign_class_id("gc_634")
@lru_cache(maxsize=None)
def is_gc_634(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{4}, P_{4})-free.

    See https://www.graphclasses.org/classes/gc_634

    Complexity of naïve matching: O(n^4)

    :type graph: networkx.Graph
    """
    return is_cograph(graph) and is_k4_free(graph)


@assign_class_id("gc_1304")
@lru_cache(maxsize=None)
def is_gc_1304(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, C_{4}, C_{5}, co-claw, co-diamond)-free.

    See https://www.graphclasses.org/classes/gc_1304

    Complexity of naïve matching: O(n^5)

    :type graph: networkx.Graph
    """
    return is_split(graph) and is_co_claw_free(graph) and is_co_diamond_free(graph)


@assign_class_id("gc_1244")
@lru_cache(maxsize=None)
def is_gc_1244(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{4}, co(P_{3}))-free.

    See https://www.graphclasses.org/classes/gc_1244

    Complexity of naïve matching: O(n^4)

    :type graph: networkx.Graph
    """
    return is_co_p3_free(graph) and is_c4_free(graph)


@assign_class_id("gc_919")
@lru_cache(maxsize=None)
def is_gc_919(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{4}, claw, diamond)-free.

    See https://www.graphclasses.org/classes/gc_919

    Complexity of naïve matching: O(n^4)

    :type graph: networkx.Graph
    """
    return is_claw_diamond_free(graph) and is_k4_free(graph)


@assign_class_id("gc_506")
@lru_cache(maxsize=None)
def is_gc_506(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{4}, K_{4}, claw, diamond)-free.

    See https://www.graphclasses.org/classes/gc_506

    Complexity of naïve matching: O(n^4)

    :type graph: networkx.Graph
    """
    return is_claw_diamond_free(graph) and is_k4_free(graph) and is_c4_free(graph)


@assign_class_id("AUTO_2776")
@lru_cache(maxsize=None)
def is_co_xc11_claw_diamond_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_co_maximum_degree_4(graph) and is_auto_1467(graph)


@assign_class_id("AUTO_2768")
@lru_cache(maxsize=None)
def is_co_cnplus4_co_claw_co_gem_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_co_chordal(graph) and is_co_gem_free(graph) and is_co_claw_free(graph)


# -------------------------------------------------------------------------------------------------
# The following recognizers call another recognizer on the complement of the input graph. Since
# building the complement can be time- and memory-consuming on large instances, and since
# recognizers are loaded in the order in which they appear in a recognizer file, those recognizers
# should stay at the end of the file in the hope that they are not actually needed until we figure
# out a way to bypass the computation of the complement.
# -------------------------------------------------------------------------------------------------
@assign_fisc(
    ["C_{5}", "co(C_{6})", "co(C_{7})", "co(C_{8})"]
)  # partial fisc derived from complement
@assign_class_id("gc_1364")
@lru_cache(maxsize=None)
def is_anti_hole_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    # iterate over co-connected components instead of complementing the whole graph, in the hope
    # that we can thereby stop early
    return all(
        is_hole_free(complement(graph.subgraph(cc)))
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
