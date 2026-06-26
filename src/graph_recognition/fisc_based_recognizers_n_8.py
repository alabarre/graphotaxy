"""Anthony Labarre © 2023-2026

This file contains all naïve recognizers with complexity O(n^8) for those graph classes in ISGCI
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
from graph_recognition.fisc_based_recognizers_n_5 import is_p5_free, is_k23_free, is_k14_free, is_c5_free
from graph_recognition.fisc_based_recognizers_n_6 import is_p6_free, is_e_free
from graph_recognition.fisc_based_recognizers_n_7 import is_p7_free, is_co_p7_free
from graph_recognition.misc_algo import (
    is_h_u_k1_free,
    is_h_u_2k1_free,
    is_odd_clique_free,
    is_odd_co_clique_free,
    is_h_u_k2_free, )
from graph_recognition.profitable_hereditary_n import (
    is_cograph,
    is_split,
    is_p3_free,
    is_2k2_free, is_chordal, is_bipartite, is_co_bipartite, is_maximum_degree_4,
    is_planar_and_maximum_degree_3, is_co_maximum_degree_4,
)
from graph_recognition.profitable_hereditary_n_2 import (
    is_co_gem_free, is_co_chordal,
)
from graph_recognition.profitable_hereditary_n_3 import (
    is_3k1_free,
    is_triangle_free,
    is_girth_at_least_9,
    is_p2up4_free,
    is_co_p3_free, is_claw_diamond_free,
)
from graph_recognition.profitable_hereditary_n_4 import (
    is_co_diamond_free,
)
from graph_recognition.fisc_based_recognizers_n_4 import is_c4_free, is_co_claw_free, is_claw_free
from graph_recognition.recognizers_utils import (
    assign_class_id,
    current_module_recognizers,
    assign_inherited_fisc,
)
from graph_recognition.subgraphs import is_h_free


# Recognizers -------------------------------------------------------------------------------------

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


@assign_inherited_fisc()
@assign_class_id("gc_445")
@lru_cache(maxsize=None)
def is_p7_odd_cycle_star123_sunlet4_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return (
            is_bipartite(graph)
            and is_p7_free(graph)
            and is_h_free(graph, ["star_{1,2,3}", "sunlet_{4}"])
    )


@assign_inherited_fisc()
@assign_class_id("AUTO_2080")
@lru_cache(maxsize=None)
def is_co_p7_co_star123_co_sunlet4_odd_anti_cycle_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return (
            is_co_bipartite(graph)
            and is_co_p7_free(graph)
            and is_h_free(graph, ["co(star_{1,2,3})", "co(sunlet_{4})"])
    )


@assign_inherited_fisc()
@assign_class_id("gc_528")
@lru_cache(maxsize=None)
def is_c4_c5_c6_c7_c8_xc11_claw_diamond_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return (
            is_maximum_degree_4(graph)
            and is_claw_diamond_free(graph)
            and is_c4_c5_c6_c7_c8_free(graph)
    )


@assign_inherited_fisc()
@assign_class_id("AUTO_1739")
@lru_cache(maxsize=None)
def is_c4_c6_c8_k1_4_free_and_bipartite(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_bipartite(graph) and is_h_free(
        graph, ["C_{4}", "C_{6}", "C_{8}", "K_{1,4}"]
    )


@assign_inherited_fisc()
@assign_class_id("gc_1282")
@lru_cache(maxsize=None)
def is_c4_c5_c6_c7_c8_free_and_maximum_degree3_and_planar(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_planar_and_maximum_degree_3(graph) and is_c4_c5_c6_c7_c8_free(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_2471")
@lru_cache(maxsize=None)
def is_auto_2471(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return (
            is_co_maximum_degree_4(graph)
            and is_co_diamond_free(graph)
            and is_co_claw_free(graph)
            and is_h_free(
        graph,
        [
            "co(C_{4})",
            "co(C_{5})",
            "co(C_{6})",
            "co(C_{7})",
            "co(C_{8})",
        ],
    )
    )


@assign_inherited_fisc()
@assign_class_id("AUTO_3653")
@lru_cache(maxsize=None)
def is_co_c4_c6_c8_k1_4_free_and_bipartite(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_co_bipartite(graph) and is_h_free(
        graph, ["co(C_{4})", "co(C_{6})", "co(C_{8})", "co(K_{1,4})"]
    )


@assign_inherited_fisc()
@assign_class_id("AUTO_2083")
@lru_cache(maxsize=None)
def is_co_star123_co_sunlet4_odd_anti_cycle_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_co_bipartite(graph) and is_h_free(graph, ["co(star_{1,2,3})", "co(sunlet_{4})"])


@assign_inherited_fisc()
@assign_class_id("gc_1240")
@lru_cache(maxsize=None)
def is_gc_1240(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_chordal(graph) and is_h_free(
        graph, ["co(P_{3} U 2K_{1})", "X_{102}", "X_{204}", "gem"]
    )


@assign_inherited_fisc()
@assign_class_id("gc_449")
@lru_cache(maxsize=None)
def is_odd_cycle_star123_sunlet4_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_bipartite(graph) and is_h_free(graph, ["star_{1,2,3}", "sunlet_{4}"])


@assign_inherited_fisc()
@assign_class_id("gc_827")
@lru_cache(maxsize=None)
def is_probe_bipartite_chain(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_bipartite(graph) and is_h_free(
        graph, ["3K_{2}", "C_{6}", "P_{7}", "X_{164}", "X_{165}", "sunlet_{4}"]
    )


@assign_inherited_fisc()
@assign_class_id("AUTO_2459")
@lru_cache(maxsize=None)
def is_auto_2459(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return (
            is_co_gem_free(graph)
            and is_co_chordal(graph)
            and is_h_u_2k1_free(graph, is_p3_free)
            and is_h_free(graph, ["co(X_{102})", "co(X_{204})"])
    )


@assign_inherited_fisc()
@assign_class_id("AUTO_2144")
@lru_cache(maxsize=None)
def is_co_probe_bipartite_chain(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_co_bipartite(graph) and is_h_free(
        graph,
        [
            "co(3K_{2})",
            "co(C_{6})",
            "co(P_{7})",
            "co(X_{164})",
            "co(X_{165})",
            "co(sunlet_{4})",
        ],
    )


@assign_inherited_fisc()
@assign_class_id("gc_447")
@lru_cache(maxsize=None)
def is_bipartite_and_bithreshold(graph: nx.Graph) -> bool:
    """

    NOTE: using FISC here : https://www.graphclasses.org/classes/gc_539.html

    :param graph:
    :return:
    """
    return (
            is_bipartite(graph)
            and is_e_free(graph)
            and is_p6_free(graph)
            and is_h_u_k2_free(graph, is_cograph)
            and is_h_free(
        graph,
        [
            "2C_{4}",
            "3K_{2}",
            "C_{6}",
            "X_{25}",
            "X_{26}",
            "X_{27}",
            "X_{28}",
            "X_{29}",
        ],
    )
    )


@assign_inherited_fisc()
@assign_class_id("AUTO_2091")
@lru_cache(maxsize=None)
def is_auto_2091(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_co_bipartite(graph) and is_h_free(
        graph,
        [
            "co(2C_{4})",
            "co(3K_{2})",
            "co(C_{6})",
            "co(E)",
            "co(P_{2} U P_{4})",
            "co(P_{6})",
            "co(X_{25})",
            "co(X_{26})",
            "co(X_{27})",
            "co(X_{28})",
            "co(X_{29})",
        ],
    )


@assign_inherited_fisc()
@assign_class_id("gc_1291")
@lru_cache(maxsize=None)
def is_line_and_mock_threshold(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_1291.html

    @param graph:
    @return:
    """
    # the straightforward option:
    #
    # return is_line(graph) and is_mock_threshold(graph)
    #
    # takes too long because of is_mock_threshold. Instead, we use the FISC
    # from https://doi.org/10.1016/j.disc.2018.04.023 :
    # G contains no cycle of length at least 5 and none of the twelve graphs
    # shown in Fig. 4.
    return (
            nx.girth(graph) < 5
            and is_k23_free(graph)
            and is_h_free(
        graph,
        [
            "2K_{1,3}",
            "claw U triangle",
            "2K_{3}",
            "K_{3} U C_{4}",
            "K_{1,3} U C_{4}",
            "fish",
            "2C_{4}",
            "X_{27}",
            "X_{84}",
            "X_{85}",
            "friendship_{3}",
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
