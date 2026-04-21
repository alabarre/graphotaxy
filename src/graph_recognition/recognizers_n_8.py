"""
Anthony Labarre © 2025-2026

O(n^8) algorithms.

"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
import os
from array import array
from functools import lru_cache
from itertools import combinations

# ----- Third-party imports -----------------------------------------------------------------------
import networkx as nx

# ----- My imports --------------------------------------------------------------------------------
from graph_recognition.fisc_based_recognizers import (
    is_p7_free,
    is_co_p7_free,
    is_c4_c5_c6_c7_c8_free,
    is_e_free,
    is_p6_free, is_k23_free,
)
from graph_recognition.misc_algo import degree_sequence, is_h_u_2k1_free, is_h_u_k2_free
from graph_recognition.profitable_hereditary_n import (
    is_bipartite,
    is_co_bipartite,
    is_maximum_degree_4,
    is_planar_and_maximum_degree_3,
    is_co_maximum_degree_4,
    is_chordal,
    is_p3_free,
    is_cograph,
)
from graph_recognition.profitable_hereditary_n_2 import (
    is_co_diamond_free,
    is_co_chordal,
    is_co_gem_free,
)
from graph_recognition.profitable_hereditary_n_3 import is_claw_diamond_free
from graph_recognition.profitable_hereditary_n_4 import is_co_claw_free
from graph_recognition.recognizers_utils import (
    assign_class_id,
    current_module_recognizers, assign_inherited_fisc, assign_fisc,
)
from graph_recognition.subgraphs import is_h_free


# Recognizers -------------------------------------------------------------------------------------
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


@assign_fisc([
    "co(C_{5})",
    "co(C_{6})",
    "co(C_{7})",
    "co(C_{8})",
    "domino",
    "C_{7}",
    "C_{8}",
])  # partial fisc also used in the code of the function
@assign_class_id("gc_352")
@lru_cache(maxsize=None)
def is_wing_triangulated(graph: nx.Graph) -> bool:
    """
    For a graph G the graph W(G) having all edges of G as its vertices, two edges of G being
    adjacent in W(G) if they are the non-incident edges (called wings) of an induced path on four
    vertices in G, is called the wing-graph of G. A graph G is wing-triangulated if W(G) is
    triangulated.

    https://www.graphclasses.org/classes/gc_352

    @param graph:
    @return:
    """
    # see https://doi.org/10.1002/(SICI)1097-0118(199701)24:1%3C25::AID-JGT4%3E3.0.CO;2-L ,
    # observation 1:
    # wing-triangulated graphs are C_k free for all k >= 7; domino-free; and co(C_k)-free for all
    # k >= 5; we are only testing the smallgraphs we already have
    if not is_h_free(
            graph,
            [
                "co(C_{5})",
                "co(C_{6})",
                "co(C_{7})",
                "co(C_{8})",
                "domino",
                "C_{7}",
                "C_{8}",
            ],
    ):
        return False

    # build the wing-graph
    wing_graph = nx.Graph()
    wing_graph.add_nodes_from(graph.edges())

    # connect each pair of nodes in wing_graph that corresponds to edges in the graph that satisfy
    # both conditions; we can actually just check that they are disjoint and induce a P_4
    p4_deg_seq = array('b', [2, 2, 1, 1])
    for e, f in combinations(wing_graph, 2):
        endpoints = set(e + f)
        if len(endpoints) == 4 and degree_sequence(graph.subgraph(endpoints)) == p4_deg_seq:
            wing_graph.add_edge(e, f)

    # check wing_graph's chordality (preemptively return True for empty graphs, as nx.is_chordal
    # crashes on those)
    return not wing_graph or is_chordal(wing_graph)


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
            os.path.basename(__file__).removesuffix(".py"),
        ]
    )
)
# -------------------------------------------------------------------------------------------------
