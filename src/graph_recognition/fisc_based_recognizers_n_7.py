"""Anthony Labarre © 2023-2026

This file contains all naïve recognizers with complexity O(n^7) for those graph classes in ISGCI
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

# ----- Third-party imports -----------------------------------------------------------------------
import networkx as nx

# ----- My imports --------------------------------------------------------------------------------
from graph_recognition.fisc_based_recognizers_n_5 import is_p5_free, is_k23_free, is_k14_free, is_gc_268, \
    is_k_clique_free, is_k2_u_k3_free
from graph_recognition.fisc_based_recognizers_n_6 import is_p6_free
from graph_recognition.profitable_hereditary_n import (
    is_cograph,
    is_split,
    is_2k2_free, )
from graph_recognition.profitable_hereditary_n_2 import (
    is_co_gem_free, )
from graph_recognition.profitable_hereditary_n_3 import (
    is_3k1_free,
    is_triangle_free,
    is_p2up4_free,
)
from graph_recognition.profitable_hereditary_n_4 import (
    is_k4_free,
    is_anti_hole_free,
    is_hole_free, is_co_diamond_free,
)
from graph_recognition.fisc_based_recognizers_n_4 import is_c4_free, is_4k1_free
from graph_recognition.recognizers_utils import (
    assign_class_id,
    current_module_recognizers,
    assign_fisc, )
from graph_recognition.subgraphs import is_h_free


# Recognizers -------------------------------------------------------------------------------------

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
