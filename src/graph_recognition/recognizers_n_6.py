"""
Anthony Labarre © 2023-2026

O(n^6) algorithms.

"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
import os
from functools import lru_cache

# ----- Third-party imports -----------------------------------------------------------------------
import networkx as nx

# ----- My imports --------------------------------------------------------------------------------
from graph_recognition.fisc_based_recognizers import (
    is_gc_373,
    is_e_free,
    is_net_free,
    is_s3_free,
    is_gc_1234,
    is_domino_free,
    is_co_e_free,
    is_co_domino_free,
    is_p5_free,
    is_house_free,
    is_gem_free,
)
from graph_recognition.misc_algo import complement_as_adj_mat
from graph_recognition.profitable_hereditary_n import (
    is_chordal,
    is_co_bipartite,
    is_bipartite,
    is_planar,
)
from graph_recognition.profitable_hereditary_n_2 import (
    is_co_chordal,
    is_co_gem_free,
    is_c_n_plus_4_u_k_1_free,
)
from graph_recognition.profitable_hereditary_n_4 import (
    is_co_claw_free,
    is_claw_free,
    is_hole_free,
    is_anti_hole_free,
)
from graph_recognition.recognizers_n import is_2_vertex_connected
from graph_recognition.recognizers_utils import (
    current_module_recognizers,
    assign_class_id,
    assign_inherited_fisc,
)
from graph_recognition.subgraphs import is_h_free


# Recognizers -------------------------------------------------------------------------------------
@assign_inherited_fisc()
@assign_class_id("AUTO_2595")
@lru_cache(maxsize=None)
def is_k3_union3_k1_co_cnplus4_co_dart_co_gem_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_2595

    @param graph:
    @return:
    """
    return (
            is_co_gem_free(graph)
            and is_co_chordal(graph)
            and is_h_free(graph, ["K_{3} U 3K_{1}", "co-dart"])
    )


@assign_inherited_fisc()
@assign_class_id("gc_1352")
@lru_cache(maxsize=None)
def is_cnplus4_co_k3_union3_k1_dart_gem_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return (
            is_chordal(graph)
            and is_gem_free(graph)
            and is_h_free(graph, ["co(K_{3} U 3K_{1})", "dart"])
    )


@assign_inherited_fisc()
@assign_class_id("AUTO_2763")
@lru_cache(maxsize=None)
def is_co_c4_co_c6_free_and_co_bipartite(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_co_bipartite(graph) and is_h_free(graph, ["co(C_{4})", "co(C_{6})"])


@assign_inherited_fisc()
@assign_class_id("AUTO_2785")
@lru_cache(maxsize=None)
def is_s3_co_cnplus4_net_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_co_chordal(graph) and is_gc_373(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_2765")
@lru_cache(maxsize=None)
def is_co_cnplus4_h_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_co_chordal(graph) and is_h_free(graph, ["co(H)"])


@assign_inherited_fisc()
@assign_class_id("AUTO_2773")
@lru_cache(maxsize=None)
def is_k33_k33_plus_e2_p3_cnplus4_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_co_chordal(graph) and is_h_free(graph, ["K_{3,3}", "K_{3,3}+e", "co(2P_{3})"])


@assign_inherited_fisc()
@assign_class_id("AUTO_747")
@lru_cache(maxsize=None)
def is2_k32_p3_cnplus4_k3_union_p3_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_chordal(graph) and is_h_free(graph, ["2K_{3}", "2P_{3}", "K_{3} U P_{3}"])


@assign_inherited_fisc()
@assign_class_id("AUTO_757")
@lru_cache(maxsize=None)
def is_cnplus4_h_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_chordal(graph) and is_h_free(graph, ["H"])


@assign_inherited_fisc()
@assign_class_id("gc_817")
@lru_cache(maxsize=None)
def is_e_free_and_bipartite(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_bipartite(graph) and is_e_free(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_2082")
@lru_cache(maxsize=None)
def is_co_e_free_and_co_bipartite(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_co_bipartite(graph) and is_co_e_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_1216")
@lru_cache(maxsize=None)
def is_e_free_and_planar(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_planar(graph) and is_e_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_507")
@lru_cache(maxsize=None)
def is_c4_c6_free_and_bipartite(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_bipartite(graph) and is_h_free(graph, ["C_{4}", "C_{6}"])


@assign_inherited_fisc()
@assign_class_id("AUTO_2786")
@lru_cache(maxsize=None)
def is_co_cnplus4_net_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_co_chordal(graph) and is_net_free(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_2779")
@lru_cache(maxsize=None)
def is_s3_cnplus4_co_claw_net_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return (
            is_co_chordal(graph)
            and is_co_claw_free(graph)
            and is_net_free(graph)
            and is_s3_free(graph)
    )


@assign_inherited_fisc()
@assign_class_id("AUTO_2761")
@lru_cache(maxsize=None)
def is_s3_co_cnplus4_co_claw_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_co_chordal(graph) and is_claw_free(graph) and is_s3_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_300")
@lru_cache(maxsize=None)
def is_s3_claw_net_free_and_chordal(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return (
            is_chordal(graph)
            and is_claw_free(graph)
            and is_net_free(graph)
            and is_s3_free(graph)
    )


@assign_inherited_fisc()
@assign_class_id("gc_380")
@lru_cache(maxsize=None)
def is_chordal_and_claw_net_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_chordal(graph) and is_claw_free(graph) and is_net_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_34")
@lru_cache(maxsize=None)
def is_s3_net_free_and_chordal(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_chordal(graph) and is_net_free(graph) and is_s3_free(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_726")
@lru_cache(maxsize=None)
def is_cnplus4_s3_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_chordal(graph) and is_s3_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_1235")
@lru_cache(maxsize=None)
def is_2_connected_and_p6_claw_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_2_vertex_connected(graph) and is_gc_1234(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_2131")
@lru_cache(maxsize=None)
def is_auto_2131(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return (
            is_co_chordal(graph)
            and is_h_free(graph, ["K_{3} U 2K_{1}", "co-4-fan", "co(K_{5} - e)", "H"])
            and is_net_free(graph)
    )


@assign_inherited_fisc()
@assign_class_id("gc_772")
@lru_cache(maxsize=None)
def is_gc_772(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return (
            is_chordal(graph)
            and is_h_free(graph, ["4-fan", "K_{5} - e", "co(H)", "co(K_{3} U 2K_{1})"])
            and is_s3_free(graph)
    )


@assign_inherited_fisc()
@assign_class_id("gc_1231")
@lru_cache(maxsize=None)
def is_domino_gem_hole_house_net_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return (
            is_hole_free(graph)
            and is_gem_free(graph)
            and is_house_free(graph)
            and is_domino_free(graph)
            and is_net_free(graph)
    )


@assign_inherited_fisc()
@assign_class_id("AUTO_1752")
@lru_cache(maxsize=None)
def is_p5_s3_anti_hole_co_domino_co_gem(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return (
            is_co_gem_free(graph)
            and is_anti_hole_free(graph)
            and is_p5_free(graph)
            and is_co_domino_free(graph)
            and is_h_free(graph, ["S_{3}"])
    )


@assign_inherited_fisc()
@assign_class_id("AUTO_1075")
@lru_cache(maxsize=None)
def is_p5_anti_hole_co_domino_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_anti_hole_free(graph) and is_p5_free(graph) and is_co_domino_free(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_1535")
@lru_cache(maxsize=None)
def is_p5_anti_hole_co_domino_co_gem_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return (
            is_co_gem_free(graph)
            and is_anti_hole_free(graph)
            and is_p5_free(graph)
            and is_co_domino_free(graph)
    )


@assign_inherited_fisc()
@assign_class_id("gc_351")
@lru_cache(maxsize=None)
def is_hhda_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return (
            is_hole_free(graph)
            and is_house_free(graph)
            and is_domino_free(graph)
            and is_h_free(graph, ["A"])
    )


@assign_inherited_fisc()
@assign_class_id("AUTO_1531")
@lru_cache(maxsize=None)
def is_p5_co_a_co_domino_antihole_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return (
            is_anti_hole_free(graph)
            and is_p5_free(graph)
            and is_h_free(graph, ["co(A)", "co-domino"])
    )


@assign_inherited_fisc()
@assign_class_id("gc_178")
@lru_cache(maxsize=None)
def is_hhdg_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_178

    @param graph:
    @return:
    """
    return (
            is_hole_free(graph)
            and is_gem_free(graph)
            and is_house_free(graph)
            and is_domino_free(graph)
    )


@assign_inherited_fisc()
@assign_class_id("gc_208")
@lru_cache(maxsize=None)
def is_hhd_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_208

    @param graph:
    @return:
    """
    return is_hole_free(graph) and is_house_free(graph) and is_domino_free(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_2783")
@lru_cache(maxsize=None)
def is_anti_hole_co_domino_odd_anti_cycle_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_2783

    @param graph:
    @return:
    """
    return is_co_bipartite(graph) and is_anti_hole_free(graph) and is_co_domino_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_1236")
@lru_cache(maxsize=None)
def is_proper_helly_circular_arc(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_889.html

    @param graph:
    @return:
    """
    # this algo uses https://www.graphclasses.org/classes/gc_1236.html instead
    return (
            is_c_n_plus_4_u_k_1_free(graph)
            and is_claw_free(graph)
            and is_s3_free(graph)
            and is_h_free(graph, ["W_{4}", "W_{5}", "co(C_{6})", "net"])
    )


@assign_class_id("AUTO_2442")
@lru_cache(maxsize=None)
def is_co_proper_helly_circular_arc(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_2442

    @param graph:
    @return:
    """
    return is_proper_helly_circular_arc(complement_as_adj_mat(graph))


@assign_inherited_fisc()
@assign_class_id("AUTO_731")
@lru_cache(maxsize=None)
def is_domino_hole_odd_cycle_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_731.html

    @param graph:
    @return:
    """
    return is_bipartite(graph) and is_hole_free(graph) and is_domino_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_773")
@lru_cache(maxsize=None)
def is_2_connected_and_gc_772(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_773

    @param graph:
    @return:
    """
    return is_2_vertex_connected(graph) and is_gc_772(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_2107")
@lru_cache(maxsize=None)
def is_auto_2107(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{3,3}, co(C_{n+4}))-free.

    See https://www.graphclasses.org/classes/AUTO_2107

    :type graph: networkx.Graph
    """
    return is_co_chordal(graph) and is_h_free(graph, ["K_{3,3}"])


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
