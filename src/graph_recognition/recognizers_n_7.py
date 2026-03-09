"""
Anthony Labarre © 2023-2026

O(n^7) algorithms.

"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
import os
from functools import lru_cache

# ----- Third-party imports -----------------------------------------------------------------------
import networkx as nx

from graph_recognition.fisc_based_recognizers import (
    is_gc_972,
    is_p7_free,
    is_co_p7_free,
    is_gc_1276,
    is_net_free,
    is_s3_free,
    is_k23_free,
    is_diamond_free,
)

# ----- My imports --------------------------------------------------------------------------------
from graph_recognition.misc_algo import is_h_u_2k1_free
from graph_recognition.profitable_hereditary_n import (
    is_planar,
    is_bipartite,
    is_co_bipartite,
    is_chordal,
    is_co_tree,
)
from graph_recognition.profitable_hereditary_n_2 import (
    is_co_chordal,
    is_c_n_plus_4_u_k_1_free,
    is_co_line,
)
from graph_recognition.profitable_hereditary_n_3 import is_paw_free, is_triangle_free
from graph_recognition.profitable_hereditary_n_4 import (
    is_claw_free,
    is_co_claw_free,
    is_hole_free,
)
from graph_recognition.recognizers_utils import (
    assign_class_id,
    current_module_recognizers,
    cached_function,
)
from graph_recognition.subgraphs import is_h_free

# Cache imported functions that are not already cached --------------------------------------------
__functions_to_cache = [
    nx.is_chordal,
    nx.node_connectivity,
]
for i, function in enumerate(__functions_to_cache):
    __functions_to_cache[i] = cached_function(function)


# Recognizers -------------------------------------------------------------------------------------
@assign_class_id("gc_986")
@lru_cache(maxsize=None)
def is_polyhedral(graph: nx.Graph) -> bool:
    """
    A graph is polyhedral if it is 3-vertex-connected and planar (a.k.a. Steinitz' Theorem).

    https://www.graphclasses.org/classes/gc_986

    The function relies on networkx's functions, which as of version 2.8.8 have the following
    running times:

    - is_planar: O(n+m)
    - node_connectivity: O((n-d-1+d(d-1)/2)) calls to a maximum flow algorithm, where d is the
      minimum degree. I use the default edmonds_karp method, whose complexity is O(nm^2).

    In the worst case d = O(n), so the complexity is O(n+m+n^2 (nm^2)) = O(n^3m^2) = O(n^7).

    :param graph:
    :return:
    """
    return is_planar(graph) and nx.node_connectivity(graph) == 3


@assign_class_id("gc_939")
@lru_cache(maxsize=None)
def is_claw_union_3_k1_odd_cycle_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_bipartite(graph) and is_h_free(graph, ["claw U 3K_{1}"])


@assign_class_id("gc_1306")
@lru_cache(maxsize=None)
def is_p7_free_and_bipartite(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_bipartite(graph) and is_p7_free(graph)


@assign_class_id("AUTO_3313")
@lru_cache(maxsize=None)
def is_co_p7_free_and_co_bipartite(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_co_bipartite(graph) and is_co_p7_free(graph)


@assign_class_id("gc_971")
@lru_cache(maxsize=None)
def is_balanced_and_co_line(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_971.html

    @param graph:
    @return:
    """
    # algo based on equivalence with https://www.graphclasses.org/classes/gc_973.html
    return is_co_line(graph) and is_gc_972(graph)


@assign_class_id("AUTO_2156")
@lru_cache(maxsize=None)
def is_co_claw_union_3_k1_odd_anti_cycle_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_2156

    @param graph:
    @return:
    """
    return is_co_bipartite(graph) and is_h_free(graph, ["co(claw U 3K_{1})"])


@assign_class_id("gc_1280")
@lru_cache(maxsize=None)
def is5_pan_t2_x172_free_and_planar(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_planar(graph) and is_gc_1276(graph)


@assign_class_id("gc_782")
@lru_cache(maxsize=None)
def is_chordal_and_proper_circular_arc(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_782

    @type graph: nx.Graph
    @param graph:
    @return:
    """
    return (
        is_chordal(graph)
        and is_claw_free(graph)
        and is_net_free(graph)
        and is_h_free(graph, ["S_{3} U K_{1}"])
    )


@assign_class_id("gc_577")
@lru_cache(maxsize=None)
def is_cnplus4_t2_net_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_chordal(graph) and is_net_free(graph) and is_h_free(graph, ["T_{2}"])


@assign_class_id("gc_505")
@lru_cache(maxsize=None)
def is_at2_odd_cycle_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_bipartite(graph) and is_h_free(graph, ["A", "T_{2}"])


@assign_class_id("gc_450")
@lru_cache(maxsize=None)
def is_odd_cycle_star123_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_bipartite(graph) and is_h_free(graph, ["star_{1,2,3}"])


@assign_class_id("gc_446")
@lru_cache(maxsize=None)
def is_p7_odd_cycle_star123_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return (
        is_bipartite(graph) and is_p7_free(graph) and is_h_free(graph, ["star_{1,2,3}"])
    )


@assign_class_id("gc_940")
@lru_cache(maxsize=None)
def is_x177_odd_cycle_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_bipartite(graph) and is_h_free(graph, ["X_{177}"])


@assign_class_id("AUTO_2081")
@lru_cache(maxsize=None)
def is_co_p7_co_star123_odd_anti_cycle_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return (
        is_co_bipartite(graph)
        and is_co_p7_free(graph)
        and is_h_free(graph, ["co(star_{1,2,3})"])
    )


@assign_class_id("AUTO_2084")
@lru_cache(maxsize=None)
def is_co_star123_odd_anti_cycle_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_co_bipartite(graph) and is_h_free(graph, ["co(star_{1,2,3})"])


@assign_class_id("AUTO_2095")
@lru_cache(maxsize=None)
def is_s3_co_cnplus4_co_t2_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return (
        is_co_chordal(graph) and is_s3_free(graph) and is_h_free(graph, ["co(T_{2})"])
    )


@assign_class_id("AUTO_2157")
@lru_cache(maxsize=None)
def is_co_x177_odd_anti_cycle_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_co_bipartite(graph) and is_h_free(graph, ["co(X_{177})"])


@assign_class_id("AUTO_2086")
@lru_cache(maxsize=None)
def is_co_a_co_t2_co_odd_cycle_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_co_bipartite(graph) and is_h_free(graph, ["co(A)", "co(T_{2})"])


@assign_class_id("gc_858")
@lru_cache(maxsize=None)
def is_chordal_and_circular_arc_and_claw_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_858.html

    @param graph:
    @return:
    """
    return (
        is_chordal(graph)
        and is_claw_free(graph)
        and is_h_free(
            graph, ["S_{3} U K_{1}", "co(X_{103})", "eiffeltower", "net U K_{1}"]
        )
    )


@assign_class_id("AUTO_2147")
@lru_cache(maxsize=None)
def is_auto_2147(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_2147.html

    @param graph:
    @return:
    """
    return (
        is_co_chordal(graph)
        and is_co_claw_free(graph)
        and is_h_free(
            graph,
            [
                "co(S_{3} U K_{1})",
                "X_{103}",
                "co-eiffeltower",
                "co(net U K_{1})",
            ],
        )
    )


@assign_class_id("AUTO_2132")
@lru_cache(maxsize=None)
def is_auto_2132(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return (
        is_co_chordal(graph)
        and is_net_free(graph)
        and is_h_u_2k1_free(graph, is_triangle_free)
        and is_h_free(
            graph,
            [
                "co-4-fan",
                "co(K_{5} - e)",
                "co(X_{100})",
                "co(X_{101})",
                "co(X_{102})",
                "H",
            ],
        )
    )


@assign_class_id("AUTO_2135")
@lru_cache(maxsize=None)
def is_auto_2135(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_2135

    @type graph: nx.Graph
    @param graph:
    @return:
    """
    return (
        is_co_claw_free(graph)
        and is_co_chordal(graph)
        and is_s3_free(graph)
        and is_h_free(graph, ["co(S_{3} U K_{1})"])
    )


@assign_class_id("AUTO_2136")
@lru_cache(maxsize=None)
def is_co_t2_co_cycle_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_co_tree(graph) and is_h_free(graph, ["co(T_{2})"])


@assign_class_id("gc_774")
@lru_cache(maxsize=None)
def is_gc_774(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return (
        is_chordal(graph)
        and is_s3_free(graph)
        and is_h_free(
            graph,
            [
                "4-fan",
                "K_{5} - e",
                "X_{100}",
                "X_{101}",
                "X_{102}",
                "co(H)",
                "co(K_{3} U 2K_{1})",
            ],
        )
    )


@assign_class_id("gc_859")
@lru_cache(maxsize=None)
def is_circular_arc_and_diamond_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_859.html

    @param graph:
    @return:
    """
    # this algo uses https://www.graphclasses.org/classes/gc_860.html instead
    return (
        is_c_n_plus_4_u_k_1_free(graph)
        and is_diamond_free(graph)
        and is_k23_free(graph)
        and is_h_free(
            graph,
            [
                "T_{2}",
                "co(C_{6})",
                "co(X_{103})",
                "co(X_{37})",
                "co(X_{88})",
                "co(X_{90})",
                "net U K_{1}",
                "domino",
                "eiffeltower",
                "twin-C_{5}",
            ],
        )
    )


@assign_class_id("gc_856")
@lru_cache(maxsize=None)
def is_circular_arc_and_paw_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_855.html

    @param graph:
    @return:
    """
    # this algo uses https://www.graphclasses.org/classes/gc_856.html instead
    return (
        is_c_n_plus_4_u_k_1_free(graph)
        and is_paw_free(graph)
        and is_k23_free(graph)
        and is_h_free(graph, ["T_{2}", "co(X_{90})", "domino", "twin-C_{5}"])
    )


@assign_class_id("gc_534")
@lru_cache(maxsize=None)
def is_hereditary_welsh_powell_perfect(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_hole_free(graph) and is_h_free(
        graph,
        [
            "P_{6}",
            "X_{10}",
            "X_{11}",
            "X_{12}",
            "X_{13}",
            "X_{14}",
            "X_{15}",
            "X_{5}",
            "X_{6}",
            "X_{7}",
            "X_{8}",
            "X_{9}",
            "co(C_{6})",
            "co(P_{6})",
            "antenna",
        ],
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
