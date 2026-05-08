"""Anthony Labarre © 2023-2026

This file contains all naïve recognizers for those graph classes in ISGCI that admit a FISC
(forbidden induced subgraph characterisation).

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

# ----- Third-party imports -----------------------------------------------------------------------
import networkx as nx

# ----- My imports --------------------------------------------------------------------------------
from graph_recognition.adjacency_matrix import HalfAdjacencyMatrix
from graph_recognition.domination import has_dominating_set_of_size_at_most_2, has_dominating_triangle_or_p3
from graph_recognition.misc_algo import (
    is_h_u_k1_free,
    is_h_u_2k1_free,
    is_odd_clique_free,
    is_odd_co_clique_free,
    must_contain_a_clique_of_size,
    degree_sequence,
    must_contain_an_independent_set_of_size, is_connected, complement_as_adj_mat, )
from graph_recognition.profitable_hereditary_n import (
    is_cograph,
    is_p3_triangle_free,
    is_split,
    is_p3_free,
    is_2k2_free, is_forest,
)
from graph_recognition.profitable_hereditary_n_2 import (
    is_co_diamond_free,
    is_co_paw_free,
    is_co_gem_free,
)
from graph_recognition.profitable_hereditary_n_3 import (
    is_3k1_free,
    is_triangle_free,
    is_girth_at_least_9,
    is_paw_free,
    is_p2up4_free,
    is_co_p3_free,
)
from graph_recognition.profitable_hereditary_n_4 import (
    is_co_claw_free,
    is_claw_free,
    is_c4_free,
    is_k4_free,
    is_c4_diamond_free,
    is_4k1_free,
    is_anti_hole_free,
    is_hole_free,
)
from graph_recognition.profitable_hereditary_n_5 import is_2p3_free, is_k2_u_k3_free
from graph_recognition.recognizers_utils import (
    assign_class_id,
    current_module_recognizers,
    assign_fisc, assign_inherited_fisc,
)
from graph_recognition.subgraphs import is_h_free


# Auxiliary functions -----------------------------------------------------------------------------
# The following functions are not proper recognizers, but are meant to be used by recognizers in
# this file.
@lru_cache(maxsize=None)
def is_k_clique_free(graph: nx.Graph, k: int) -> bool:
    """
    Returns True iff graph has no clique of size k.

    @param graph:
    @param k:
    @return:
    """
    if must_contain_a_clique_of_size(graph, k):
        return False

    # since vertices in a k-clique have degree k-1, restrict our search to vertices of degree at
    # least k-1
    ds = degree_sequence(graph)
    if ds and ds[-1] <= k:  # don't create a useless copy if all vertices already have degree > k
        graph = graph.subgraph(v for v, d in graph.degree if d > k)
        # check criterion again, since graph has changed (we can afford it, it takes time O(1))
        if must_contain_a_clique_of_size(graph, k):
            return False

    # graph is k-clique-free iff the neighborhood of each vertex of degree >= k-1 is
    # (k-1)-clique-free
    return is_h_free(graph, ["K_{" + str(k) + "}"])


# Recognizers -------------------------------------------------------------------------------------
# All recognizers for patterns on at most 4 vertices ----------------------------------------------
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
    return is_h_free(graph, ["diamond"])


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
            and is_c4_free(graph)
            and is_diamond_free(graph)
            and is_paw_free(graph)
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


# All recognizers for patterns on at most 5 vertices ----------------------------------------------
@assign_fisc(["P"])
@assign_class_id("gc_814")
@lru_cache(maxsize=None)
def is_p_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is P-free.

    See https://www.graphclasses.org/classes/gc_814

    Complexity of naïve matching: O(n^5)

    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["P"])


@assign_fisc(["co(P)"])
@assign_class_id("AUTO_2")
@lru_cache(maxsize=None)
def is_co_p_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is co(P)-free.

    See https://www.graphclasses.org/classes/AUTO_2

    Complexity of naïve matching: O(n^5)

    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["co(P)"])


@assign_fisc(["C_{5}"])
@assign_class_id("gc_359")
@lru_cache(maxsize=None)
def is_c5_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is C_{5}-free.

    See https://www.graphclasses.org/classes/gc_359

    Complexity of naïve matching: O(n^5)

    :type graph: networkx.Graph
    """
    # if graph has a C_5 then it has a P_4, so if graph is a cograph it has no P_4 and therefore no
    # C_5
    if is_cograph(graph):
        return True

    return is_h_free(graph, ["C_{5}"])


@assign_fisc(["P_{5}"])
@assign_class_id("gc_396")
@lru_cache(maxsize=None)
def is_p5_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is P_{5}-free.

    See https://www.graphclasses.org/classes/gc_396

    Complexity of naïve matching: O(n^5)

    :type graph: networkx.Graph
    """
    # if graph has no P_{4}, then it has no P_{5}
    if is_cograph(graph):
        return True

    # every connected P_{5}-free graph has a dominating clique of size <= 3 or a dominating P_{3}
    # see https://doi.org/10.4230/LIPIcs.ISAAC.2017.16 page 16:4
    if is_connected(graph) and (
            not has_dominating_set_of_size_at_most_2(graph) or
            not has_dominating_triangle_or_p3(graph)
    ):
        return False

    return is_h_free(graph, ["P_{5}"])


@assign_fisc(["co(K_{1,4})"])
@assign_class_id("gc_673")
@lru_cache(maxsize=None)
def is_co_k14_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is co(K_{1, 4})-free.

    See https://www.graphclasses.org/classes/gc_673

    Complexity of naïve matching: O(n^5)

    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["co(K_{1,4})"])


@assign_fisc(["co-fork"])
@assign_class_id("AUTO_3")
@lru_cache(maxsize=None)
def is_co_fork_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is co-fork-free.

    See https://www.graphclasses.org/classes/AUTO_3

    Complexity of naïve matching: O(n^5)

    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["co-fork"])


@assign_fisc(["house"])
@assign_class_id("gc_361")
@lru_cache(maxsize=None)
def is_house_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is house-free.

    See https://www.graphclasses.org/classes/gc_361

    Complexity of naïve matching: O(n^5)

    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["house"])


@assign_fisc(["gem"])
@assign_class_id("gc_354")
@lru_cache(maxsize=None)
def is_gem_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is gem-free.

    See https://www.graphclasses.org/classes/gc_354

    Complexity of naïve matching: O(n^5)

    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["gem"])


@assign_fisc(["K_{2,3}"])
@assign_class_id("gc_362")
@lru_cache(maxsize=None)
def is_k23_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is K_{2, 3}-free.

    See https://www.graphclasses.org/classes/gc_362

    Complexity of naïve matching: O(n^5)

    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["K_{2,3}"])


@assign_fisc(["bull"])
@assign_class_id("gc_372")
@lru_cache(maxsize=None)
def is_bull_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is bull-free.

    See https://www.graphclasses.org/classes/gc_372

    Complexity of naïve matching: O(n^5)

    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["bull"])


@assign_fisc(["fork"])
@assign_class_id("gc_391")
@lru_cache(maxsize=None)
def is_fork_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is fork-free.

    See https://www.graphclasses.org/classes/gc_391

    Complexity of naïve matching: O(n^5)

    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["fork"])


@assign_fisc(["K_{1,4}"])
@assign_class_id("gc_388")
@lru_cache(maxsize=None)
def is_k14_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is K_{1, 4}-free.

    See https://www.graphclasses.org/classes/gc_388

    Complexity of naïve matching: O(n^5)

    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["K_{1,4}"])


@assign_fisc(["co-cricket", "house"])
@assign_class_id("AUTO_1515")
@lru_cache(maxsize=None)
def is_auto_1515(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co-cricket, house)-free.

    See https://www.graphclasses.org/classes/AUTO_1515

    Complexity of naïve matching: O(n^5)

    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["co-cricket"]) and is_house_free(graph)


@assign_fisc(["K_{5}"])
@assign_class_id("AUTO_136")
@lru_cache(maxsize=None)
def is_auto_136(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is K_{5}-free.

    See https://www.graphclasses.org/classes/AUTO_136

    Complexity of naïve matching: O(n^5)

    :type graph: networkx.Graph
    """
    return is_k_clique_free(graph, 5)


@assign_class_id("gc_1377")
@lru_cache(maxsize=None)
def is_gc_1377(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is 5K_{1}-free.

    See https://www.graphclasses.org/classes/gc_1377

    Complexity of naïve matching: O(n^5)

    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["5K_{1}"])


@assign_class_id("gc_430")
@lru_cache(maxsize=None)
def is_gc_430(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{4}, P_{5})-free.

    See https://www.graphclasses.org/classes/gc_430

    Complexity of naïve matching: O(n^5)

    :type graph: networkx.Graph
    """
    return is_c4_free(graph) and is_p5_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_463")
@lru_cache(maxsize=None)
def is_gc_463(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{5}, co-fork)-free.

    See https://www.graphclasses.org/classes/gc_463

    Complexity of naïve matching: O(n^5)

    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_co_fork_free(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_1521")
@lru_cache(maxsize=None)
def is_auto_1521(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co-diamond, house)-free.

    See https://www.graphclasses.org/classes/AUTO_1521

    Complexity of naïve matching: O(n^5)

    :type graph: networkx.Graph
    """
    return is_co_diamond_free(graph) and is_house_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_574")
@lru_cache(maxsize=None)
def is_gc_574(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (bull, house)-free.

    See https://www.graphclasses.org/classes/gc_574

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_bull_free(graph) and is_house_free(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_1528")
@lru_cache(maxsize=None)
def is_auto_1528(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (bull, co-fork)-free.

    See https://www.graphclasses.org/classes/AUTO_1528

    Complexity of naïve matching: O(n^5)

    :type graph: networkx.Graph
    """
    return is_bull_free(graph) and is_co_fork_free(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_2117")
@lru_cache(maxsize=None)
def is_auto_2117(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co(W_{4}), co-gem)-free.

    See https://www.graphclasses.org/classes/AUTO_2117

    Complexity of naïve matching: O(n^5)

    :type graph: networkx.Graph
    """
    # co(W_{4}) = 2K_{2} U K_{1} = K_{2} U co(P_{3})
    # return is_co_gem_free(graph) and is_h_u_k1_free(graph, is_2k2_free)
    return is_co_gem_free(graph) and is_h_u_2k1_free(graph, is_co_p3_free)


@assign_inherited_fisc()
@assign_class_id("gc_628")
@lru_cache(maxsize=None)
def is_gc_628(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{2, 3}, diamond)-free.

    See https://www.graphclasses.org/classes/gc_628

    Complexity of naïve matching: O(n^5)

    :type graph: networkx.Graph
    """
    return is_diamond_free(graph) and is_k23_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_427")
@lru_cache(maxsize=None)
def is_gc_427(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{5}, cricket)-free.

    See https://www.graphclasses.org/classes/gc_427

    Complexity of naïve matching: O(n^5)

    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_h_free(graph, ["cricket"])


@assign_inherited_fisc()
@assign_class_id("gc_402")
@lru_cache(maxsize=None)
def is_gc_402(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{5}, house)-free.

    See https://www.graphclasses.org/classes/gc_402

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_house_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_403")
@lru_cache(maxsize=None)
def is_gc_403(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{2, 3}, P_{5})-free.

    See https://www.graphclasses.org/classes/gc_403

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_k23_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_408")
@lru_cache(maxsize=None)
def is_gc_408(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{1, 4}, P_{5})-free.

    See https://www.graphclasses.org/classes/gc_408

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_k14_free(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_1472")
@lru_cache(maxsize=None)
def is_auto_1472(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (3K_{1}, house)-free.

    See https://www.graphclasses.org/classes/AUTO_1472

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_3k1_free(graph) and is_house_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_632")
@lru_cache(maxsize=None)
def is_gc_632(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (fork, triangle)-free.

    See https://www.graphclasses.org/classes/gc_632

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_triangle_free(graph) and is_fork_free(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_1520")
@lru_cache(maxsize=None)
def is_auto_1520(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co(P), house)-free.

    See https://www.graphclasses.org/classes/AUTO_1520

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_house_free(graph) and is_co_p_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_510")
@lru_cache(maxsize=None)
def is_gc_510(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co-gem, gem)-free.

    See https://www.graphclasses.org/classes/gc_510

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_co_gem_free(graph) and is_gem_free(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_1728")
@lru_cache(maxsize=None)
def is_auto_1728(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co-butterfly, co-claw)-free.

    See https://www.graphclasses.org/classes/AUTO_1728

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_co_claw_free(graph) and is_h_free(graph, ["co-butterfly"])


@assign_inherited_fisc()
@assign_class_id("gc_413")
@lru_cache(maxsize=None)
def is_gc_413(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{1, 4}, diamond)-free.

    See https://www.graphclasses.org/classes/gc_413

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_diamond_free(graph) and is_k14_free(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_1522")
@lru_cache(maxsize=None)
def is_auto_1522(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co(K_{1, 4}), house)-free.

    See https://www.graphclasses.org/classes/AUTO_1522

    Complexity of naïve matching: O(n^5)

    :type graph: networkx.Graph
    """
    return is_co_k14_free(graph) and is_house_free(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_1481")
@lru_cache(maxsize=None)
def is_auto_1481(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (3K_{1}, co-fork)-free.

    See https://www.graphclasses.org/classes/AUTO_1481

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_3k1_free(graph) and is_co_fork_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_367")
@lru_cache(maxsize=None)
def is_gc_367(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{4}, C_{5})-free.

    See https://www.graphclasses.org/classes/gc_367

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_c4_free(graph) and is_c5_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_812")
@lru_cache(maxsize=None)
def is_gc_812(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{5}, co(P_{2} U P_{3}))-free.

    See https://www.graphclasses.org/classes/gc_812

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_h_free(graph, ["co(P_{2} U P_{3})"])


@assign_inherited_fisc()
@assign_class_id("AUTO_1512")
@lru_cache(maxsize=None)
def is_auto_1512(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, house)-free.

    See https://www.graphclasses.org/classes/AUTO_1512

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_2k2_free(graph) and is_house_free(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_1525")
@lru_cache(maxsize=None)
def is_auto_1525(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{2} U K_{3}, house)-free.

    See https://www.graphclasses.org/classes/AUTO_1525

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_k2_u_k3_free(graph) and is_house_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_409")
@lru_cache(maxsize=None)
def is_gc_409(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{5}, diamond)-free.

    See https://www.graphclasses.org/classes/gc_409

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_diamond_free(graph) and is_p5_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_572")
@lru_cache(maxsize=None)
def is_p5_bull_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{5}, bull)-free.

    See https://www.graphclasses.org/classes/gc_572

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_bull_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_1275")
@lru_cache(maxsize=None)
def is_gc_1275(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, C_{5})-free.

    See https://www.graphclasses.org/classes/gc_1275

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_2k2_free(graph) and is_c5_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_669")
@lru_cache(maxsize=None)
def is_gc_669(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, P_{5})-free.

    See https://www.graphclasses.org/classes/gc_669

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_c5_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_670")
@lru_cache(maxsize=None)
def is_gc_670(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{5}, triangle)-free.

    See https://www.graphclasses.org/classes/gc_670

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_triangle_free(graph) and is_p5_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_1213")
@lru_cache(maxsize=None)
def is_gc_1213(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (butterfly, claw)-free.

    See https://www.graphclasses.org/classes/gc_1213

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_claw_free(graph) and is_h_free(graph, ["butterfly"])


@assign_inherited_fisc()
@assign_class_id("gc_671")
@lru_cache(maxsize=None)
def is_gc_671(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{4}, P_{5})-free.

    See https://www.graphclasses.org/classes/gc_671

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_k4_free(graph) and is_p5_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_871")
@lru_cache(maxsize=None)
def is_gc_871(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (butterfly, gem)-free.

    See https://www.graphclasses.org/classes/gc_871

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_gem_free(graph) and is_h_free(graph, ["butterfly"])


@assign_inherited_fisc()
@assign_class_id("gc_466")
@lru_cache(maxsize=None)
def is_gc_466(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{5}, gem)-free.

    See https://www.graphclasses.org/classes/gc_466

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_gem_free(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_1473")
@lru_cache(maxsize=None)
def is_auto_1473(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, house)-free.

    See https://www.graphclasses.org/classes/AUTO_1473

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_c5_free(graph) and is_house_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_439")
@lru_cache(maxsize=None)
def is_gc_439(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{5}, fork)-free.

    See https://www.graphclasses.org/classes/gc_439

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_h_free(graph, ["fork"])


@assign_inherited_fisc()
@assign_class_id("AUTO_1462")
@lru_cache(maxsize=None)
def is_house_p2_u_p3_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{2} U P_{3}, house)-free.

    See https://www.graphclasses.org/classes/AUTO_1462

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["P_{2} U P_{3}"]) and is_house_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_700")
@lru_cache(maxsize=None)
def is_gc_700(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (W_{4}, gem)-free.

    See https://www.graphclasses.org/classes/gc_700

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_gem_free(graph) and is_h_free(graph, ["W_{4}"])


@assign_inherited_fisc()
@assign_class_id("AUTO_1448")
@lru_cache(maxsize=None)
def is_auto_1448(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co(K_{1, 4}), co-paw)-free.

    See https://www.graphclasses.org/classes/AUTO_1448

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_co_paw_free(graph) and is_co_k14_free(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_1762")
@lru_cache(maxsize=None)
def is_auto_1762(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (4K_{1}, gem)-free.

    See https://www.graphclasses.org/classes/AUTO_1762

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_gem_free(graph) and is_4k1_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_920")
@lru_cache(maxsize=None)
def is_gc_920(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{1, 4}, paw)-free.

    See https://www.graphclasses.org/classes/gc_920

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_paw_free(graph) and is_k14_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_410")
@lru_cache(maxsize=None)
def is_gc_410(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P, P_{5})-free.

    See https://www.graphclasses.org/classes/gc_410

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_h_free(graph, ["P"])


@assign_inherited_fisc()
@assign_class_id("gc_438")
@lru_cache(maxsize=None)
def is_gc_438(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co(P), fork)-free.

    See https://www.graphclasses.org/classes/gc_438

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["fork", "co(P)"])


@assign_class_id("gc_397")
@lru_cache(maxsize=None)
def is_gc_397(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (bull, fork)-free.

    See https://www.graphclasses.org/classes/gc_397

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["fork", "bull"])


@assign_inherited_fisc()
@assign_class_id("AUTO_1510")
@lru_cache(maxsize=None)
def is_auto_1510(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P, co-fork)-free.

    See https://www.graphclasses.org/classes/AUTO_1510

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_p_free(graph) and is_co_fork_free(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_1523")
@lru_cache(maxsize=None)
def is_auto_1523(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co-claw, house)-free.

    See https://www.graphclasses.org/classes/AUTO_1523

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_co_claw_free(graph) and is_h_free(graph, ["house"])


@assign_inherited_fisc()
@assign_class_id("AUTO_1509")
@lru_cache(maxsize=None)
def is_auto_1509(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co-fork, house)-free.

    See https://www.graphclasses.org/classes/AUTO_1509

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_house_free(graph) and is_co_fork_free(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_1508")
@lru_cache(maxsize=None)
def is_auto_1508(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (fork, house)-free.

    See https://www.graphclasses.org/classes/AUTO_1508

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_fork_free(graph) and is_house_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_407")
@lru_cache(maxsize=None)
def is_gc_407(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{5}, claw)-free.

    See https://www.graphclasses.org/classes/gc_407

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_claw_free(graph) and is_p5_free(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_1453")
@lru_cache(maxsize=None)
def is_auto_1453(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co-butterfly, co-gem)-free.

    See https://www.graphclasses.org/classes/AUTO_1453

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_co_gem_free(graph) and is_h_free(graph, ["co-butterfly"])


@assign_inherited_fisc()
@assign_class_id("AUTO_1518")
@lru_cache(maxsize=None)
def is_auto_1518(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co(K_{1, 4}), co-diamond)-free.

    See https://www.graphclasses.org/classes/AUTO_1518

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_co_diamond_free(graph) and is_co_k14_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_1233")
@lru_cache(maxsize=None)
def is_gc_1233(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{4}, co-gem)-free.

    See https://www.graphclasses.org/classes/gc_1233

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_co_gem_free(graph) and is_k4_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_566")
@lru_cache(maxsize=None)
def is_gc_566(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (W_{4}, claw)-free.

    See https://www.graphclasses.org/classes/gc_566

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_claw_free(graph) and is_h_free(graph, ["W_{4}"])


@assign_inherited_fisc()
@assign_class_id("AUTO_1507")
@lru_cache(maxsize=None)
def is_auto_1507(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co-gem, house)-free.

    See https://www.graphclasses.org/classes/AUTO_1507

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_co_gem_free(graph) and is_house_free(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_1471")
@lru_cache(maxsize=None)
def is_auto_1471(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (4K_{1}, house)-free.

    See https://www.graphclasses.org/classes/AUTO_1471

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_4k1_free(graph) and is_house_free(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_2094")
@lru_cache(maxsize=None)
def is_auto_2094(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co(W_{4}), co-claw)-free.

    See https://www.graphclasses.org/classes/AUTO_2094

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_co_claw_free(graph) and is_h_u_k1_free(graph, is_2k2_free)


@assign_inherited_fisc()
@assign_class_id("gc_854")
@lru_cache(maxsize=None)
def is_gc_854(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{2, 3}, P_{4}, co-butterfly)-free.

    See https://www.graphclasses.org/classes/gc_854

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_cograph(graph) and is_k23_free(graph) and is_h_free(graph, ["co-butterfly"])


@assign_inherited_fisc()
@assign_class_id("gc_478")
@lru_cache(maxsize=None)
def is_gc_478(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{5}, bull, house)-free.

    See https://www.graphclasses.org/classes/gc_478

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_bull_free(graph) and is_house_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_518")
@lru_cache(maxsize=None)
def is_gc_518(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, co-gem, gem)-free.

    See https://www.graphclasses.org/classes/gc_518

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_co_gem_free(graph) and is_c5_free(graph) and is_gem_free(graph)


@assign_class_id("gc_519")
@lru_cache(maxsize=None)
def is_gc_519(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (bull, co-gem, gem)-free.

    See https://www.graphclasses.org/classes/gc_519

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_co_gem_free(graph) and is_bull_free(graph) and is_gem_free(graph)


@assign_class_id("AUTO_1502")
@lru_cache(maxsize=None)
def is_auto_1502(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{5}, bull, co-fork)-free.

    See https://www.graphclasses.org/classes/AUTO_1502

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_bull_free(graph) and is_co_fork_free(graph)


@assign_class_id("gc_517")
@lru_cache(maxsize=None)
def is_gc_517(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, P_{5}, gem)-free.

    See https://www.graphclasses.org/classes/gc_517

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_c5_free(graph) and is_gem_free(graph)


@assign_class_id("gc_404")
@lru_cache(maxsize=None)
def is_gc_404(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{2, 3}, P, P_{5})-free.

    See https://www.graphclasses.org/classes/gc_404

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_k23_free(graph) and is_h_free(graph, ["P"])


@assign_class_id("AUTO_1454")
@lru_cache(maxsize=None)
def is_auto_1454(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{2} U K_{3}, P_{4}, butterfly)-free.

    See https://www.graphclasses.org/classes/AUTO_1454

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return (
            is_cograph(graph) and is_k2_u_k3_free(graph) and is_h_free(graph, ["butterfly"])
    )


@assign_class_id("gc_477")
@lru_cache(maxsize=None)
def is_gc_477(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (bull, fork, house)-free.

    See https://www.graphclasses.org/classes/gc_477

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_fork_free(graph) and is_bull_free(graph) and is_house_free(graph)


@assign_class_id("gc_475")
@lru_cache(maxsize=None)
def is_gc_475(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (bull, fork, gem)-free.

    See https://www.graphclasses.org/classes/gc_475

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["fork", "bull", "gem"])


@assign_class_id("AUTO_1504")
@lru_cache(maxsize=None)
def is_auto_1504(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (bull, co-fork, co-gem)-free.

    See https://www.graphclasses.org/classes/AUTO_1504

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_co_gem_free(graph) and is_bull_free(graph) and is_co_fork_free(graph)


@assign_class_id("AUTO_1513")
@lru_cache(maxsize=None)
def is_auto_1513(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, P_{2} U P_{3}, house)-free.

    See https://www.graphclasses.org/classes/AUTO_1513

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_house_p2_u_p3_free(graph) and is_c5_free(graph)


@assign_class_id("gc_480")
@lru_cache(maxsize=None)
def is_gc_480(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{5}, fork, house)-free.

    See https://www.graphclasses.org/classes/gc_480

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_fork_free(graph) and is_house_free(graph)


@assign_class_id("AUTO_2074")
@lru_cache(maxsize=None)
def is_auto_2074(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, P_{4}, co-dart)-free.

    See https://www.graphclasses.org/classes/AUTO_2074

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_cograph(graph) and is_2k2_free(graph) and is_h_free(graph, ["co-dart"])


@assign_class_id("gc_308")
@lru_cache(maxsize=None)
def is_gc_308(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{5}, co-fork, house)-free.

    See https://www.graphclasses.org/classes/gc_308

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_house_free(graph) and is_co_fork_free(graph)


@assign_class_id("gc_326")
@lru_cache(maxsize=None)
def is_gc_326(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{4}, P_{4}, dart)-free.

    See https://www.graphclasses.org/classes/gc_326

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_cograph(graph) and is_c4_free(graph) and is_h_free(graph, ["dart"])


@assign_class_id("gc_474")
@lru_cache(maxsize=None)
def is_gc_474(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co(P), fork, gem)-free.

    See https://www.graphclasses.org/classes/gc_474

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["gem", "fork", "co(P)"])


@assign_class_id("gc_429")
@lru_cache(maxsize=None)
def is_gc_429(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, P_{5}, co(P_{2} U P_{3}))-free.

    See https://www.graphclasses.org/classes/gc_429

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return (
            is_p5_free(graph)
            and is_c5_free(graph)
            and is_h_free(graph, ["co(P_{2} U P_{3})"])
    )


@assign_class_id("AUTO_2071")
@lru_cache(maxsize=None)
def is_auto_2071(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co(W_{4}), co-claw, co-gem)-free.

    See https://www.graphclasses.org/classes/AUTO_2071

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_co_gem_free(graph) and is_auto_2094(graph)


@assign_fisc(["claw", "W_{4}", "gem"])
@assign_class_id("gc_180")
@lru_cache(maxsize=None)
def is_gc_180(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (W_{4}, claw, gem)-free.

    See https://www.graphclasses.org/classes/gc_180

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["claw", "W_{4}", "gem"])


@assign_class_id("gc_516")
@lru_cache(maxsize=None)
def is_gc_516(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{5}, co(P), gem)-free.

    See https://www.graphclasses.org/classes/gc_516

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_h_free(graph, ["gem", "co(P)"])


@assign_class_id("AUTO_1503")
@lru_cache(maxsize=None)
def is_auto_1503(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P, P_{5}, co-fork)-free.

    See https://www.graphclasses.org/classes/AUTO_1503

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_p_free(graph) and is_co_fork_free(graph)


@assign_class_id("gc_398")
@lru_cache(maxsize=None)
def is_gc_398(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (bull, co-fork, fork)-free.

    See https://www.graphclasses.org/classes/gc_398

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_fork_free(graph) and is_co_fork_free(graph) and is_bull_free(graph)


@assign_class_id("gc_662")
@lru_cache(maxsize=None)
def is_gc_662(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (3K_{1}, C_{4}, C_{5})-free.

    See https://www.graphclasses.org/classes/gc_662

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_3k1_free(graph) and is_c4_free(graph) and is_c5_free(graph)


@assign_class_id("gc_268")
@lru_cache(maxsize=None)
def is_gc_268(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, P_{5}, house)-free.

    See https://www.graphclasses.org/classes/gc_268

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_c5_free(graph) and is_house_free(graph)


@assign_class_id("AUTO_1496")
@lru_cache(maxsize=None)
def is_auto_1496(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P, co-gem, house)-free.

    See https://www.graphclasses.org/classes/AUTO_1496

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_co_gem_free(graph) and is_p_free(graph) and is_house_free(graph)


@assign_class_id("AUTO_1495")
@lru_cache(maxsize=None)
def is_auto_1495(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, co-gem, house)-free.

    See https://www.graphclasses.org/classes/AUTO_1495

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_co_gem_free(graph) and is_c5_free(graph) and is_house_free(graph)


@assign_class_id("gc_476")
@lru_cache(maxsize=None)
def is_gc_476(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co(P), fork, house)-free.

    See https://www.graphclasses.org/classes/gc_476

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_fork_free(graph) and is_house_free(graph) and is_co_p_free(graph)


@assign_class_id("AUTO_1505")
@lru_cache(maxsize=None)
def is_auto_1505(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P, co-fork, co-gem)-free.

    See https://www.graphclasses.org/classes/AUTO_1505

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_co_gem_free(graph) and is_p_free(graph) and is_co_fork_free(graph)


@assign_class_id("AUTO_1524")
@lru_cache(maxsize=None)
def is_auto_1524(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{2} U K_{3}, co(P), house)-free.

    See https://www.graphclasses.org/classes/AUTO_1524

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_k2_u_k3_free(graph) and is_house_free(graph) and is_co_p_free(graph)


@assign_class_id("AUTO_1533")
@lru_cache(maxsize=None)
def is_auto_1533(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, P_{5}, co(P), house)-free.

    See https://www.graphclasses.org/classes/AUTO_1533

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return (
            is_p5_free(graph)
            and is_c5_free(graph)
            and is_house_free(graph)
            and is_co_p_free(graph)
    )


@assign_class_id("gc_420")
@lru_cache(maxsize=None)
def is_gc_420(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{1, 4}, P, P_{5}, fork)-free.

    See https://www.graphclasses.org/classes/gc_420

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_k14_free(graph) and is_h_free(graph, ["P", "fork"])


@assign_class_id("gc_917")
@lru_cache(maxsize=None)
def is_gc_917(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{4}, C_{5}, K_{4}, diamond)-free.

    See https://www.graphclasses.org/classes/gc_917

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_c4_diamond_free(graph) and is_h_free(graph, ["K_{4}", "C_{5}"])


@assign_class_id("gc_1303")
@lru_cache(maxsize=None)
def is_gc_1303(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (3K_{1}, C_{5}, butterfly, diamond)-free.

    See https://www.graphclasses.org/classes/gc_1303

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_3k1_free(graph) and is_h_free(graph, ["diamond", "C_{5}", "butterfly"])


@assign_class_id("AUTO_1450")
@lru_cache(maxsize=None)
def is_auto_1450(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, 4K_{1}, C_{5}, co-diamond)-free.

    See https://www.graphclasses.org/classes/AUTO_1450

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return (
            is_2k2_free(graph)
            and is_4k1_free(graph)
            and is_co_diamond_free(graph)
            and is_h_free(graph, ["C_{5}"])
    )


@assign_class_id("AUTO_1516")
@lru_cache(maxsize=None)
def is_auto_1516(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P, co-butterfly, co-fork, co-gem)-free.

    See https://www.graphclasses.org/classes/AUTO_1516

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return (
            is_co_gem_free(graph)
            and is_h_free(graph, ["co-butterfly"])
            and is_p_free(graph)
            and is_co_fork_free(graph)
    )


@assign_class_id("gc_479")
@lru_cache(maxsize=None)
def is_gc_479(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P, co(P), co-fork, fork)-free.

    See https://www.graphclasses.org/classes/gc_479

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return (
            is_p_free(graph)
            and is_co_p_free(graph)
            and is_fork_free(graph)
            and is_co_fork_free(graph)
    )


@assign_class_id("gc_224")
@lru_cache(maxsize=None)
def is_gc_224(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, P, P_{5}, house)-free.

    See https://www.graphclasses.org/classes/gc_224

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_h_free(graph, ["P", "C_{5}", "house"])


@assign_class_id("gc_421")
@lru_cache(maxsize=None)
def is_gc_421(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co(P), butterfly, fork, gem)-free.

    See https://www.graphclasses.org/classes/gc_421

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_gem_free(graph) and is_h_free(graph, ["fork", "butterfly", "co(P)"])


@assign_class_id("gc_520")
@lru_cache(maxsize=None)
def is_gc_520(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, bull, co-gem, gem)-free.

    See https://www.graphclasses.org/classes/gc_520

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_co_gem_free(graph) and is_h_free(graph, ["C_{5}", "bull", "gem"])


@assign_class_id("AUTO_1517")
@lru_cache(maxsize=None)
def is_auto_1517(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co(K_{1, 4}), co(P), co-fork, house)-free.

    See https://www.graphclasses.org/classes/AUTO_1517

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_co_k14_free(graph) and is_h_free(graph, ["co-fork", "house", "co(P)"])


@assign_class_id("gc_511")
@lru_cache(maxsize=None)
def is_gc_511(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, P, P_{5}, co(P), house)-free.

    See https://www.graphclasses.org/classes/gc_511

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_h_free(graph, ["C_{5}", "house", "P", "co(P)"])


@assign_class_id("gc_189")
@lru_cache(maxsize=None)
def is_gc_189(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P, P_{5}, co(P), co-fork, fork, house)-free.

    See https://www.graphclasses.org/classes/gc_189

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_h_free(
        graph, ["house", "P", "co(P)", "fork", "co-fork"]
    )


@assign_class_id("gc_512")
@lru_cache(maxsize=None)
def is_gc_512(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, P_{5}, co(P), co-fork, co-gem, fork)-free.

    See https://www.graphclasses.org/classes/gc_512

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return (
            is_co_gem_free(graph)
            and is_p5_free(graph)
            and is_h_free(graph, ["C_{5}", "co(P)", "fork", "co-fork"])
    )


@assign_class_id("AUTO_1498")
@lru_cache(maxsize=None)
def is_auto_1498(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, P, co-fork, fork, gem, house)-free.

    See https://www.graphclasses.org/classes/AUTO_1498

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["C_{5}", "house", "P", "gem", "fork", "co-fork"])


@assign_class_id("gc_24")
@lru_cache(maxsize=None)
def is_gc_24(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, P, P_{5}, co(P), co-fork, fork,
    house)-free.

    See https://www.graphclasses.org/classes/gc_24

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_h_free(
        graph, ["C_{5}", "house", "P", "co(P)", "fork", "co-fork"]
    )


@assign_class_id("AUTO_1497")
@lru_cache(maxsize=None)
def is_auto_1497(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, P, co(P), bull, co-fork, gem, house)-free.

    See https://www.graphclasses.org/classes/AUTO_1497

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["C_{5}", "house", "P", "co(P)", "gem", "bull", "co-fork"])


@assign_class_id("gc_513")
@lru_cache(maxsize=None)
def is_gc_513(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, P, P_{5}, co(P), bull, co-gem, fork)-free.

    See https://www.graphclasses.org/classes/gc_513

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return (
            is_co_gem_free(graph)
            and is_p5_free(graph)
            and is_h_free(graph, ["C_{5}", "P", "co(P)", "fork", "bull"])
    )


@assign_class_id("gc_1359")
@lru_cache(maxsize=None)
def is_gc_1359(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{3} U 2K_{1}, co(K_{3} U 2K_{1}), bull, co-
    cricket, co-dart, cricket, dart)-free.

    See https://www.graphclasses.org/classes/gc_1359

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_h_u_2k1_free(graph, is_triangle_free) and is_h_free(
        graph,
        [
            "dart",
            "co-dart",
            "co-cricket",
            "bull",
            "co(K_{3} U 2K_{1})",
            "cricket",
        ],
    )


@assign_class_id("gc_502")
@lru_cache(maxsize=None)
def is_gc_502(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, K_{2} U K_{3}, K_{2, 3}, P, P_{2} U P_{3},
    P_{5}, co(P), co(P_{2} U P_{3}), co-fork, fork, house)-free.

    See https://www.graphclasses.org/classes/gc_502

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return (
            is_p5_free(graph)
            and is_k2_u_k3_free(graph)
            and is_k23_free(graph)
            and is_house_p2_u_p3_free(graph)
            and is_h_free(
        graph,
        [
            "C_{5}",
            "co(P_{2} U P_{3})",
            "P",
            "co(P)",
            "fork",
            "co-fork",
        ],
    )
    )


@assign_class_id("gc_503")
@lru_cache(maxsize=None)
def is_xc_9_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is XC_{9}-free, False otherwise. This is equivalent to checking whether
    graph is (P_{5}, K_{2} U K_{3}, K_{2, 3}, house, P_{2} U P_{3}, P, co(P), co(P_{2} U P_{3}),
    co-fork, fork)-free.

    https://www.graphclasses.org/classes/gc_503.html

    @param graph:
    @return:
    """
    return (
            is_p5_free(graph)
            and is_k2_u_k3_free(graph)
            and is_k23_free(graph)
            and is_house_p2_u_p3_free(graph)
            and is_h_free(
        graph,
        [
            "P",
            "co(P)",
            "co(P_{2} U P_{3})",
            "co-fork",
            "fork",
        ],
    )
    )


# All recognizers for patterns on at most 6 vertices ----------------------------------------------
@assign_fisc(["K_{6}"])
@assign_class_id("gc_1344")
@lru_cache(maxsize=None)
def is_k6_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is K_{6}-free.

    See https://www.graphclasses.org/classes/gc_1344

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_k_clique_free(graph, 6)


@assign_fisc(["6K_{1}"])
@assign_class_id("AUTO_2584")
@lru_cache(maxsize=None)
def is_6k1_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is 6K_{1}-free.

    See https://www.graphclasses.org/classes/AUTO_2584

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    if must_contain_an_independent_set_of_size(graph, 6):
        return False

    return is_h_free(graph, ["6K_{1}"])


@assign_fisc(["K_{2} U claw"])
@assign_class_id("gc_735")
@lru_cache(maxsize=None)
def is_gc_735(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is K_{2} U claw-free.

    See https://www.graphclasses.org/classes/gc_735

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["K_{2} U claw"])
    # faster than:
    # return is_h_u_k2_free(graph, is_claw_free)


@assign_fisc(["C_{6}"])
@assign_class_id("gc_436")
@lru_cache(maxsize=None)
def is_c6_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is C_{6}-free.

    See https://www.graphclasses.org/classes/gc_436

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    # if graph has a C_6 then it has a P_4, so if graph is a cograph it has no P_4 and therefore no
    # C_6
    if is_cograph(graph):
        return True

    return is_h_free(graph, ["C_{6}"])


@assign_class_id("AUTO_224")
@lru_cache(maxsize=None)
def is_auto_224(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is co(2P_{3})-free.

    See https://www.graphclasses.org/classes/AUTO_224

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["co(2P_{3})"])


@assign_class_id("AUTO_407")
@lru_cache(maxsize=None)
def is_co_domino_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is co-domino-free.

    See https://www.graphclasses.org/classes/AUTO_407

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["co-domino"])


@assign_class_id("AUTO_2123")
@lru_cache(maxsize=None)
def is_auto_2123(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is co(K_{2} U claw)-free.

    See https://www.graphclasses.org/classes/AUTO_2123

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["co(K_{2} U claw)"])


@assign_class_id("AUTO_202")
@lru_cache(maxsize=None)
def is_auto_202(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is co(P_{2} U P_{4})-free.

    See https://www.graphclasses.org/classes/AUTO_202

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["co(P_{2} U P_{4})"])


@assign_class_id("gc_592")
@lru_cache(maxsize=None)
def is_domino_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is domino-free.

    See https://www.graphclasses.org/classes/gc_592

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["domino"])


@assign_class_id("AUTO_92")
@lru_cache(maxsize=None)
def is_auto_92(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is co(C_{6})-free.

    See https://www.graphclasses.org/classes/AUTO_92

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["co(C_{6})"])


@assign_class_id("gc_816")
@lru_cache(maxsize=None)
def is_e_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is E-free.

    See https://www.graphclasses.org/classes/gc_816

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["E"])


@assign_class_id("gc_638")
@lru_cache(maxsize=None)
def is_p6_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is P_{6}-free.

    See https://www.graphclasses.org/classes/gc_638

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    # if graph has no P_{4}, then it has no P_{6}
    if is_cograph(graph):
        return True

    return is_h_free(graph, ["P_{6}"])


@assign_class_id("gc_376")
@lru_cache(maxsize=None)
def is_s3_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is S_{3}-free.

    See https://www.graphclasses.org/classes/gc_376

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["S_{3}"])


@assign_class_id("AUTO_41")
@lru_cache(maxsize=None)
def is_co_p6_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is co(P_{6})-free.

    See https://www.graphclasses.org/classes/AUTO_41

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["co(P_{6})"])


@assign_class_id("gc_1357")
@lru_cache(maxsize=None)
def is_net_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is net-free.

    See https://www.graphclasses.org/classes/gc_1357

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["net"])


@assign_class_id("AUTO_497")
@lru_cache(maxsize=None)
def is_co_e_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is co(E)-free.

    See https://www.graphclasses.org/classes/AUTO_497

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["co(E)"])


@assign_class_id("AUTO_1635")
@lru_cache(maxsize=None)
def is_auto_1635(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (3K_{1}, co(C_{6}))-free.

    See https://www.graphclasses.org/classes/AUTO_1635

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_3k1_free(graph) and is_h_free(graph, ["co(C_{6})"])


@assign_class_id("gc_815")
@lru_cache(maxsize=None)
def is_gc_815(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{4}, P_{6})-free.

    See https://www.graphclasses.org/classes/gc_815

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_c4_free(graph) and is_p6_free(graph)


@assign_fisc(["P_{5}, co(P_{6})"])
@assign_class_id("gc_677")
@lru_cache(maxsize=None)
def is_p5_co_p6_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{5}, co(P_{6}))-free.

    See https://www.graphclasses.org/classes/gc_677

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_co_p6_free(graph)


@assign_class_id("gc_633")
@lru_cache(maxsize=None)
def is_gc_633(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (cross, triangle)-free.

    See https://www.graphclasses.org/classes/gc_633

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_triangle_free(graph) and is_h_free(graph, ["cross"])


@assign_class_id("AUTO_1441")
@lru_cache(maxsize=None)
def is_auto_1441(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (3K_{1}, co(3K_{2}))-free.

    See https://www.graphclasses.org/classes/AUTO_1441

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_3k1_free(graph) and is_h_free(graph, ["co(3K_{2})"])


@assign_class_id("AUTO_1511")
@lru_cache(maxsize=None)
def is_auto_1511(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{3}, house)-free.

    See https://www.graphclasses.org/classes/AUTO_1511

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["house", "2K_{3}"])


@assign_class_id("AUTO_1465")
@lru_cache(maxsize=None)
def is_auto_1465(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co(E), co(P))-free.

    See https://www.graphclasses.org/classes/AUTO_1465

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["co(P)", "co(E)"])


@assign_class_id("gc_1076")
@lru_cache(maxsize=None)
def is_gc_1076(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{4}, co(2P_{3}))-free.

    See https://www.graphclasses.org/classes/gc_1076

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_cograph(graph) and is_h_free(graph, ["co(2P_{3})"])


@assign_class_id("AUTO_1451")
@lru_cache(maxsize=None)
def is_auto_1451(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (3K_{1}, co(2P_{3}))-free.

    See https://www.graphclasses.org/classes/AUTO_1451

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_3k1_free(graph) and is_h_free(graph, ["co(2P_{3})"])


@assign_class_id("AUTO_1447")
@lru_cache(maxsize=None)
def is_auto_1447(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (3K_{1}, co(P_{6}))-free.

    See https://www.graphclasses.org/classes/AUTO_1447

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_3k1_free(graph) and is_co_p6_free(graph)


@assign_class_id("gc_678")
@lru_cache(maxsize=None)
def is_gc_678(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{5}, co(C_{6}))-free.

    See https://www.graphclasses.org/classes/gc_678

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_h_free(graph, ["co(C_{6})"])


@assign_class_id("gc_929")
@lru_cache(maxsize=None)
def is_gc_929(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (3K_{2}, triangle)-free.

    See https://www.graphclasses.org/classes/gc_929

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_triangle_free(graph) and is_h_free(graph, ["3K_{2}"])


@assign_class_id("AUTO_1477")
@lru_cache(maxsize=None)
def is_auto_1477(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (3K_{1}, co(E))-free.

    See https://www.graphclasses.org/classes/AUTO_1477

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_3k1_free(graph) and is_h_free(graph, ["co(E)"])


@assign_class_id("AUTO_1445")
@lru_cache(maxsize=None)
def is_auto_1445(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (3K_{1}, co(X_{172}))-free.

    See https://www.graphclasses.org/classes/AUTO_1445

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_3k1_free(graph) and is_h_free(graph, ["co(X_{172})"])


@assign_class_id("gc_431")
@lru_cache(maxsize=None)
def is_gc_431(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{3, 3}, P_{5})-free.

    See https://www.graphclasses.org/classes/gc_431

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_h_free(graph, ["K_{3,3}"])


@assign_class_id("AUTO_1470")
@lru_cache(maxsize=None)
def is_auto_1470(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{6}, house)-free.

    See https://www.graphclasses.org/classes/AUTO_1470

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["house", "C_{6}"])


@assign_class_id("AUTO_1767")
@lru_cache(maxsize=None)
def is_auto_1767(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co(P_{6}), co-claw)-free.

    See https://www.graphclasses.org/classes/AUTO_1767

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_co_claw_free(graph) and is_co_p6_free(graph)


@assign_class_id("AUTO_1443")
@lru_cache(maxsize=None)
def is_auto_1443(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{4}, S_{3})-free.

    See https://www.graphclasses.org/classes/AUTO_1443

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_c4_free(graph) and is_h_free(graph, ["S_{3}"])


@assign_class_id("gc_922")
@lru_cache(maxsize=None)
def is_gc_922(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{6}, triangle)-free.

    See https://www.graphclasses.org/classes/gc_922

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_triangle_free(graph) and is_p6_free(graph)


@assign_class_id("gc_635")
@lru_cache(maxsize=None)
def is_gc_635(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (H, triangle)-free.

    See https://www.graphclasses.org/classes/gc_635

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_triangle_free(graph) and is_h_free(graph, ["H"])


@assign_class_id("gc_648")
@lru_cache(maxsize=None)
def is_gc_648(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{3, 3}-e, P_{5})-free.

    See https://www.graphclasses.org/classes/gc_648

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_h_free(graph, ["K_{3,3}-e"])


@assign_class_id("gc_925")
@lru_cache(maxsize=None)
def is_gc_925(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{2} U claw, triangle)-free.

    See https://www.graphclasses.org/classes/gc_925

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_triangle_free(graph) and is_gc_735(graph)


@assign_class_id("gc_433")
@lru_cache(maxsize=None)
def is_gc_433(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{6}, co(C_{6}))-free.

    See https://www.graphclasses.org/classes/gc_433

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["C_{6}", "co(C_{6})"])


@assign_class_id("gc_373")
@lru_cache(maxsize=None)
def is_gc_373(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (S_{3}, net)-free.

    See https://www.graphclasses.org/classes/gc_373

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["net", "S_{3}"])


@assign_class_id("AUTO_1442")
@lru_cache(maxsize=None)
def is_auto_1442(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{4}, S_{3})-free.

    See https://www.graphclasses.org/classes/AUTO_1442

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_k4_free(graph) and is_h_free(graph, ["S_{3}"])


@assign_class_id("AUTO_1476")
@lru_cache(maxsize=None)
def is_auto_1476(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{3} + e, house)-free.

    See https://www.graphclasses.org/classes/AUTO_1476

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["house", "2K_{3} + e"])


@assign_class_id("gc_1234")
@lru_cache(maxsize=None)
def is_gc_1234(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{6}, claw)-free.

    See https://www.graphclasses.org/classes/gc_1234

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_claw_free(graph) and is_p6_free(graph)


@assign_class_id("gc_1024")
@lru_cache(maxsize=None)
def is_gc_1024(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{6}, triangle)-free.

    See https://www.graphclasses.org/classes/gc_1024

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_triangle_free(graph) and is_h_free(graph, ["C_{6}"])


@assign_class_id("gc_137")
@lru_cache(maxsize=None)
def is_gc_137(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (claw, net)-free.

    See https://www.graphclasses.org/classes/gc_137

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["claw", "net"])


@assign_class_id("gc_927")
@lru_cache(maxsize=None)
def is_gc_927(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, net)-free.

    See https://www.graphclasses.org/classes/gc_927

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_2k2_free(graph) and is_h_free(graph, ["net"])


@assign_class_id("AUTO_1480")
@lru_cache(maxsize=None)
def is_auto_1480(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (3K_{1}, co-cross)-free.

    See https://www.graphclasses.org/classes/AUTO_1480

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_3k1_free(graph) and is_h_free(graph, ["co-cross"])


@assign_class_id("gc_636")
@lru_cache(maxsize=None)
def is_gc_636(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (E, triangle)-free.

    See https://www.graphclasses.org/classes/gc_636

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_triangle_free(graph) and is_e_free(graph)


@assign_class_id("AUTO_1460")
@lru_cache(maxsize=None)
def is_auto_1460(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, co(P_{6}))-free.

    See https://www.graphclasses.org/classes/AUTO_1460

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_2k2_free(graph) and is_co_p6_free(graph)


@assign_class_id("gc_914")
@lru_cache(maxsize=None)
def is_gc_914(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2P_{3}, triangle)-free.

    See https://www.graphclasses.org/classes/gc_914

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    # check instead that the graph is both (triangle, P_{3})-free and 2P_{3}-free, since the former
    # can be achieved in time O(m+n); in the worst-case, we'll have to check 2P_{3}-freeness too,
    # but the running time will be the same as checking for (triangle, 2P_{3})-directly
    return is_p3_triangle_free(graph) and is_2p3_free(graph)


@assign_class_id("AUTO_2154")
@lru_cache(maxsize=None)
def is_auto_2154(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (3K_{1}, co(K_{2} U claw))-free.

    See https://www.graphclasses.org/classes/AUTO_2154

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_3k1_free(graph) and is_h_free(graph, ["co(K_{2} U claw)"])


@assign_class_id("AUTO_1700")
@lru_cache(maxsize=None)
def is_auto_1700(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2P_{3}, P_{4})-free.

    See https://www.graphclasses.org/classes/AUTO_1700

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_cograph(graph) and is_2p3_free(graph)


@assign_class_id("gc_924")
@lru_cache(maxsize=None)
def is_gc_924(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (X_{172}, triangle)-free.

    See https://www.graphclasses.org/classes/gc_924

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_triangle_free(graph) and is_h_free(graph, ["X_{172}"])


@assign_class_id("AUTO_1446")
@lru_cache(maxsize=None)
def is_auto_1446(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (3K_{1}, co(P_{2} U P_{4}))-free.

    See https://www.graphclasses.org/classes/AUTO_1446

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_3k1_free(graph) and is_h_free(graph, ["co(P_{2} U P_{4})"])


@assign_class_id("AUTO_1478")
@lru_cache(maxsize=None)
def is_auto_1478(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (3K_{1}, co(H))-free.

    See https://www.graphclasses.org/classes/AUTO_1478

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_3k1_free(graph) and is_h_free(graph, ["co(H)"])


@assign_class_id("AUTO_1537")
@lru_cache(maxsize=None)
def is_auto_1537(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (S_{3}, co-claw)-free.

    See https://www.graphclasses.org/classes/AUTO_1537

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_co_claw_free(graph) and is_s3_free(graph)


@assign_class_id("AUTO_2153")
@lru_cache(maxsize=None)
def is_auto_2153(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (3K_{1}, co(K_{1, 5}))-free.

    See https://www.graphclasses.org/classes/AUTO_2153

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_3k1_free(graph) and is_h_free(graph, ["co(K_{1,5})"])


@assign_class_id("gc_756")
@lru_cache(maxsize=None)
def is_gc_756(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (E, P)-free.

    See https://www.graphclasses.org/classes/gc_756

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["P", "E"])


@assign_class_id("gc_928")
@lru_cache(maxsize=None)
def is_gc_928(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (4K_{1}, net)-free.

    See https://www.graphclasses.org/classes/gc_928

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_4k1_free(graph) and is_net_free(graph)


@assign_class_id("gc_585")
@lru_cache(maxsize=None)
def is_gc_585(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (domino, gem, house)-free.

    See https://www.graphclasses.org/classes/gc_585

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_gem_free(graph) and is_house_free(graph) and is_domino_free(graph)


@assign_class_id("AUTO_2102")
@lru_cache(maxsize=None)
def is_auto_2102(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co(W_{4}), co(W_{5}), co-butterfly)-free.

    See https://www.graphclasses.org/classes/AUTO_2102

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    #      co(W_{4})
    return (
            is_h_u_k1_free(graph, is_2k2_free)
            and is_h_free(graph, ["co-butterfly"])
            and is_h_free(graph, ["co(W_{5})"])
    )


@assign_class_id("AUTO_1488")
@lru_cache(maxsize=None)
def is_auto_1488(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{5}, co-domino, co-gem)-free.

    See https://www.graphclasses.org/classes/AUTO_1488

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return (
            is_p5_free(graph) and is_co_gem_free(graph) and is_h_free(graph, ["co-domino"])
    )


@assign_class_id("AUTO_1490")
@lru_cache(maxsize=None)
def is_auto_1490(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co(A), co(P_{6}), co-domino)-free.

    See https://www.graphclasses.org/classes/AUTO_1490

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["co(A)", "co(P_{6})", "co-domino"])


@assign_class_id("gc_1074")
@lru_cache(maxsize=None)
def is_gc_1074(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, P_{4}, co(2P_{3}))-free.

    See https://www.graphclasses.org/classes/gc_1074

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_cograph(graph) and is_2k2_free(graph) and is_h_free(graph, ["co(2P_{3})"])


@assign_class_id("gc_1279")
@lru_cache(maxsize=None)
def is_gc_1279(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2P_{3}, C_{4}, C_{6})-free.

    See https://www.graphclasses.org/classes/gc_1279

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_c4_free(graph) and is_h_free(graph, ["C_{6}", "2P_{3}"])


@assign_class_id("gc_355")
@lru_cache(maxsize=None)
def is_gc_355(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (S_{3}, claw, net)-free.

    See https://www.graphclasses.org/classes/gc_355

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["claw", "net", "S_{3}"])


@assign_class_id("gc_1075")
@lru_cache(maxsize=None)
def is_gc_1075(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2P_{3}, C_{4}, P_{4})-free.

    See https://www.graphclasses.org/classes/gc_1075

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_cograph(graph) and is_c4_free(graph) and is_h_free(graph, ["2P_{3}"])


@assign_class_id("gc_428")
@lru_cache(maxsize=None)
def is_gc_428(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{3, 3}-e, P_{5}, X_{98})-free.

    See https://www.graphclasses.org/classes/gc_428

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_h_free(graph, ["X_{98}", "K_{3,3}-e"])


@assign_class_id("AUTO_1821")
@lru_cache(maxsize=None)
def is_auto_1821(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, co(2P_{3}), co(C_{6}))-free.

    See https://www.graphclasses.org/classes/AUTO_1821

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_2k2_free(graph) and is_h_free(graph, ["co(C_{6})", "co(2P_{3})"])


@assign_class_id("AUTO_1530")
@lru_cache(maxsize=None)
def is_auto_1530(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (S_{3}, co-claw, net)-free.

    See https://www.graphclasses.org/classes/AUTO_1530

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_co_claw_free(graph) and is_h_free(graph, ["net", "S_{3}"])


@assign_class_id("gc_273")
@lru_cache(maxsize=None)
def is_gc_273(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, P_{6}, co(P_{6}))-free.

    See https://www.graphclasses.org/classes/gc_273

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_p6_free(graph) and is_h_free(graph, ["C_{5}", "co(P_{6})"])


@assign_class_id("AUTO_1491")
@lru_cache(maxsize=None)
def is_auto_1491(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{4}, co(A), co(H))-free.

    See https://www.graphclasses.org/classes/AUTO_1491

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_c4_free(graph) and is_h_free(graph, ["co(A)", "co(H)"])


@assign_class_id("gc_563")
@lru_cache(maxsize=None)
def is_gc_563(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (A, P_{6}, domino)-free.

    See https://www.graphclasses.org/classes/gc_563

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_p6_free(graph) and is_h_free(graph, ["A", "domino"])


@assign_class_id("AUTO_1514")
@lru_cache(maxsize=None)
def is_auto_1514(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{3} + e, co(X_{98}), house)-free.

    See https://www.graphclasses.org/classes/AUTO_1514

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["house", "2K_{3} + e", "co(X_{98})"])


@assign_class_id("gc_542")
@lru_cache(maxsize=None)
def is_gc_542(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, A, H)-free.

    See https://www.graphclasses.org/classes/gc_542

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_2k2_free(graph) and is_h_free(graph, ["H", "A"])


@assign_class_id("AUTO_1466")
@lru_cache(maxsize=None)
def is_auto_1466(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (3K_{2}, E, P_{2} U P_{4}, net)-free.

    See https://www.graphclasses.org/classes/AUTO_1466

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_p2up4_free(graph) and is_h_free(graph, ["net", "E", "3K_{2}"])


@assign_class_id("gc_411")
@lru_cache(maxsize=None)
def is_gc_411(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P, P_{5}, co(3K_{2}), gem)-free.

    See https://www.graphclasses.org/classes/gc_411

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_h_free(graph, ["P", "gem", "co(3K_{2})"])


@assign_class_id("AUTO_1710")
@lru_cache(maxsize=None)
def is_auto_1710(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (3K_{1}, C_{5}, co(C_{6}), co(P_{6}))-free.

    See https://www.graphclasses.org/classes/AUTO_1710

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_3k1_free(graph) and is_h_free(graph, ["C_{5}", "co(C_{6})", "co(P_{6})"])


@assign_class_id("AUTO_1636")
@lru_cache(maxsize=None)
def is_auto_1636(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, C_{5}, co(C_{6}), net)-free.

    See https://www.graphclasses.org/classes/AUTO_1636

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_2k2_free(graph) and is_h_free(graph, ["C_{5}", "net", "co(C_{6})"])


@assign_class_id("gc_1026")
@lru_cache(maxsize=None)
def is_gc_1026(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{4}, C_{5}, C_{6}, S_{3})-free.

    See https://www.graphclasses.org/classes/gc_1026

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_c4_free(graph) and is_h_free(graph, ["C_{5}", "C_{6}", "S_{3}"])


@assign_class_id("AUTO_1563")
@lru_cache(maxsize=None)
def is_auto_1563(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (3K_{2}, C_{5}, P_{2} U P_{4}, net)-free.

    See https://www.graphclasses.org/classes/AUTO_1563

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_p2up4_free(graph) and is_h_free(
        graph, ["P_{2} U P_{4}", "C_{5}", "net", "3K_{2}"]
    )


@assign_class_id("gc_1176")
@lru_cache(maxsize=None)
def is_gc_1176(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, C_{6}, P_{6}, triangle)-free.

    See https://www.graphclasses.org/classes/gc_1176

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return (
            is_triangle_free(graph)
            and is_p6_free(graph)
            and is_h_free(graph, ["C_{5}", "C_{6}"])
    )


@assign_class_id("AUTO_1519")
@lru_cache(maxsize=None)
def is_auto_1519(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (3K_{2}, co(P), co-gem, house)-free.

    See https://www.graphclasses.org/classes/AUTO_1519

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_co_gem_free(graph) and is_h_free(graph, ["house", "co(P)", "3K_{2}"])


@assign_class_id("gc_748")
@lru_cache(maxsize=None)
def is_gc_748(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (S_{3}, co(3K_{2}), co(E), co(P_{2} U P_{4}))-free.

    See https://www.graphclasses.org/classes/gc_748

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["S_{3}", "co(P_{2} U P_{4})", "co(E)", "co(3K_{2})"])


@assign_class_id("gc_960")
@lru_cache(maxsize=None)
def is_gc_960(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, S_{3}, co(3K_{2}), co(P_{2} U P_{4}))-free.

    See https://www.graphclasses.org/classes/gc_960

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["C_{5}", "S_{3}", "co(P_{2} U P_{4})", "co(3K_{2})"])


@assign_class_id("AUTO_756")
@lru_cache(maxsize=None)
def is_auto_756(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (A, H, K_{3, 3}, X_{45}, triangle)-free.

    See https://www.graphclasses.org/classes/AUTO_756

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_triangle_free(graph) and is_h_free(graph, ["X_{45}", "K_{3,3}", "H", "A"])


@assign_class_id("gc_260")
@lru_cache(maxsize=None)
def is_gc_260(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, P_{5}, co-fish, fish, house)-free.

    See https://www.graphclasses.org/classes/gc_260

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_h_free(graph, ["C_{5}", "house", "co-fish", "fish"])


@assign_class_id("AUTO_2766")
@lru_cache(maxsize=None)
def is_auto_2766(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{3}, 3K_{1}, co(A), co(H), co(X_{45}))-free.

    See https://www.graphclasses.org/classes/AUTO_2766

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_3k1_free(graph) and is_h_free(
        graph, ["co(H)", "co(A)", "2K_{3}", "co(X_{45})"]
    )


@assign_class_id("AUTO_734")
@lru_cache(maxsize=None)
def is_auto_734(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, C_{6}, P_{6}, co(C_{6}), co(P_{6}))-free.

    See https://www.graphclasses.org/classes/AUTO_734

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_p6_free(graph) and is_h_free(
        graph, ["C_{5}", "C_{6}", "co(P_{6})", "co(C_{6})"]
    )


@assign_class_id("gc_627")
@lru_cache(maxsize=None)
def is_gc_627(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, K_{3, 3}, K_{3, 3}+e, P_{4}, co(2P_{3}))-free.

    See https://www.graphclasses.org/classes/gc_627

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return (
            is_cograph(graph)
            and is_2k2_free(graph)
            and is_h_free(graph, ["co(2P_{3})", "K_{3,3}", "K_{3,3}+e"])
    )


@assign_class_id("gc_38")
@lru_cache(maxsize=None)
def is_gc_38(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, C_{4}, C_{5}, S_{3}, net)-free.

    See https://www.graphclasses.org/classes/gc_38

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_split(graph) and is_h_free(graph, ["S_{3}", "net"])


@assign_class_id("AUTO_1483")
@lru_cache(maxsize=None)
def is_auto_1483(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{3}, 2P_{3}, C_{4}, K_{3} U P_{3}, P_{4})-free.

    See https://www.graphclasses.org/classes/AUTO_1483

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return (
            is_cograph(graph)
            and is_c4_free(graph)
            and is_h_free(graph, ["K_{3} U P_{3}", "2P_{3}", "2K_{3}"])
    )


@assign_class_id("gc_845")
@lru_cache(maxsize=None)
def is_gc_845(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (A, C_{5}, C_{6}, P_{6}, domino, house)-free.

    See https://www.graphclasses.org/classes/gc_845

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_p6_free(graph) and is_h_free(
        graph, ["C_{5}", "house", "C_{6}", "A", "domino"]
    )


@assign_class_id("gc_809")
@lru_cache(maxsize=None)
def is_gc_809(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{2, 3}, P, P_{5}, X_{163}, X_{95}, diamond)-free.

    See https://www.graphclasses.org/classes/gc_809

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return (
            is_p5_free(graph)
            and is_k23_free(graph)
            and is_h_free(graph, ["diamond", "P", "X_{163}", "X_{95}"])
    )


@assign_class_id("AUTO_3700")
@lru_cache(maxsize=None)
def is_auto_3700(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, C_{4}, C_{5}, S_{3}, co-claw, net)-free.

    See https://www.graphclasses.org/classes/AUTO_3700

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return (
            is_split(graph)
            and is_co_claw_free(graph)
            and is_h_free(graph, ["S_{3}", "net"])
    )


@assign_class_id("AUTO_2140")
@lru_cache(maxsize=None)
def is_auto_2140(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{2} U K_{3}, co(P), co(X_{163}), co(X_{95}), co-diamond,
    house)-free.

    See https://www.graphclasses.org/classes/AUTO_2140

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return (
            is_co_diamond_free(graph)
            and is_k2_u_k3_free(graph)
            and is_h_free(
        graph,
        ["house", "co(P)", "co(X_{163})", "co(X_{95})"],
    )
    )


@assign_class_id("AUTO_1456")
@lru_cache(maxsize=None)
def is_auto_1456(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, P_{5}, co(A), co(C_{6}), co(P_{6}), co-domino)-free.

    See https://www.graphclasses.org/classes/AUTO_1456

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_h_free(
        graph, ["C_{5}", "co(P_{6})", "co(A)", "co(C_{6})", "co-domino"]
    )


@assign_class_id("AUTO_1765")
@lru_cache(maxsize=None)
def is_auto_1765(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, C_{4}, C_{5}, S_{3}, claw, net)-free.

    See https://www.graphclasses.org/classes/AUTO_1765

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_split(graph) and is_h_free(graph, ["claw", "S_{3}", "net"])


@assign_class_id("gc_188")
@lru_cache(maxsize=None)
def is_gc_188(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P, P_{5}, S_{3}, co(P), co-fork, fork, house, net)-free.

    See https://www.graphclasses.org/classes/gc_188

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_h_free(
        graph, ["house", "P", "co(P)", "fork", "co-fork", "S_{3}", "net"]
    )


@assign_class_id("gc_17")
@lru_cache(maxsize=None)
def is_gc_17(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, P, P_{5}, S_{3}, co(P), co-fork, fork, house, net)-free.

    See https://www.graphclasses.org/classes/gc_17

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_h_free(
        graph,
        ["C_{5}", "house", "P", "co(P)", "fork", "co-fork", "S_{3}", "net"],
    )


@assign_class_id("gc_1037")
@lru_cache(maxsize=None)
def is_gc_1037(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{4} U P_{2}, C_{5}, C_{6}, K_{2} U K_{3}, K_{2,
    3}, P_{6}, W_{4}, X_{18}, X_{5}, X_{84}, co(C_{4} U P_{2}), co(C_{6}),
    co(P_{6}), co(W_{4}), co(X_{18}), co(X_{5}), co(X_{84}), antenna, co-
    antenna, co-domino, co-fish, domino, fish)-free.

    See https://www.graphclasses.org/classes/gc_1037

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return (
            is_p6_free(graph)
            and is_k2_u_k3_free(graph)
            and is_k23_free(graph)
            and is_h_free(
        graph,
        [
            "C_{4} U P_{2}",
            "W_{4}",
            "co(W_{4})",
            "C_{5}",
            "co-fish",
            "co(P_{6})",
            "fish",
            "co-domino",
            "C_{6}",
            "X_{84}",
            "co(X_{5})",
            "co-antenna",
            "X_{18}",
            "co(C_{6})",
            "domino",
            "X_{5}",
            "antenna",
            "co(X_{18})",
            "co(X_{84})",
            "co(C_{4} U P_{2})",
        ],
    )
    )


@assign_class_id("gc_842")
@lru_cache(maxsize=None)
def is_gc_842(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{3} + e, A, C_{5}, C_{6}, E, H, K_{3, 3}-e, R,
    X_{168}, X_{171}, X_{18}, X_{45}, X_{5}, X_{58}, X_{84}, X_{95}, co(A),
    co(C_{6}), co(E), co(H), co(R), co(X_{168}), co(X_{171}), co(X_{18}),
    co(X_{45}), co(X_{5}), co(X_{58}), co(X_{84}), co(X_{95}), antenna, co-
    antenna, co-domino, co-fish, co-twin-house, domino, fish, twin-house)-free.

    See https://www.graphclasses.org/classes/gc_842

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_h_free(
        graph,
        [
            "C_{5}",
            "co-fish",
            "fish",
            "co(R)",
            "co(X_{171})",
            "2K_{3} + e",
            "co(A)",
            "co-domino",
            "co(X_{95})",
            "C_{6}",
            "X_{84}",
            "co(X_{5})",
            "X_{168}",
            "co(X_{45})",
            "co-antenna",
            "co(H)",
            "X_{45}",
            "X_{58}",
            "co(E)",
            "X_{18}",
            "co(C_{6})",
            "X_{95}",
            "X_{171}",
            "domino",
            "X_{5}",
            "R",
            "antenna",
            "E",
            "A",
            "H",
            "co(X_{58})",
            "co(X_{18})",
            "K_{3,3}-e",
            "co-twin-house",
            "twin-house",
            "co(X_{84})",
            "co(X_{168})",
        ],
    )


@assign_class_id("gc_840")
@lru_cache(maxsize=None)
def is_gc_840(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{3} + e, A, C_{5}, C_{6}, E, K_{3, 3}-e,
    P_{6}, R, X_{166}, X_{167}, X_{169}, X_{170}, X_{171}, X_{172}, X_{18},
    X_{45}, X_{5}, X_{58}, X_{84}, X_{95}, X_{98}, co(A), co(C_{6}), co(E),
    co(P_{6}), co(R), co(X_{166}), co(X_{167}), co(X_{169}), co(X_{170}),
    co(X_{171}), co(X_{172}), co(X_{18}), co(X_{45}), co(X_{5}), co(X_{58}),
    co(X_{84}), co(X_{95}), co(X_{98}), antenna, co-antenna, co-domino, co-fish,
    co-twin-house, domino, fish, twin-house)-free.

    See https://www.graphclasses.org/classes/gc_840

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_h_free(
        graph,
        [
            "C_{5}",
            "X_{169}",
            "co(P_{6})",
            "X_{166}",
            "co-fish",
            "fish",
            "co(R)",
            "co(X_{171})",
            "2K_{3} + e",
            "X_{170}",
            "co(A)",
            "co-domino",
            "X_{167}",
            "co(X_{95})",
            "C_{6}",
            "P_{6}",
            "X_{84}",
            "co(X_{5})",
            "X_{172}",
            "co(X_{98})",
            "co(X_{45})",
            "co-antenna",
            "X_{45}",
            "X_{58}",
            "co(E)",
            "co(X_{170})",
            "X_{18}",
            "co(X_{172})",
            "co(C_{6})",
            "X_{95}",
            "X_{171}",
            "X_{98}",
            "domino",
            "X_{5}",
            "R",
            "antenna",
            "E",
            "A",
            "co(X_{169})",
            "co(X_{58})",
            "co(X_{18})",
            "K_{3,3}-e",
            "co(X_{167})",
            "co-twin-house",
            "co(X_{166})",
            "twin-house",
            "co(X_{84})",
        ],
    )


@assign_class_id("gc_1108")
@lru_cache(maxsize=None)
def is_gc_1108(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{3} + e, 5-pan, A, C_{6}, E, K_{3, 3}-e,
    P_{6}, R, X_{166}, X_{167}, X_{169}, X_{170}, X_{171}, X_{172}, X_{18},
    X_{37}, X_{45}, X_{5}, X_{58}, X_{84}, X_{95}, X_{98}, co(5-pan), co(A),
    co(C_{6}), co(E), co(P_{6}), co(R), co(X_{166}), co(X_{167}), co(X_{169}),
    co(X_{170}), co(X_{171}), co(X_{172}), co(X_{18}), co(X_{37}), co(X_{45}),
    co(X_{5}), co(X_{58}), co(X_{84}), co(X_{95}), co(X_{98}), antenna, co-
    antenna, co-domino, co-fish, co-twin-C_{5}, co-twin-house, domino, fish,
    twin-C_{5}, twin-house)-free.

    See https://www.graphclasses.org/classes/gc_1108

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_h_free(
        graph,
        [
            "X_{169}",
            "co(P_{6})",
            "X_{166}",
            "co-fish",
            "fish",
            "co(R)",
            "X_{37}",
            "co(X_{171})",
            "2K_{3} + e",
            "X_{170}",
            "co(A)",
            "co-domino",
            "twin-C_{5}",
            "X_{167}",
            "co(X_{95})",
            "C_{6}",
            "P_{6}",
            "co(X_{37})",
            "co-twin-C_{5}",
            "co(5-pan)",
            "X_{84}",
            "co(X_{5})",
            "X_{172}",
            "co(X_{98})",
            "co(X_{45})",
            "co-antenna",
            "X_{45}",
            "X_{58}",
            "co(E)",
            "co(X_{170})",
            "X_{18}",
            "co(X_{172})",
            "co(C_{6})",
            "X_{95}",
            "X_{171}",
            "X_{98}",
            "domino",
            "X_{5}",
            "R",
            "antenna",
            "E",
            "A",
            "co(X_{169})",
            "co(X_{58})",
            "co(X_{18})",
            "K_{3,3}-e",
            "co(X_{167})",
            "co-twin-house",
            "co(X_{166})",
            "twin-house",
            "co(X_{84})",
            "5-pan",
        ],
    )


@assign_class_id("gc_839")
@lru_cache(maxsize=None)
def is_gc_839(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{3} + e, A, C_{5}, C_{6}, E, H, K_{3, 3}-e,
    P_{6}, R, S_{3}, X_{166}, X_{167}, X_{168}, X_{169}, X_{170}, X_{171},
    X_{172}, X_{18}, X_{45}, X_{5}, X_{58}, X_{84}, X_{95}, X_{96}, X_{98},
    co(A), co(C_{6}), co(E), co(H), co(P_{6}), co(R), co(X_{166}), co(X_{167}),
    co(X_{168}), co(X_{169}), co(X_{170}), co(X_{171}), co(X_{172}), co(X_{18}),
    co(X_{45}), co(X_{5}), co(X_{58}), co(X_{84}), co(X_{95}), co(X_{96}),
    co(X_{98}), antenna, co-antenna, co-cross, co-domino, co-fish, co-twin-
    house, cross, domino, fish, net, twin-house)-free.

    See https://www.graphclasses.org/classes/gc_839

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_h_free(
        graph,
        [
            "C_{5}",
            "X_{169}",
            "co(P_{6})",
            "X_{166}",
            "co-fish",
            "fish",
            "co(R)",
            "co(X_{171})",
            "2K_{3} + e",
            "X_{170}",
            "co(A)",
            "co-domino",
            "X_{167}",
            "co(X_{95})",
            "C_{6}",
            "P_{6}",
            "S_{3}",
            "X_{84}",
            "co(X_{96})",
            "co(X_{5})",
            "co-cross",
            "X_{168}",
            "X_{172}",
            "net",
            "co(X_{98})",
            "co(X_{45})",
            "co-antenna",
            "co(H)",
            "X_{45}",
            "X_{58}",
            "co(E)",
            "co(X_{170})",
            "X_{18}",
            "co(X_{172})",
            "co(C_{6})",
            "X_{95}",
            "X_{171}",
            "X_{98}",
            "domino",
            "X_{5}",
            "R",
            "antenna",
            "X_{96}",
            "E",
            "A",
            "H",
            "co(X_{169})",
            "co(X_{18})",
            "K_{3,3}-e",
            "co(X_{167})",
            "co(X_{58})",
            "co(X_{166})",
            "cross",
            "co-twin-house",
            "co(X_{84})",
            "twin-house",
            "co(X_{168})",
        ],
    )


@assign_class_id("gc_838")
@lru_cache(maxsize=None)
def is_p4_tidy(graph: nx.Graph) -> bool:
    """
    A partner of a P4 A in G is a vertex v in G-A such that A+v induces at least two P4s.
    A graph G is P4-tidy if any P4 has at most one partner.

    Self-complementary class.

    https://www.graphclasses.org/classes/gc_8.html

    @param graph:
    @return:
    """
    """
    V. Giakoumakis, F. Roussel, H. Thuillier
    On P4--tidy graphs
    Discrete Math. and Theor. Comp. Sci. 1 1997 17--41
    ZMath 0930.05073
    """
    # I'm using the fact that this class is equivalent to the class
    # https://www.graphclasses.org/classes/gc_838.html , as well as the
    # characterization provided by my xc_unpacker program, which tells me that
    # the union of the graphs covered by XZ_6 to XZ_14 (XZ_10 excluded) is:
    #
    # ['2K_{3} + e', '5-pan', 'A', 'C_{6}', 'E', 'H', 'P_{6}', 'X_{166}',
    #  'X_{169}', 'X_{170}', 'X_{171}', 'X_{172}', 'X_{18}', 'X_{37}',
    #  'X_{45}', 'X_{58}', 'X_{5}', 'X_{84}', 'X_{95}', 'X_{96}', 'antenna',
    #  'co(5-pan)', 'co(R)', 'co(X_{167})', 'co(X_{168})', 'co(X_{37})',
    #  'co(X_{5})', 'co(X_{98})', 'co-domino', 'co-fish', 'co-twin-C_{5}',
    #  'co-twin-house', 'cross', 'twin-C_{5}']
    #
    # so a graph is P_4-tidy iff it contains none of the above subgraphs, and
    # none of their complements either
    return is_h_free(
        graph,
        {  # the result of unpacking XZ_6 to XZ_14 excluding XZ_10
            "2K_{3} + e",
            "5-pan",
            "A",
            "C_{6}",
            "E",
            "H",
            "P_{6}",
            "X_{166}",
            "X_{169}",
            "X_{170}",
            "X_{171}",
            "X_{172}",
            "X_{18}",
            "X_{37}",
            "X_{45}",
            "X_{58}",
            "X_{5}",
            "X_{84}",
            "X_{95}",
            "X_{96}",
            "antenna",
            "co(5-pan)",
            "co(R)",
            "co(X_{167})",
            "co(X_{168})",
            "co(X_{37})",
            "co(X_{5})",
            "co(X_{98})",
            "co-domino",
            "co-fish",
            "co-twin-C_{5}",
            "co-twin-house",
            "cross",
            "twin-C_{5}",
        }.union(
            {  # the complements of the above subgraphs
                "K_{3,3}-e",
                "co(5-pan)",
                "co(A)",
                "co(C_{6})",
                "co(E)",
                "co(H)",
                "co(P_{6})",
                "co(X_{166})",
                "co(X_{169})",
                "co(X_{170})",
                "co(X_{171})",
                "co(X_{172})",
                "co(X_{18})",
                "co(X_{37})",
                "co(X_{45})",
                "co(X_{58})",
                "co(X_{5})",
                "co(X_{84})",
                "co(X_{95})",
                "co(X_{96})",
                "co-antenna",
                "5-pan",
                "R",
                "X_{167}",
                "X_{168}",
                "X_{37}",
                "X_{5}",
                "X_{98}",
                "domino",
                "fish",
                "twin-C_{5}",
                "twin-house",
                "co-cross",
                "co-twin-C_{5}",
            }
        ),
    )


@assign_class_id("gc_13")
@lru_cache(maxsize=None)
def is_c5_free_and_p4_tidy(graph: nx.Graph) -> bool:
    """
    Returns True if graph is C_{5}-free and P_{4}-tidy, False otherwise.

    Self-complementary class.

    https://www.graphclasses.org/classes/gc_13.html

    @param graph:
    @return:
    """
    return is_c5_free(graph) and is_p4_tidy(graph)


@assign_class_id("gc_961")
@lru_cache(maxsize=None)
def is_p4_tidy_and_balanced(graph: nx.Graph) -> bool:
    """
    https://www.graphclasses.org/classes/gc_958.html
    @param graph:
    @return:
    """
    # using equivalence with https://www.graphclasses.org/classes/gc_961.html
    return is_gc_960(graph) and is_p4_tidy(graph)


@assign_class_id("AUTO_3683")
@lru_cache(maxsize=None)
def is_auto_3683(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_3683.html

    @param graph:
    @return:
    """
    return is_auto_1563(graph) and is_p4_tidy(graph)


@assign_class_id("gc_1372")
@lru_cache(maxsize=None)
def is_gc_1372(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2P_3, C_4, C_5, P_5, X_170, co(A))-free.

    See https://www.graphclasses.org/classes/gc_1372

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["2P_{3}", "C_{4}", "C_{5}", "P_{5}", "X_{170}", "co(A)"])


@assign_class_id("AUTO_1930")
@lru_cache(maxsize=None)
def is_auto_1930(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co(2P_3), 2K_2, C_5, house, co(X_170), A)-free.

    See https://www.graphclasses.org/classes/AUTO_1930

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """

    return is_2k2_free(graph) and is_h_free(
        graph, ["co(2P_{3})", "house", "C_{5}", "co(X_{170})", "A"]
    )


# All recognizers for patterns on at most 7 vertices ----------------------------------------------
@assign_class_id("AUTO_2097")
@lru_cache(maxsize=None)
def is_auto_2097(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is co(BW_{3})-free.

    See https://www.graphclasses.org/classes/AUTO_2097

    Complexity of naïve matching: O(n^7)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["co(BW_{3})"])


@assign_class_id("AUTO_329")
@lru_cache(maxsize=None)
def is_co_p7_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is co(P_{7})-free.

    See https://www.graphclasses.org/classes/AUTO_329

    Complexity of naïve matching: O(n^7)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["co(P_{7})"])


@assign_class_id("AUTO_2583")
@lru_cache(maxsize=None)
def is_auto_2583(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is 7K_{1}-free.

    See https://www.graphclasses.org/classes/AUTO_2583

    Complexity of naïve matching: O(n^7)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["7K_{1}"])


@assign_class_id("gc_590")
@lru_cache(maxsize=None)
def is_gc_590(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is BW_{3}-free.

    See https://www.graphclasses.org/classes/gc_590

    Complexity of naïve matching: O(n^7)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["BW_{3}"])


@assign_fisc(["K_{7}"])
@assign_class_id("gc_1343")
@lru_cache(maxsize=None)
def is_gc_1343(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is K_{7}-free.

    See https://www.graphclasses.org/classes/gc_1343

    Complexity of naïve matching: O(n^7)
    :type graph: networkx.Graph
    """
    return is_k_clique_free(graph, 7)


@assign_class_id("gc_737")
@lru_cache(maxsize=None)
def is_p7_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is P_{7}-free.

    See https://www.graphclasses.org/classes/gc_737

    Complexity of naïve matching: O(n^7)
    :type graph: networkx.Graph
    """
    # if graph has no P_{4}, then it has no P_{7}
    if is_cograph(graph):
        return True

    return is_h_free(graph, ["P_{7}"])


@assign_class_id("gc_757")
@lru_cache(maxsize=None)
def is_gc_757(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P, T_{2})-free.

    See https://www.graphclasses.org/classes/gc_757

    Complexity of naïve matching: O(n^7)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["P", "T_{2}"])


@assign_class_id("AUTO_1464")
@lru_cache(maxsize=None)
def is_auto_1464(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co(P), co(T_{2}))-free.

    See https://www.graphclasses.org/classes/AUTO_1464

    Complexity of naïve matching: O(n^7)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["co(P)", "co(T_{2})"])


@assign_class_id("AUTO_1461")
@lru_cache(maxsize=None)
def is_auto_1461(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co(P), co(P_{7}))-free.

    See https://www.graphclasses.org/classes/AUTO_1461

    Complexity of naïve matching: O(n^7)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["co(P)", "co(P_{7})"])


@assign_class_id("gc_818")
@lru_cache(maxsize=None)
def is_gc_818(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P, star_{1, 2, 3})-free.

    See https://www.graphclasses.org/classes/gc_818

    Complexity of naïve matching: O(n^7)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["P", "star_{1,2,3}"])


@assign_class_id("AUTO_1459")
@lru_cache(maxsize=None)
def is_auto_1459(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co(P), co(star_{1, 2, 3}))-free.

    See https://www.graphclasses.org/classes/AUTO_1459

    Complexity of naïve matching: O(n^7)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["co(P)", "co(star_{1,2,3})"])


@assign_class_id("gc_813")
@lru_cache(maxsize=None)
def is_gc_813(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P, P_{7})-free.

    See https://www.graphclasses.org/classes/gc_813

    Complexity of naïve matching: O(n^7)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["P", "P_{7}"])


@assign_class_id("gc_619")
@lru_cache(maxsize=None)
def is_gc_619(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (X_{38}, gem, house)-free.

    See https://www.graphclasses.org/classes/gc_619

    Complexity of naïve matching: O(n^7)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["house", "gem", "X_{38}"])


@assign_class_id("AUTO_2110")
@lru_cache(maxsize=None)
def is_auto_2110(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co(P_{6}), co(X_{30}), co(X_{8}))-free.

    See https://www.graphclasses.org/classes/AUTO_2110

    Complexity of naïve matching: O(n^7)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["co(P_{6})", "co(X_{30})", "co(X_{8})"])


@assign_class_id("AUTO_1484")
@lru_cache(maxsize=None)
def is_auto_1484(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{5}, co(X_{38}), co-gem)-free.

    See https://www.graphclasses.org/classes/AUTO_1484

    Complexity of naïve matching: O(n^7)
    :type graph: networkx.Graph
    """
    return (
            is_p5_free(graph) and is_co_gem_free(graph) and is_h_free(graph, ["co(X_{38})"])
    )


@assign_class_id("gc_1276")
@lru_cache(maxsize=None)
def is_gc_1276(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (5-pan, T_{2}, X_{172})-free.

    See https://www.graphclasses.org/classes/gc_1276

    Complexity of naïve matching: O(n^7)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["X_{172}", "5-pan", "T_{2}"])


@assign_class_id("AUTO_1820")
@lru_cache(maxsize=None)
def is_auto_1820(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co(5-pan), co(T_{2}), co(X_{172}))-free.

    See https://www.graphclasses.org/classes/AUTO_1820

    Complexity of naïve matching: O(n^7)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["co(5-pan)", "co(X_{172})", "co(T_{2})"])


@assign_class_id("AUTO_1526")
@lru_cache(maxsize=None)
def is_auto_1526(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, C_{5}, co(T_{2}))-free.

    See https://www.graphclasses.org/classes/AUTO_1526

    Complexity of naïve matching: O(n^7)
    :type graph: networkx.Graph
    """
    return is_2k2_free(graph) and is_h_free(graph, ["C_{5}", "co(T_{2})"])


@assign_class_id("gc_759")
@lru_cache(maxsize=None)
def is_gc_759(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{3, 3}-e, P_{5}, X_{99})-free.

    See https://www.graphclasses.org/classes/gc_759

    Complexity of naïve matching: O(n^7)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_h_free(graph, ["K_{3,3}-e", "X_{99}"])


@assign_class_id("AUTO_2125")
@lru_cache(maxsize=None)
def is_auto_2125(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{3} + e, co(X_{99}), house)-free.

    See https://www.graphclasses.org/classes/AUTO_2125

    Complexity of naïve matching: O(n^7)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["house", "2K_{3} + e", "co(X_{99})"])


@assign_class_id("gc_401")
@lru_cache(maxsize=None)
def is_gc_401(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{4}, C_{5}, T_{2})-free.

    See https://www.graphclasses.org/classes/gc_401

    Complexity of naïve matching: O(n^7)
    :type graph: networkx.Graph
    """
    return is_c4_free(graph) and is_h_free(graph, ["C_{5}", "T_{2}"])


@assign_class_id("gc_683")
@lru_cache(maxsize=None)
def is_gc_683(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{6}, X_{30}, X_{8})-free.

    See https://www.graphclasses.org/classes/gc_683

    Complexity of naïve matching: O(n^7)
    :type graph: networkx.Graph
    """
    return is_p6_free(graph) and is_h_free(graph, ["X_{30}", "X_{8}"])


@assign_class_id("gc_808")
@lru_cache(maxsize=None)
def is_gc_808(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{6}, K_{3, 3}+e, P, P_{7}, X_{37},
    X_{41})-free.

    See https://www.graphclasses.org/classes/gc_808

    Complexity of naïve matching: O(n^7)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["P", "C_{6}", "K_{3,3}+e", "X_{37}", "X_{41}", "P_{7}"])


@assign_class_id("gc_166")
@lru_cache(maxsize=None)
def is_gc_166(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, C_{4}, C_{5}, S_{3}, co-rising sun,
    net)-free.

    See https://www.graphclasses.org/classes/gc_166

    Complexity of naïve matching: O(n^7)
    :type graph: networkx.Graph
    """
    return is_split(graph) and is_h_free(graph, ["S_{3}", "net", "co-rising sun"])


@assign_class_id("AUTO_1463")
@lru_cache(maxsize=None)
def is_auto_1463(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{3} U P_{3}, co(C_{6}), co(P), co(P_{7}),
    co(X_{37}), co(X_{41}))-free.

    See https://www.graphclasses.org/classes/AUTO_1463

    Complexity of naïve matching: O(n^7)
    :type graph: networkx.Graph
    """
    return is_h_free(
        graph,
        [
            "co(P)",
            "co(X_{37})",
            "K_{3} U P_{3}",
            "co(C_{6})",
            "co(P_{7})",
            "co(X_{41})",
        ],
    )


@assign_class_id("AUTO_1536")
@lru_cache(maxsize=None)
def is_auto_1536(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, C_{4}, C_{5}, S_{3}, net, rising
    sun)-free.

    See https://www.graphclasses.org/classes/AUTO_1536

    Complexity of naïve matching: O(n^7)
    :type graph: networkx.Graph
    """
    return is_split(graph) and is_h_free(graph, ["S_{3}", "net", "rising sun"])


@assign_class_id("gc_27")
@lru_cache(maxsize=None)
def is_superbrittle(graph: nx.Graph) -> bool:
    """
    A graph G is superbrittle iff in every induced subgraph of G no vertex is both a midpoint of an
    induced P4 and an endpoint of an induced P4 .

    https://www.graphclasses.org/classes/gc_27

    Complexity of naïve matching: O(n^7)

    :param graph:
    :return:
    """
    return is_gc_268(graph) and is_h_free(graph, ["A", "co(A)", "parapluie", "parachute"])
    # naive algorithm is much faster than this O(n^5) attempt:
    # return empty_graph_by_removing_vertices(graph, vertex_is_superbrittle)


@assign_class_id("gc_972")
@lru_cache(maxsize=None)
def is_gc_972(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, S_{3}, X_{11}, co(3K_{2}), co(C_{7}), co(P_{2} U P_{4}),
    co(X_{173}))-free.

    See https://www.graphclasses.org/classes/gc_972

    Complexity of naïve matching: O(n^7)
    :type graph: networkx.Graph
    """
    return is_h_free(
        graph,
        [
            "C_{5}",
            "S_{3}",
            "co(3K_{2})",
            "co(P_{2} U P_{4})",
            "co(X_{173})",
            "co(C_{7})",
            "X_{11}",
        ],
    )


@assign_class_id("AUTO_1485")
@lru_cache(maxsize=None)
def is_auto_1485(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{2} U K_{3}, P_{5}, co(X_{37}), co(X_{38}), co-
    diamond, co-domino, co-twin-C_{5})-free.

    See https://www.graphclasses.org/classes/AUTO_1485

    Complexity of naïve matching: O(n^7)
    :type graph: networkx.Graph
    """
    return (
            is_co_diamond_free(graph)
            and is_p5_free(graph)
            and is_k2_u_k3_free(graph)
            and is_h_free(
        graph,
        [
            "co(X_{37})",
            "co-twin-C_{5}",
            "co-domino",
            "co(X_{38})",
        ],
    )
    )


@assign_class_id("AUTO_2188")
@lru_cache(maxsize=None)
def is_auto_2188(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (3K_{2}, C_{5}, C_{7}, P_{2} U P_{4}, X_{173}, co(X_{11}), net)-free.

    See https://www.graphclasses.org/classes/AUTO_2188

    Complexity of naïve matching: O(n^7)
    :type graph: networkx.Graph
    """
    return is_p2up4_free(graph) and is_h_free(
        graph,
        ["C_{5}", "3K_{2}", "net", "co(X_{11})", "C_{7}", "X_{173}"],
    )


@assign_class_id("gc_618")
@lru_cache(maxsize=None)
def is_gc_618(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{2, 3}, X_{37}, X_{38}, diamond, domino, house, twin-C_{5})-free.

    See https://www.graphclasses.org/classes/gc_618

    Complexity of naïve matching: O(n^7)
    :type graph: networkx.Graph
    """
    return is_k23_free(graph) and is_h_free(
        graph,
        ["diamond", "house", "X_{37}", "twin-C_{5}", "domino", "X_{38}"],
    )


@assign_class_id("gc_245")
@lru_cache(maxsize=None)
def is_gc_245(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, C_{4}, C_{5}, S_{3}, co-rising sun, net,
    rising sun)-free.

    See https://www.graphclasses.org/classes/gc_245

    Complexity of naïve matching: O(n^7)
    :type graph: networkx.Graph
    """
    return is_split(graph) and is_h_free(
        graph,
        ["S_{3}", "net", "co-rising sun", "rising sun"],
    )


@assign_class_id("gc_713")
@lru_cache(maxsize=None)
def is_gc_713(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (4-fan, K_{1, 4}, W_{4}, W_{5}, co(A U K_{1}),
    co(co-fork U K_{1}), co(gem U K_{1}), co(net U K_{1}))-free.

    See https://www.graphclasses.org/classes/gc_713

    Complexity of naïve matching: O(n^7)
    :type graph: networkx.Graph
    """
    return is_k14_free(graph) and is_h_free(
        graph,
        [
            "W_{4}",
            "W_{5}",
            "4-fan",
            "co(co-fork U K_{1})",
            "co(gem U K_{1})",
            "co(net U K_{1})",
            "co(A U K_{1})",
        ],
    )


@assign_class_id("AUTO_2111")
@lru_cache(maxsize=None)
def is_auto_2111(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (3K_{1}, C_{5}, K_{5} - e, co(C_{6} U K_{1}), co(C_{7}),
    co(K_{3, 3} U K_{1}), co(K_{3, 3}-e U K_{1}), co(domino U K_{1}))-free.

    See https://www.graphclasses.org/classes/AUTO_2111

    Complexity of naïve matching: O(n^7)
    :type graph: networkx.Graph
    """
    return is_3k1_free(graph) and is_h_free(
        graph,
        [
            "C_{5}",
            "K_{5} - e",
            "co(K_{3,3} U K_{1})",
            "co(domino U K_{1})",
            "co(C_{7})",
            "co(C_{6} U K_{1})",
            "co(K_{3,3}-e U K_{1})",
        ],
    )


@assign_class_id("AUTO_2120")
@lru_cache(maxsize=None)
def is_auto_2120(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (A U K_{1}, co(K_{1, 4}), co(W_{4}), co(W_{5}),
    co-4-fan, co-fork U K_{1}, gem U K_{1}, net U K_{1})-free.

    See https://www.graphclasses.org/classes/AUTO_2120

    Complexity of naïve matching: O(n^7)
    :type graph: networkx.Graph
    """
    return is_h_free(
        graph,
        [
            "co(K_{1,4})",
            "co(W_{4})",
            "co-fork U K_{1}",
            "co(W_{5})",
            "gem U K_{1}",
            "co-4-fan",
            "net U K_{1}",
            "A U K_{1}",
        ],
    )


@assign_class_id("gc_697")
@lru_cache(maxsize=None)
def is_gc_697(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (A, H, K_{3, 3}, K_{3, 3}-e, T_{2}, X_{18},
    X_{45}, domino, triangle)-free.

    See https://www.graphclasses.org/classes/gc_697

    Complexity of naïve matching: O(n^7)
    :type graph: networkx.Graph
    """
    return is_triangle_free(graph) and is_h_free(
        graph,
        [
            "X_{45}",
            "X_{18}",
            "K_{3,3}",
            "H",
            "A",
            "K_{3,3}-e",
            "domino",
            "T_{2}",
        ],
    )


@assign_class_id("gc_696")
@lru_cache(maxsize=None)
def is_gc_696(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (BW_{3}, C_{5}, K_{3, 4}, K_{3, 4}-e, T_{2},
    X_{18}, X_{92}, X_{93}, triangle)-free.

    See https://www.graphclasses.org/classes/gc_696

    Complexity of naïve matching: O(n^7)
    :type graph: networkx.Graph
    """
    return is_triangle_free(graph) and is_h_free(
        graph,
        [
            "C_{5}",
            "X_{18}",
            "BW_{3}",
            "T_{2}",
            "K_{3,4}-e",
            "X_{93}",
            "K_{3,4}",
            "X_{92}",
        ],
    )


@assign_class_id("AUTO_2115")
@lru_cache(maxsize=None)
def is_auto_2115(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (3K_{1}, C_{5}, K_{3} U K_{4}, co(BW_{3}),
    co(K_{3, 4}-e), co(T_{2}), co(X_{18}), co(X_{92}), co(X_{93}))-free.

    See https://www.graphclasses.org/classes/AUTO_2115

    Complexity of naïve matching: O(n^7)
    :type graph: networkx.Graph
    """
    return is_3k1_free(graph) and is_h_free(
        graph,
        [
            "C_{5}",
            "co(X_{18})",
            "co(X_{92})",
            "K_{3} U K_{4}",
            "co(T_{2})",
            "co(X_{93})",
            "co(BW_{3})",
            "co(K_{3,4}-e)",
        ],
    )


@assign_class_id("AUTO_1468")
@lru_cache(maxsize=None)
def is_auto_1468(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{3}, 2K_{3} + e, 3K_{1}, co(A), co(H),
    co(T_{2}), co(X_{18}), co(X_{45}), co-domino)-free.

    See https://www.graphclasses.org/classes/AUTO_1468

    Complexity of naïve matching: O(n^7)
    :type graph: networkx.Graph
    """
    return is_3k1_free(graph) and is_h_free(
        graph,
        [
            "co(H)",
            "co(X_{18})",
            "2K_{3} + e",
            "co(A)",
            "co-domino",
            "2K_{3}",
            "co(X_{45})",
            "co(T_{2})",
        ],
    )


@assign_class_id("AUTO_2089")
@lru_cache(maxsize=None)
def is_auto_2089(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, C_{6}, P_{6}, co(C_{6}), co(P_{6}),
    co(X_{17}), co(X_{18}), co(X_{5}), co(X_{98}), co-antenna, co-domino)-free.

    See https://www.graphclasses.org/classes/AUTO_2089

    Complexity of naïve matching: O(n^7)
    :type graph: networkx.Graph
    """
    return is_p6_free(graph) and is_h_free(
        graph,
        [
            "C_{5}",
            "C_{6}",
            "co(P_{6})",
            "co-antenna",
            "co(X_{18})",
            "co(X_{5})",
            "co(C_{6})",
            "co-domino",
            "co(X_{98})",
            "co(X_{17})",
        ],
    )


@assign_class_id("gc_537")
@lru_cache(maxsize=None)
def is_gc_537(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, C_{6}, P_{6}, X_{17}, X_{18}, X_{5}, X_{98}, co(C_{6}),
    co(P_{6}), antenna, domino)-free.

    See https://www.graphclasses.org/classes/gc_537

    Complexity of naïve matching: O(n^7)
    :type graph: networkx.Graph
    """
    return is_p6_free(graph) and is_h_free(
        graph,
        [
            "C_{5}",
            "C_{6}",
            "co(P_{6})",
            "antenna",
            "X_{18}",
            "co(C_{6})",
            "X_{98}",
            "domino",
            "X_{5}",
            "X_{17}",
        ],
    )


@assign_class_id("gc_688")
@lru_cache(maxsize=None)
def is_gc_688(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{3, 3} U K_{1}, K_{4}, W_{4} U K_{1}, W_{5},
    X_{86}, X_{87}, X_{88}, X_{89}, X_{90}, co(C_{7}), co(X_{38}), co(X_{39}),
    co(butterfly U K_{1}), co-diamond)-free.

    See https://www.graphclasses.org/classes/gc_688

    Complexity of naïve matching: O(n^7)
    :type graph: networkx.Graph
    """
    return (
            is_k4_free(graph)
            and is_co_diamond_free(graph)
            and is_h_free(
        graph,
        [
            "W_{5}",
            "W_{4} U K_{1}",
            "co(butterfly U K_{1})",
            "K_{3,3} U K_{1}",
            "co(X_{39})",
            "X_{88}",
            "co(X_{38})",
            "X_{87}",
            "co(C_{7})",
            "X_{89}",
            "X_{86}",
            "X_{90}",
        ],
    )
    )


@assign_class_id("AUTO_2596")
@lru_cache(maxsize=None)
def is_auto_2596(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (4K_{1}, C_{7}, X_{38}, X_{39}, co(K_{3, 3} U
    K_{1}), co(W_{4} U K_{1}), co(W_{5}), co(X_{86}), co(X_{87}), co(X_{88}),
    co(X_{89}), co(X_{90}), butterfly U K_{1}, diamond)-free.

    See https://www.graphclasses.org/classes/AUTO_2596

    Complexity of naïve matching: O(n^7)
    :type graph: networkx.Graph
    """
    return is_4k1_free(graph) and is_h_free(
        graph,
        [
            "diamond",
            "co(W_{5})",
            "co(W_{4} U K_{1})",
            "butterfly U K_{1}",
            "co(X_{88})",
            "co(K_{3,3} U K_{1})",
            "X_{39}",
            "co(X_{90})",
            "co(X_{87})",
            "C_{7}",
            "co(X_{86})",
            "co(X_{89})",
            "X_{38}",
        ],
    )


@assign_class_id("AUTO_1474")
@lru_cache(maxsize=None)
def is_auto_1474(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (3K_{2}, C_{4} U P_{2}, C_{5}, C_{6}, K_{2} U
    K_{3}, K_{3, 3}, K_{3, 3}+e, P_{2} U P_{4}, P_{6}, X_{18}, X_{5},
    co(2P_{3}), co(C_{6}), co(C_{7}), co(X_{84}), antenna, domino, fish)-free.

    See https://www.graphclasses.org/classes/AUTO_1474

    Complexity of naïve matching: O(n^7)
    :type graph: networkx.Graph
    """
    return (
            is_p6_free(graph)
            and is_p2up4_free(graph)
            and is_k2_u_k3_free(graph)
            and is_h_free(
        graph,
        [
            "C_{4} U P_{2}",
            "C_{5}",
            "C_{6}",
            "antenna",
            "co(2P_{3})",
            "fish",
            "3K_{2}",
            "K_{3,3}",
            "K_{3,3}+e",
            "X_{18}",
            "co(C_{6})",
            "co(X_{84})",
            "X_{5}",
            "domino",
            "co(C_{7})",
        ],
    )
    )


@assign_class_id("gc_664")
@lru_cache(maxsize=None)
def is_gc_664(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{3}, 2P_{3}, C_{5}, C_{6}, C_{7}, K_{2, 3}, K_{3} U P_{3},
    X_{84}, co(3K_{2}), co(C_{4} U P_{2}), co(C_{6}), co(P_{2} U P_{4}), co(P_{6}), co(X_{18}),
    co(X_{5}), co-antenna, co-domino, co-fish)-free.

    See https://www.graphclasses.org/classes/gc_664

    Complexity of naïve matching: O(n^7)
    :type graph: networkx.Graph
    """
    return is_k23_free(graph) and is_h_free(
        graph,
        [
            "C_{5}",
            "C_{6}",
            "co(P_{6})",
            "co-antenna",
            "co-fish",
            "K_{3} U P_{3}",
            "X_{84}",
            "2P_{3}",
            "co(X_{18})",
            "co(X_{5})",
            "co(3K_{2})",
            "co(C_{6})",
            "co-domino",
            "co(P_{2} U P_{4})",
            "co(C_{4} U P_{2})",
            "2K_{3}",
            "C_{7}",
        ],
    )


@assign_class_id("gc_1217")
@lru_cache(maxsize=None)
def is_gc_1217(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{3}, 2K_{3} + e, 2P_{3}, C_{5}, C_{6}, C_{7},
    K_{2, 3}, K_{3} U P_{3}, W_{4}, X_{84}, X_{95}, co(A), co(C_{6}), co(P_{6}),
    co(X_{5}), co(X_{98}), butterfly, co-domino, co-fish, fish)-free.

    See https://www.graphclasses.org/classes/gc_1217

    Complexity of naïve matching: O(n^7)
    :type graph: networkx.Graph
    """
    return is_k23_free(graph) and is_h_free(
        graph,
        [
            "W_{4}",
            "butterfly",
            "C_{5}",
            "co-fish",
            "co(P_{6})",
            "fish",
            "2P_{3}",
            "2K_{3} + e",
            "co(A)",
            "co-domino",
            "2K_{3}",
            "C_{6}",
            "X_{84}",
            "co(X_{5})",
            "co(X_{98})",
            "co(C_{6})",
            "X_{95}",
            "K_{3} U P_{3}",
            "C_{7}",
        ],
    )


@assign_class_id("AUTO_1735")
@lru_cache(maxsize=None)
def is_auto_1735(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (A, C_{5}, C_{6}, K_{2} U K_{3}, K_{3, 3}, K_{3,3}+e, K_{3, 3}-e,
    P_{6}, X_{5}, X_{98}, co(2P_{3}), co(C_{6}), co(C_{7}), co(W_{4}), co(X_{84}), co(X_{95}),
    co-butterfly, co-fish, domino, fish)-free.

    See https://www.graphclasses.org/classes/AUTO_1735

    Complexity of naïve matching: O(n^7)

    :type graph: networkx.Graph
    """
    return (
            is_p6_free(graph)
            and is_k2_u_k3_free(graph)
            and is_h_free(
        graph,
        [
            "co(W_{4})",
            "co-butterfly",
            "C_{5}",
            "co-fish",
            "fish",
            "co(2P_{3})",
            "co(X_{95})",
            "C_{6}",
            "K_{3,3}+e",
            "co(C_{6})",
            "X_{98}",
            "domino",
            "X_{5}",
            "K_{3,3}",
            "A",
            "K_{3,3}-e",
            "co(X_{84})",
            "co(C_{7})",
        ],
    )
    )


@assign_class_id("AUTO_1493")
@lru_cache(maxsize=None)
def is_auto_1493(graph: nx.Graph) -> bool:
    """



    :param graph:
    :return:
    """
    return (
            is_anti_hole_free(graph)
            and is_p5_free(graph)
            and is_h_free(
        graph,
        [
            "S_{3}",
            "co(A)",
            "co(E)",
            "co(X_{1})",
            "co-domino",
            "co-rising sun",
            "net",
        ],
    )
    )


@assign_class_id("gc_530")
@lru_cache(maxsize=None)
def is_gc_530(graph: nx.Graph) -> bool:
    """



    :param graph:
    :return:
    """
    return is_hole_free(graph) and is_h_free(
        graph,
        [
            "house",
            "S_{3}",
            "A",
            "E",
            "X_{1}",
            "domino",
            "rising sun",
            "net",
        ],
    )


# All recognizers for patterns on at most 8 vertices ----------------------------------------------
@assign_class_id("AUTO_2142")
@lru_cache(maxsize=None)
def is_auto_2142(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co(P), co-star_{1, 2, 4})-free.

    See https://www.graphclasses.org/classes/AUTO_2142

    Complexity of naïve matching: O(n^8)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["co(P)", "co-star_{1,2,4}"])


@assign_class_id("AUTO_2124")
@lru_cache(maxsize=None)
def is_auto_2124(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co(P), co(P_{8}))-free.

    See https://www.graphclasses.org/classes/AUTO_2124

    Complexity of naïve matching: O(n^8)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["co(P)", "co(P_{8})"])


@assign_class_id("gc_588")
@lru_cache(maxsize=None)
def is_gc_588(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (X_{79}, X_{80})-free.

    See https://www.graphclasses.org/classes/gc_588

    Complexity of naïve matching: O(n^8)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["X_{79}", "X_{80}"])


@assign_class_id("AUTO_2079")
@lru_cache(maxsize=None)
def is_auto_2079(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{4}, house)-free.

    See https://www.graphclasses.org/classes/AUTO_2079

    Complexity of naïve matching: O(n^8)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["house", "2K_{4}"])


@assign_class_id("gc_819")
@lru_cache(maxsize=None)
def is_gc_819(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P, star_{1, 2, 4})-free.

    See https://www.graphclasses.org/classes/gc_819

    Complexity of naïve matching: O(n^8)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["P", "star_{1,2,4}"])


@assign_class_id("AUTO_2096")
@lru_cache(maxsize=None)
def is_auto_2096(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co(X_{79}), co(X_{80}))-free.

    See https://www.graphclasses.org/classes/AUTO_2096

    Complexity of naïve matching: O(n^8)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["co(X_{79})", "co(X_{80})"])


@assign_class_id("gc_432")
@lru_cache(maxsize=None)
def is_gc_432(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{4, 4}, P_{5})-free.

    See https://www.graphclasses.org/classes/gc_432

    Complexity of naïve matching: O(n^8)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_h_free(graph, ["K_{4,4}"])


@assign_class_id("gc_758")
@lru_cache(maxsize=None)
def is_gc_758(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P, P_{8})-free.

    See https://www.graphclasses.org/classes/gc_758

    Complexity of naïve matching: O(n^8)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["P", "P_{8}"])


@assign_class_id("gc_386")
@lru_cache(maxsize=None)
def is_gc_386(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (S_{3}, S_{4}, net)-free.

    See https://www.graphclasses.org/classes/gc_386

    Complexity of naïve matching: O(n^8)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["net", "S_{3}", "S_{4}"])


@assign_class_id("gc_647")
@lru_cache(maxsize=None)
def is_gc_647(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{5}, X_{82}, X_{83})-free.

    See https://www.graphclasses.org/classes/gc_647

    Complexity of naïve matching: O(n^8)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_h_free(graph, ["X_{82}", "X_{83}"])


@assign_class_id("AUTO_2104")
@lru_cache(maxsize=None)
def is_auto_2104(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co(X_{82}), co(X_{83}), house)-free.

    See https://www.graphclasses.org/classes/AUTO_2104

    Complexity of naïve matching: O(n^8)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["house", "co(X_{82})", "co(X_{83})"])


@assign_class_id("gc_1281")
@lru_cache(maxsize=None)
def is_c4_c5_c6_c7_c8_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{4}, C_{5}, C_{6}, C_{7}, C_{8})-free.

    See https://www.graphclasses.org/classes/gc_1281

    Complexity of naïve matching: O(n^8)
    :type graph: networkx.Graph
    """
    return is_c4_free(graph) and is_h_free(graph, ["C_{5}", "C_{6}", "C_{7}", "C_{8}"])


@assign_class_id("AUTO_1822")
@lru_cache(maxsize=None)
def is_auto_1822(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, C_{5}, co(C_{6}), co(C_{7}), co(C_{8}))-free.

    See https://www.graphclasses.org/classes/AUTO_1822

    Complexity of naïve matching: O(n^8)

    :type graph: networkx.Graph
    """
    return is_2k2_free(graph) and is_h_free(
        graph, ["C_{5}", "co(C_{6})", "co(C_{7})", "co(C_{8})"]
    )


@assign_class_id("gc_1022")
@lru_cache(maxsize=None)
def is_gc_1022(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, C_{6}, X_{164}, X_{165}, sunlet_{4}, triangle)-free.

    See https://www.graphclasses.org/classes/gc_1022

    Complexity of naïve matching: O(n^8)
    :type graph: networkx.Graph
    """
    return is_triangle_free(graph) and is_h_free(
        graph, ["C_{5}", "C_{6}", "sunlet_{4}", "X_{165}", "X_{164}"]
    )


@assign_class_id("AUTO_1745")
@lru_cache(maxsize=None)
def is_auto_1745(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, 3K_{1}, C_{5}, co(C_{6}), co(C_{7}), co(C_{8}))-free.

    See https://www.graphclasses.org/classes/AUTO_1745

    Complexity of naïve matching: O(n^8)
    :type graph: networkx.Graph
    """
    return (
            is_3k1_free(graph)
            and is_2k2_free(graph)
            and is_h_free(graph, ["C_{5}", "co(C_{6})", "co(C_{7})", "co(C_{8})"])
    )


@assign_class_id("AUTO_2277")
@lru_cache(maxsize=None)
def is_auto_2277(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (3K_{1}, C_{5}, co(C_{6}), co(X_{164}), co(X_{165}),
    co(sunlet_{4}))-free.

    See https://www.graphclasses.org/classes/AUTO_2277

    Complexity of naïve matching: O(n^8)
    :type graph: networkx.Graph
    """
    return is_3k1_free(graph) and is_h_free(
        graph,
        [
            "C_{5}",
            "co(C_{6})",
            "co(X_{165})",
            "co(sunlet_{4})",
            "co(X_{164})",
        ],
    )


@assign_class_id("AUTO_2109")
@lru_cache(maxsize=None)
def is_auto_2109(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, 3K_{1}, C_{5}, co(C_{6}), co(C_{7}), co(C_{8}), co(H),
    co(X_{85}))-free.

    See https://www.graphclasses.org/classes/AUTO_2109

    Complexity of naïve matching: O(n^8)
    :type graph: networkx.Graph
    """
    return (
            is_3k1_free(graph)
            and is_2k2_free(graph)
            and is_h_free(
        graph,
        [
            "C_{5}",
            "co(H)",
            "co(C_{6})",
            "co(X_{85})",
            "co(C_{7})",
            "co(C_{8})",
        ],
    )
    )


@assign_class_id("gc_672")
@lru_cache(maxsize=None)
def is_gc_672(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{4}, C_{5}, C_{6}, C_{7}, C_{8}, H, X_{85},
    triangle)-free.

    See https://www.graphclasses.org/classes/gc_672

    Complexity of naïve matching: O(n^8)
    :type graph: networkx.Graph
    """
    return is_girth_at_least_9(graph) and is_h_free(graph, ["H", "X_{85}"])


@assign_class_id("AUTO_2787")
@lru_cache(maxsize=None)
def is_auto_2787(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, 3K_{1}, C_{5}, co(C_{6}), co(C_{7}),
    co(C_{8}), co(H), co(K_{1, 4}), co(X_{85}))-free.

    See https://www.graphclasses.org/classes/AUTO_2787

    Complexity of naïve matching: O(n^8)
    :type graph: networkx.Graph
    """
    return (
            is_3k1_free(graph)
            and is_2k2_free(graph)
            and is_h_free(
        graph,
        [
            "C_{5}",
            "co(K_{1,4})",
            "co(H)",
            "co(C_{6})",
            "co(X_{85})",
            "co(C_{7})",
            "co(C_{8})",
        ],
    )
    )


@assign_class_id("AUTO_740")
@lru_cache(maxsize=None)
def is_auto_740(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{4}, C_{5}, C_{6}, C_{7}, C_{8}, H, K_{1, 4}, X_{85},
    triangle)-free.

    See https://www.graphclasses.org/classes/AUTO_740

    Complexity of naïve matching: O(n^8)

    :type graph: networkx.Graph
    """
    return (
            is_girth_at_least_9(graph)
            and is_k14_free(graph)
            and is_h_free(
        graph,
        [
            "H",
            "X_{85}",
        ],
    )
    )


@assign_class_id("AUTO_2990")
@lru_cache(maxsize=None)
def is_auto_2990(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, C_{4}, C_{5}, H, S_{3}, X_{160}, co(X_{159}), net, rising
    sun)-free.

    See https://www.graphclasses.org/classes/AUTO_2990

    Complexity of naïve matching: O(n^8)

    :type graph: networkx.Graph
    """
    return is_split(graph) and is_h_free(
        graph,
        [
            "H",
            "S_{3}",
            "net",
            "co(X_{159})",
            "rising sun",
            "X_{160}",
        ],
    )


@assign_class_id("AUTO_744")
@lru_cache(maxsize=None)
def is_auto_744(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, C_{4}, C_{5}, S_{3}, X_{159}, X_{160}, co(H), co-rising sun,
    net)-free.

    See https://www.graphclasses.org/classes/AUTO_744

    Complexity of naïve matching: O(n^8)

    :type graph: networkx.Graph
    """
    return is_split(graph) and is_h_free(
        graph,
        [
            "co(H)",
            "S_{3}",
            "net",
            "co-rising sun",
            "X_{159}",
            "X_{160}",
        ],
    )


@assign_class_id("AUTO_1814")
@lru_cache(maxsize=None)
def is_auto_1814(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{4}, C_{5}, C_{6}, C_{7}, C_{8}, K_{1, 4}, K_{5}, K_{5} - e,
    co(K_{3} U 2K_{1}), co(P_{3} U 2K_{1}), co(claw U K_{1}), butterfly, cricket, dart, gem)-free.

    See https://www.graphclasses.org/classes/AUTO_1814

    Complexity of naïve matching: O(n^8)
    :type graph: networkx.Graph
    """
    return (
            is_c4_free(graph)
            and is_k14_free(graph)
            and is_odd_clique_free(graph, 5)
            and is_h_free(
        graph,
        [
            "C_{5}",
            "dart",
            "co(P_{3} U 2K_{1})",
            "cricket",
            "gem",
            "K_{5} - e",
            "co(K_{3} U 2K_{1})",
            "butterfly",
            "co(claw U K_{1})",
            "C_{6}",
            "C_{7}",
            "C_{8}",
        ],
    )
    )


@assign_class_id("AUTO_3802")
@lru_cache(maxsize=None)
def is_auto_3802(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, 5K_{1}, C_{5}, K_{3} U 2K_{1}, P_{3} U 2K_{1}, co(C_{6}),
    co(C_{7}), co(C_{8}), co(K_{1, 4}), co(K_{5} - e), claw U K_{1}, co-butterfly, co-cricket,
    co-dart, co-gem)-free.

    See https://www.graphclasses.org/classes/AUTO_3802

    Complexity of naïve matching: O(n^8)
    :type graph: networkx.Graph
    """
    return (
            is_co_gem_free(graph)
            and is_2k2_free(graph)
            and is_c5_free(graph)
            and is_odd_co_clique_free(graph, 5)  # K_{5}
            and is_h_u_2k1_free(graph, is_co_p3_free)  # co(K_{5} - e)
            and is_h_u_k1_free(graph, is_claw_free)  # claw U K_{1}
            and is_h_u_2k1_free(graph, is_triangle_free)
            and is_h_u_2k1_free(graph, is_p3_free)
            and is_h_free(
        graph,
        [
            "co-butterfly",
            "co-dart",
            "co(K_{1,4})",
            "co-cricket",
            "co(C_{6})",
            "co(C_{7})",
            "co(C_{8})",
        ],
    )
    )


@assign_class_id("AUTO_2139")
@lru_cache(maxsize=None)
def is_auto_2139(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2P_{3}, 3K_{2}, C_{4}, C_{5}, H, P_{2} U P_{4},
    P_{5}, S_{3}, X_{1}, X_{160}, co(X_{159}), co(X_{161}), co(X_{162}),
    co(X_{46}), co(X_{70}), net, rising sun)-free.

    See https://www.graphclasses.org/classes/AUTO_2139

    Complexity of naïve matching: O(n^8)
    :type graph: networkx.Graph
    """
    return (
            is_c4_free(graph)
            and is_p2up4_free(graph)
            and is_p5_free(graph)
            and is_h_free(
        graph,
        [
            "C_{5}",
            "3K_{2}",
            "H",
            "S_{3}",
            "2P_{3}",
            "net",
            "co(X_{70})",
            "X_{1}",
            "co(X_{159})",
            "co(X_{162})",
            "co(X_{46})",
            "rising sun",
            "X_{160}",
            "co(X_{161})",
        ],
    )
    )


@assign_class_id("gc_806")
@lru_cache(maxsize=None)
def is_gc_806(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, C_{5}, S_{3}, X_{159}, X_{160}, X_{161},
    X_{162}, X_{46}, X_{70}, co(2P_{3}), co(3K_{2}), co(H), co(P_{2} U P_{4}),
    co(X_{1}), co-rising sun, house, net)-free.

    See https://www.graphclasses.org/classes/gc_806

    Complexity of naïve matching: O(n^8)
    :type graph: networkx.Graph
    """
    return is_2k2_free(graph) and is_h_free(
        graph,
        [
            "C_{5}",
            "house",
            "co(H)",
            "co(2P_{3})",
            "S_{3}",
            "co(3K_{2})",
            "co(P_{2} U P_{4})",
            "net",
            "X_{70}",
            "co-rising sun",
            "X_{159}",
            "co(X_{1})",
            "X_{46}",
            "X_{162}",
            "X_{161}",
            "X_{160}",
        ],
    )


@assign_class_id("AUTO_2138")
@lru_cache(maxsize=None)
def is_auto_2138(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2P_{4}, A, C_{5}, C_{6}, C_{7}, E, K_{3, 3}-e, P_{7}, R, X_{1},
    X_{103}, X_{5}, X_{58}, X_{84}, X_{98}, co(C_{6}), co(P_{6}), co(X_{5}), co(sunlet_{4}),
    co-antenna, co-domino, co-rising sun, domino, parachute, parapluie, rising sun,
    twin-house)-free.

    See https://www.graphclasses.org/classes/AUTO_2138

    Complexity of naïve matching: O(n^8)
    :type graph: networkx.Graph
    """
    return is_h_free(
        graph,
        [
            "C_{5}",
            "co(P_{6})",
            "co-domino",
            "C_{6}",
            "X_{84}",
            "co(X_{5})",
            "co-antenna",
            "X_{58}",
            "co(C_{6})",
            "X_{98}",
            "domino",
            "X_{5}",
            "R",
            "E",
            "A",
            "twin-house",
            "K_{3,3}-e",
            "C_{7}",
            "X_{1}",
            "X_{103}",
            "parapluie",
            "rising sun",
            "co-rising sun",
            "parachute",
            "P_{7}",
            "co(sunlet_{4})",
            "2P_{4}",
        ],
    )


@assign_class_id("gc_798")
@lru_cache(maxsize=None)
def is_gc_798(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{3} + e, C_{5}, C_{6}, P_{6}, X_{5},
    co(2P_{4}), co(A), co(C_{6}), co(C_{7}), co(E), co(P_{7}), co(R), co(X_{1}),
    co(X_{103}), co(X_{5}), co(X_{58}), co(X_{84}), co(X_{98}), antenna, co-
    domino, co-rising sun, co-twin-house, domino, parachute, parapluie, rising
    sun, sunlet_{4})-free.

    See https://www.graphclasses.org/classes/gc_798

    Complexity of naïve matching: O(n^8)
    :type graph: networkx.Graph
    """
    return is_p6_free(graph) and is_h_free(
        graph,
        [
            "C_{5}",
            "co(R)",
            "2K_{3} + e",
            "co(A)",
            "co-domino",
            "C_{6}",
            "co(X_{5})",
            "co(X_{98})",
            "co(E)",
            "co(C_{6})",
            "domino",
            "X_{5}",
            "antenna",
            "co(X_{58})",
            "co-twin-house",
            "co(X_{84})",
            "co(X_{103})",
            "co(P_{7})",
            "co(C_{7})",
            "parapluie",
            "rising sun",
            "co-rising sun",
            "co(X_{1})",
            "parachute",
            "co(2P_{4})",
            "sunlet_{4}",
        ],
    )


# All recognizers for patterns on at most 9 vertices ----------------------------------------------
@assign_class_id("AUTO_2398")
@lru_cache(maxsize=None)
def is_auto_2398(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co(X_{91}), co-claw)-free.

    See https://www.graphclasses.org/classes/AUTO_2398

    Complexity of naïve matching: O(n^9)
    :type graph: networkx.Graph
    """
    return is_co_claw_free(graph) and is_h_free(graph, ["co(X_{91})"])


@assign_class_id("gc_811")
@lru_cache(maxsize=None)
def is_gc_811(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P, star_{1, 2, 5})-free.

    See https://www.graphclasses.org/classes/gc_811

    Complexity of naïve matching: O(n^9)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["P", "star_{1,2,5}"])


@assign_class_id("AUTO_2141")
@lru_cache(maxsize=None)
def is_auto_2141(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co(P), co-star_{1, 2, 5})-free.

    See https://www.graphclasses.org/classes/AUTO_2141

    Complexity of naïve matching: O(n^9)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["co(P)", "co-star_{1,2,5}"])


@assign_class_id("gc_1214")
@lru_cache(maxsize=None)
def is_gc_1214(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (X_{91}, claw)-free.

    See https://www.graphclasses.org/classes/gc_1214

    Complexity of naïve matching: O(n^9)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["claw", "X_{91}"])


@assign_class_id("AUTO_2113")
@lru_cache(maxsize=None)
def is_auto_2113(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, co(X_{91}), co-claw)-free.

    See https://www.graphclasses.org/classes/AUTO_2113

    Complexity of naïve matching: O(n^9)
    :type graph: networkx.Graph
    """
    return (
            is_2k2_free(graph)
            and is_co_claw_free(graph)
            and is_h_free(graph, ["co(X_{91})"])
    )


@assign_class_id("gc_692")
@lru_cache(maxsize=None)
def is_gc_692(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{4}, X_{91}, claw)-free.

    See https://www.graphclasses.org/classes/gc_692

    Complexity of naïve matching: O(n^9)
    :type graph: networkx.Graph
    """
    return is_claw_free(graph) and is_c4_free(graph) and is_h_free(graph, ["X_{91}"])


@assign_class_id("gc_698")
@lru_cache(maxsize=None)
def is_gc_698(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, K_{3, 3}-e, T_{2}, X_{18}, X_{94}, domino, triangle)-free.

    See https://www.graphclasses.org/classes/gc_698

    Complexity of naïve matching: O(n^9)
    :type graph: networkx.Graph
    """
    return is_triangle_free(graph) and is_h_free(
        graph, ["C_{5}", "X_{18}", "K_{3,3}-e", "domino", "T_{2}", "X_{94}"]
    )


@assign_class_id("AUTO_2116")
@lru_cache(maxsize=None)
def is_auto_2116(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{3} + e, 3K_{1}, C_{5}, co(T_{2}), co(X_{18}), co(X_{94}),
    co-domino)-free.

    See https://www.graphclasses.org/classes/AUTO_2116

    Complexity of naïve matching: O(n^9)
    :type graph: networkx.Graph
    """
    return is_3k1_free(graph) and is_h_free(
        graph,
        [
            "C_{5}",
            "co(X_{18})",
            "2K_{3} + e",
            "co-domino",
            "co(T_{2})",
            "co(X_{94})",
        ],
    )


@assign_class_id("AUTO_2090")
@lru_cache(maxsize=None)
def is_auto_2090(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, P_{5}, co(C_{6}), co(C_{7}), co(C_{8}),
    co(P_{8}), co(X_{19}), co(X_{20}), co(X_{21}), co(X_{22}), co-gem)-free.

    See https://www.graphclasses.org/classes/AUTO_2090

    Complexity of naïve matching: O(n^9)
    :type graph: networkx.Graph
    """
    return (
            is_p5_free(graph)
            and is_co_gem_free(graph)
            and is_h_free(
        graph,
        [
            "C_{5}",
            "co(C_{6})",
            "co(X_{20})",
            "co(C_{7})",
            "co(X_{19})",
            "co(C_{8})",
            "co(P_{8})",
            "co(X_{22})",
            "co(X_{21})",
        ],
    )
    )


@assign_class_id("gc_538")
@lru_cache(maxsize=None)
def is_gc_538(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, C_{6}, C_{7}, C_{8}, P_{8}, X_{19}, X_{20}, X_{21}, X_{22},
    gem, house)-free.

    See https://www.graphclasses.org/classes/gc_538

    Complexity of naïve matching: O(n^9)
    :type graph: networkx.Graph
    """
    return (
            is_gem_free(graph)
            and is_c5_free(graph)
            and is_house_free(graph)
            and is_h_free(
        graph,
        [
            "C_{6}",
            "C_{7}",
            "X_{20}",
            "P_{8}",
            "C_{8}",
            "X_{22}",
            "X_{19}",
            "X_{21}",
        ],
    )
    )


@assign_class_id("AUTO_2134")
@lru_cache(maxsize=None)
def is_auto_2134(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{6}, C_{8}, T_{2}, X_{3}, co(BW_{3}),
    co(W_{5}), co(W_{7}), co(X_{103}), co(X_{105}), co(X_{106}), co(X_{107}),
    co(X_{108}), co(X_{109}), co(X_{110}), co(X_{111}), co(X_{112}),
    co(X_{113}), co(X_{114}), co(X_{115}), co(X_{116}), co(X_{117}),
    co(X_{118}), co(X_{119}), co(X_{120}), co(X_{121}), co(X_{122}),
    co(X_{123}), co(X_{124}), co(X_{125}), co(X_{126}), co(X_{53}), co(X_{88}),
    co-X_{104})-free.

    See https://www.graphclasses.org/classes/AUTO_2134

    Complexity of naïve matching: O(n^9)
    :type graph: networkx.Graph
    """
    return is_h_free(
        graph,
        [
            "C_{6}",
            "co(W_{5})",
            "co(X_{103})",
            "co(BW_{3})",
            "co(X_{105})",
            "co(X_{106})",
            "co(X_{88})",
            "X_{3}",
            "co(X_{107})",
            "T_{2}",
            "co-X_{104}",
            "co(X_{116})",
            "co(X_{114})",
            "co(X_{119})",
            "co(X_{108})",
            "co(X_{118})",
            "co(X_{111})",
            "co(X_{115})",
            "C_{8}",
            "co(X_{122})",
            "co(X_{110})",
            "co(X_{120})",
            "co(X_{121})",
            "co(X_{123})",
            "co(X_{125})",
            "co(X_{112})",
            "co(X_{124})",
            "co(X_{113})",
            "co(X_{53})",
            "co(X_{126})",
            "co(X_{117})",
            "co(X_{109})",
            "co(W_{7})",
        ],
    )


@assign_class_id("gc_779")
@lru_cache(maxsize=None)
def is_gc_779(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (BW_{3}, W_{5}, W_{7}, X_{103}, X_{104}, X_{105}, X_{106}, X_{107},
    X_{108}, X_{109}, X_{110}, X_{111}, X_{112}, X_{113}, X_{114}, X_{115}, X_{116}, X_{117},
    X_{118}, X_{119}, X_{120}, X_{121}, X_{122}, X_{123}, X_{124}, X_{125}, X_{126}, X_{53},
    X_{88}, co(C_{6}), co(C_{8}), co(T_{2}), co(X_{3}))-free.

    See https://www.graphclasses.org/classes/gc_779

    Complexity of naïve matching: O(n^9)
    :type graph: networkx.Graph
    """
    return is_h_free(
        graph,
        [
            "co(C_{6})",
            "W_{5}",
            "X_{107}",
            "X_{104}",
            "co(X_{3})",
            "co(T_{2})",
            "X_{103}",
            "X_{88}",
            "BW_{3}",
            "X_{106}",
            "X_{105}",
            "X_{125}",
            "X_{113}",
            "X_{123}",
            "co(C_{8})",
            "X_{114}",
            "X_{115}",
            "X_{53}",
            "X_{116}",
            "X_{111}",
            "X_{117}",
            "X_{108}",
            "X_{126}",
            "X_{109}",
            "X_{121}",
            "X_{122}",
            "X_{110}",
            "X_{124}",
            "X_{119}",
            "X_{112}",
            "X_{120}",
            "X_{118}",
            "W_{7}",
        ],
    )


@assign_class_id("gc_1035")
@lru_cache(maxsize=None)
def is_gc_1035(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (6-fan, C_{4} U P_{2}, C_{5}, C_{6} U K_{1}, C_{7}, K_{2} U K_{3},
    K_{2, 3}, P_{2} U P_{4}, W_{4} U K_{1}, W_{6}, X_{132}, X_{169}, X_{176}, X_{18}, X_{197},
    X_{198}, X_{199}, X_{200}, X_{201}, X_{202}, X_{35}, X_{84}, co(C_{4} U P_{2}),
    co(C_{6} U K_{1}), co(C_{7}), co(P_{2} U P_{4}), co(W_{4} U K_{1}), co(W_{6}), co(X_{132}),
    co(X_{169}), co(X_{176}), co(X_{18}), co(X_{197}), co(X_{198}), co(X_{199}), co(X_{200}),
    co(X_{201}), co(X_{35}), co(X_{84}), co(butterfly U K_{1}), butterfly U K_{1}, co-6-fan,
    co-fish, fish)-free.

    See https://www.graphclasses.org/classes/gc_1035

    Complexity of naïve matching: O(n^9)
    :type graph: networkx.Graph
    """
    return (
            is_k23_free(graph)
            and is_p2up4_free(graph)
            and is_k2_u_k3_free(graph)
            and is_h_free(
        graph,
        [
            "C_{4} U P_{2}",
            "C_{5}",
            "X_{169}",
            "co-fish",
            "fish",
            "X_{198}",
            "co(W_{4} U K_{1})",
            "X_{197}",
            "X_{84}",
            "X_{18}",
            "co(X_{197})",
            "butterfly U K_{1}",
            "W_{4} U K_{1}",
            "co(X_{198})",
            "co(X_{169})",
            "co(X_{18})",
            "co(butterfly U K_{1})",
            "co(X_{84})",
            "co(P_{2} U P_{4})",
            "co(C_{4} U P_{2})",
            "co-6-fan",
            "C_{7}",
            "X_{35}",
            "co(C_{7})",
            "X_{199}",
            "X_{132}",
            "X_{176}",
            "C_{6} U K_{1}",
            "co(X_{176})",
            "W_{6}",
            "X_{200}",
            "co(X_{132})",
            "co(X_{200})",
            "co(W_{6})",
            "co(X_{35})",
            "6-fan",
            "co(X_{199})",
            "co(C_{6} U K_{1})",
            "X_{202}",
            "X_{201}",
            "co(X_{201})",
        ],
    )
    )


@assign_class_id("AUTO_2629")
@lru_cache(maxsize=None)
def is_auto_2629(graph: nx.Graph) -> bool:
    """



    @param graph:
    @return:
    """
    return is_co_gem_free(graph) and is_h_free(
        graph,
        [
            "P_{2} U P_{3}",
            "P_{3} U 2K_{1}",
            "X_{188}",
            "X_{214}",
            "co(W_{4})",
            "co(X_{102})",
            "co(X_{204})",
            "co(X_{209})",
            "co(X_{210})",
            "co(X_{212})",
            "co(X_{213})",
            "co(X_{215})",
            "co(X_{216})",
            "co(X_{217})",
            "co(X_{218})",
            "co(X_{86})",
        ],
    )


@assign_class_id("gc_1365")
@lru_cache(maxsize=None)
def is_gc_1365(graph: nx.Graph) -> bool:
    """



    @param graph:
    @return:
    """
    return is_gem_free(graph) and is_h_free(
        graph,
        [
            "co(P_{2} U P_{3})",
            "co(P_{3} U 2K_{1})",
            "co(X_{188})",
            "X_{214}",
            "W_{4}",
            "X_{102}",
            "X_{204}",
            "X_{209}",
            "X_{210}",
            "X_{212}",
            "X_{213}",
            "X_{215}",
            "X_{216}",
            "X_{217}",
            "X_{218}",
            "X_{86}",
        ],
    )


# All recognizers for patterns on at most 10 vertices ---------------------------------------------
@assign_class_id("gc_1002")
@lru_cache(maxsize=None)
def is_gc_1002(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (3P_{3}, P_{3} U P_{4}, P_{5}, X_{102}, X_{180}, X_{181}, X_{182},
    X_{183}, X_{184}, X_{185}, X_{186}, X_{187}, X_{188}, X_{189}, X_{190}, X_{191}, X_{192},
    X_{193}, co(5-pan), co(A), co(P_{6}), co-twin-C_{5})-free.

    See https://www.graphclasses.org/classes/gc_1002

    Complexity of naïve matching: O(n^10)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_h_free(
        graph,
        [
            "co(P_{6})",
            "co(A)",
            "co-twin-C_{5}",
            "co(5-pan)",
            "P_{3} U P_{4}",
            "X_{184}",
            "X_{102}",
            "X_{188}",
            "X_{186}",
            "X_{182}",
            "X_{185}",
            "X_{187}",
            "X_{189}",
            "X_{190}",
            "X_{192}",
            "X_{193}",
            "X_{180}",
            "X_{181}",
            "X_{191}",
            "3P_{3}",
            "X_{183}",
        ],
    )


@assign_class_id("AUTO_2248")
@lru_cache(maxsize=None)
def is_auto_2248(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (5-pan, A, P_{6}, X_{186}, co(3P_{3}), co(P_{3} U P_{4}),
    co(X_{102}), co(X_{180}), co(X_{181}), co(X_{182}), co(X_{183}), co(X_{184}), co(X_{185}),
    co(X_{187}), co(X_{188}), co(X_{189}), co(X_{190}), co(X_{191}), co(X_{192}), co(X_{193}),
    house, twin-C_{5})-free.

    See https://www.graphclasses.org/classes/AUTO_2248

    Complexity of naïve matching: O(n^10)
    :type graph: networkx.Graph
    """
    return is_p6_free(graph) and is_h_free(
        graph,
        [
            "house",
            "twin-C_{5}",
            "A",
            "5-pan",
            "co(P_{3} U P_{4})",
            "co(X_{102})",
            "co(X_{184})",
            "X_{186}",
            "co(X_{191})",
            "co(X_{187})",
            "co(X_{192})",
            "co(X_{193})",
            "co(X_{185})",
            "co(X_{182})",
            "co(X_{189})",
            "co(X_{181})",
            "co(X_{188})",
            "co(X_{190})",
            "co(X_{180})",
            "co(3P_{3})",
            "co(X_{183})",
        ],
    )


# All recognizers for patterns on at most 11 vertices ---------------------------------------------
@assign_class_id("gc_1330")
@lru_cache(maxsize=None)
def is_gc_1330(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (X_{42}, co(T_{2}), co(X_{205}), co(X_{206}), co(X_{207}),
    co(X_{208}), net)-free.

    See https://www.graphclasses.org/classes/gc_1330

    Complexity of naïve matching: O(n^11)

    :type graph: networkx.Graph
    """
    return is_h_free(
        graph,
        [
            "net",
            "X_{42}",
            "co(T_{2})",
            "co(X_{205})",
            "co(X_{207})",
            "co(X_{206})",
            "co(X_{208})",
        ],
    )


@assign_class_id("AUTO_1892")
@lru_cache(maxsize=None)
def is_auto_1892(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (S_{3}, T_{2}, X_{205}, X_{206}, X_{207}, X_{208}, co(X_{42}))-free.

    See https://www.graphclasses.org/classes/AUTO_1892

    Complexity of naïve matching: O(n^11)
    :type graph: networkx.Graph
    """
    return is_h_free(
        graph,
        ["S_{3}", "T_{2}", "co(X_{42})", "X_{205}", "X_{207}", "X_{206}", "X_{208}"],
    )


@assign_class_id("gc_550")
@lru_cache(maxsize=None)
def is_gc_550(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (A, H, K_{3, 3}, X_{45}, X_{46}, X_{47}, X_{48}, X_{49}, X_{50},
    X_{51}, X_{52}, X_{53}, X_{54}, X_{55}, X_{56}, X_{57}, co(X_{42}))-free.

    See https://www.graphclasses.org/classes/gc_550

    Complexity of naïve matching: O(n^11)
    :type graph: networkx.Graph
    """
    return is_h_free(
        graph,
        [
            "X_{45}",
            "K_{3,3}",
            "H",
            "A",
            "co(X_{42})",
            "X_{46}",
            "X_{52}",
            "X_{49}",
            "X_{50}",
            "X_{48}",
            "X_{51}",
            "X_{47}",
            "X_{53}",
            "X_{55}",
            "X_{56}",
            "X_{54}",
            "X_{57}",
        ],
    )


@assign_class_id("AUTO_2092")
@lru_cache(maxsize=None)
def is_auto_2092(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{3}, X_{42}, co(A), co(H), co(X_{45}), co(X_{46}), co(X_{47}),
    co(X_{48}), co(X_{49}), co(X_{50}), co(X_{51}), co(X_{52}), co(X_{53}), co(X_{54}), co(X_{55}),
    co(X_{56}), co(X_{57}))-free.

    See https://www.graphclasses.org/classes/AUTO_2092

    Complexity of naïve matching: O(n^11)
    :type graph: networkx.Graph
    """
    return is_h_free(
        graph,
        [
            "co(H)",
            "co(A)",
            "2K_{3}",
            "co(X_{45})",
            "X_{42}",
            "co(X_{46})",
            "co(X_{53})",
            "co(X_{51})",
            "co(X_{48})",
            "co(X_{52})",
            "co(X_{49})",
            "co(X_{50})",
            "co(X_{47})",
            "co(X_{55})",
            "co(X_{54})",
            "co(X_{56})",
            "co(X_{57})",
        ],
    )


# All recognizers for patterns on at most 13 vertices ---------------------------------------------
@assign_class_id("gc_1031")
@lru_cache(maxsize=None)
def is_gc_1031(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{4}, P_{5}, W_{5}, X_{194}, X_{86}, X_{88}, X_{89}, X_{90},
    co(C_{7}), co(X_{195}), co(X_{196}), co(X_{38}), co(X_{39}))-free.

    See https://www.graphclasses.org/classes/gc_1031

    Complexity of naïve matching: O(n^13)
    :type graph: networkx.Graph
    """
    return (
            is_k4_free(graph)
            and is_p5_free(graph)
            and is_h_free(
        graph,
        [
            "W_{5}",
            "co(X_{39})",
            "X_{88}",
            "co(X_{38})",
            "co(C_{7})",
            "X_{89}",
            "X_{86}",
            "X_{90}",
            "X_{194}",
            "co(X_{195})",
            "co(X_{196})",
        ],
    )
    )


@assign_class_id("AUTO_2292")
@lru_cache(maxsize=None)
def is_auto_2292(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (4K_{1}, C_{7}, X_{195}, X_{196}, X_{38}, X_{39}, co(W_{5}),
    co(X_{194}), co(X_{86}), co(X_{88}), co(X_{89}), co(X_{90}), house)-free.

    See https://www.graphclasses.org/classes/AUTO_2292

    Complexity of naïve matching: O(n^13)

    :type graph: networkx.Graph
    """
    return (
            is_4k1_free(graph)
            and is_house_free(graph)
            and is_h_free(
        graph,
        [
            "co(W_{5})",
            "co(X_{88})",
            "X_{39}",
            "co(X_{90})",
            "C_{7}",
            "co(X_{86})",
            "co(X_{89})",
            "X_{38}",
            "co(X_{194})",
            "X_{195}",
            "X_{196}",
        ],
    )
    )


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
