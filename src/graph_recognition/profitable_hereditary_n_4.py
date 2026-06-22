"""Anthony Labarre © 2023-2026

This file contains recognizers for profitable hereditary classes, i.e. classes that admit a
forbidden induced subgraph characterization, but can be recognized with a faster-than-naïve
algorithm.

Recognizers in this file have running time O(n^4).

"""

# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
import os
from collections import defaultdict
from functools import lru_cache
from itertools import combinations, product

# ----- Third-party imports -----------------------------------------------------------------------
import networkx as nx
from networkx import connected_components, non_edges

# ----- My imports --------------------------------------------------------------------------------
from graph_recognition.adjacency_matrix import HalfAdjacencyMatrix
from graph_recognition.misc_algo import (
    number_of_common_neighbors,
    degree_sequence,
    co_connected_components, complement_as_adj_mat, number_of_edges, induced_subgraph_degrees, )
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
from graph_recognition.recognizers_n_3 import is_weakly_modular
from graph_recognition.recognizers_utils import (
    current_module_recognizers,
    assign_class_id,
    assign_fisc, assign_inherited_fisc,
)
from graph_recognition.subgraphs import is_h_free


# Auxiliary functions -----------------------------------------------------------------------------
@lru_cache(maxsize=None)
def maximum_matching(graph: nx.Graph) -> dict:
    """
    Returns a matching of maximum cardinality for the input graph.

    Complexity: O(m+n) if graph is bipartite, O(n^3) otherwise. The function checks bipartiteness
    and selects the right algorithm.

    :param graph:
    :return:
    """
    if not graph:
        return dict()

    if is_bipartite(graph):
        # networkx's function crashes on disconnected graphs, so we can't simply return
        # nx.bipartite.maximum_matching(graph)
        result = dict()
        for cc in connected_components(graph):
            result.update(nx.bipartite.maximum_matching(graph.subgraph(cc)))
        return result

    return dict(nx.max_weight_matching(graph, maxcardinality=True))


# Recognizers -------------------------------------------------------------------------------------


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
    return all(number_of_common_neighbors(graph, u, v) <= 2 for u, v in combinations(graph, 2))


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
    return is_h_free(graph, ["co-claw"])


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
    # no way around it: check membership
    return is_h_free(graph, ["claw"])


@assign_fisc(
    ["C_{5}", "C_{6}", "C_{7}", "C_{8}"]
)  # partial since holes include all cycles of length >= 5
@assign_class_id("gc_437")
@lru_cache(maxsize=None)
def is_hole_free(graph: nx.Graph | HalfAdjacencyMatrix) -> bool:
    """
    Returns True if G is hole-free, False otherwise.

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
        The auxiliary process procedure from https://www.cs.uoi.gr/~palios/pubs/D5.pdf used in the
        algorithm that test hole-freeness.

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
    for u in graph:
        in_path[u] = True
        for v, w in graph.edges():
            if graph.has_edge(u, v) and not graph.has_edge(u, w) and not not_in_hole[(u, v, w)]:
                in_path[v] = True
                if process(u, v, w):
                    return False
                in_path[v] = False

        in_path[u] = False

    return True


@assign_inherited_fisc()
@assign_class_id("AUTO_2758")
@lru_cache(maxsize=None)
def is_anti_hole_odd_anti_cycle_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_co_bipartite(graph) and is_anti_hole_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_126")
@lru_cache(maxsize=None)
def is_comparability_and_weakly_chordal(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_126

    @param graph:
    @return:
    """
    return is_comparability(graph) and is_weakly_chordal(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_773")
@lru_cache(maxsize=None)
def is_hole_odd_cycle_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_bipartite(graph) and is_hole_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_1277")
@lru_cache(maxsize=None)
def is_hole_free_and_planar(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_planar(graph) and is_hole_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_14")
@lru_cache(maxsize=None)
def is_weakly_chordal(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_hole_free(graph) and is_anti_hole_free(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_2760")
@lru_cache(maxsize=None)
def is_co_chordal_and_co_claw_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_co_claw_free(graph) and is_co_chordal(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_2129")
@lru_cache(maxsize=None)
def is_co_at_free_and_co_claw_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_co_claw_free(graph) and is_co_at_free(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_2764")
@lru_cache(maxsize=None)
def is_co_bipartite_and_co_claw_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_co_claw_free(graph) and is_co_bipartite(graph)


@assign_inherited_fisc()
@assign_class_id("gc_60")
@lru_cache(maxsize=None)
def is_at_free_and_claw_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_claw_free(graph) and my_is_at_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_525")
@lru_cache(maxsize=None)
def is_bipartite_and_claw_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_claw_free(graph) and is_bipartite(graph)


@assign_inherited_fisc()
@assign_class_id("gc_303")
@lru_cache(maxsize=None)
def is_chordal_and_claw_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_claw_free(graph) and is_chordal(graph)


@assign_inherited_fisc()
@assign_class_id("gc_1292")
@lru_cache(maxsize=None)
def is_claw_free_and_mock_threshold(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_claw_free(graph) and is_mock_threshold(graph)


@assign_inherited_fisc()
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


@assign_inherited_fisc()
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


@assign_inherited_fisc()
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


@assign_inherited_fisc()
@assign_class_id("gc_1144")
@lru_cache(maxsize=None)
def is_claw_free_and_locally_connected(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_1144.html

    @param graph:
    @return:
    """
    return is_locally_connected(graph) and is_claw_free(graph)


@assign_inherited_fisc()
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


@assign_inherited_fisc()
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
    # note: cannot move function to fisc_based_recognizers due to circular import issues
    if nx.girth(graph) > 4:
        return True

    return is_h_free(graph, ["C_{4}"])


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


@assign_inherited_fisc()
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


@assign_inherited_fisc()
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


@assign_inherited_fisc()
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


@assign_inherited_fisc()
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


@assign_inherited_fisc()
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


@assign_inherited_fisc()
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


# note: cannot move to fisc_based_recognizers because of circular import issues
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


@assign_inherited_fisc()
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


@assign_inherited_fisc()
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
            is_2k2_free(graph)
            and is_co_diamond_free(graph)
            and is_co_claw_free(graph)
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
    return is_h_free(graph, ["K_{4}"])


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
    # co-diamond: for each non edge, go through all edges, and check degree sequence of induced
    # subgraph
    #                     diamond       co-diamond
    forbidden_deg_seqs = ([3, 3, 2, 2], [1, 1, 0, 0])
    return all(
        sorted(induced_subgraph_degrees(graph, set(e+f)).values(), reverse=True) not in forbidden_deg_seqs
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


@assign_inherited_fisc()
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


@assign_inherited_fisc()
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


@assign_inherited_fisc()
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


@assign_inherited_fisc()
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


@assign_inherited_fisc()
@assign_class_id("AUTO_2776")
@lru_cache(maxsize=None)
def is_co_xc11_claw_diamond_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_co_maximum_degree_4(graph) and is_auto_1467(graph)


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
@assign_class_id("gc_1386")
@lru_cache(maxsize=None)
def is_weakly_bridged(graph: nx.Graph) -> bool:
    """
    Equivalent to C_{4}-free ∩ weakly modular.

    https://www.graphclasses.org/classes/gc_1386.html

    :param graph:
    :return:
    """
    return is_c4_free(graph) and is_weakly_modular(graph)


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
        is_hole_free(complement_as_adj_mat(graph, cc))
        for cc in co_connected_components(graph)
    )


@assign_fisc(["co-diamond"])
@assign_class_id("AUTO_77")
@lru_cache(maxsize=None)
def is_co_diamond_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is co-diamond-free.

    See https://www.graphclasses.org/classes/AUTO_77

    Complexity: O(n^4).

    :type graph: networkx.Graph
    """
    # this naïve search outperforms the Glasgow Subgraph Solver on large graphs
    for (a, b), (c, d) in product(graph.edges, non_edges(graph)):
        if (not graph.has_edge(a, c) and not graph.has_edge(a, d) and not graph.has_edge(b, c)
                and not graph.has_edge(b, d)):
            return False
    return True


@assign_inherited_fisc()
@assign_class_id("AUTO_2774")
@lru_cache(maxsize=None)
def is_co_chordal_and_co_diamond_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_co_diamond_free(graph) and is_co_chordal(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_1939")
@lru_cache(maxsize=None)
def is_p4_co_diamond_co_paw_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{4}, co-diamond, co-paw)-free.

    See https://www.graphclasses.org/classes/AUTO_1939

    Complexity: O(n^2) < O(n^4) (naïve)

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

    Complexity: O(n^2) < O(n^4) (naïve)

    @param graph:
    @return:
    """
    return (
            is_cograph(graph)
            and is_2k2_free(graph)
            and is_co_diamond_free(graph)
            and is_co_paw_free(graph)
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
