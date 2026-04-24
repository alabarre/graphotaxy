"""
Anthony Labarre © 2026

This file contains recognizers with a worst-case exponential running time.

"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
import os
from functools import lru_cache

# ----- Third-party imports -----------------------------------------------------------------------
import networkx as nx

# ----- My imports --------------------------------------------------------------------------------
from graph_recognition.fisc_based_recognizers import is_bull_free, is_diamond_free, is_gc_180, is_gc_574
from graph_recognition.profitable_hereditary_n import is_planar, is_line, is_bipartite, is_cograph, is_chordal, \
    is_co_bipartite
from graph_recognition.profitable_hereditary_n_2 import is_comparability
from graph_recognition.profitable_hereditary_n_3 import is_paw_free, is_triangle_free, is_3k1_free
from graph_recognition.profitable_hereditary_n_4 import is_c4_free, is_k4_free, is_claw_free, is_hole_free, \
    is_co_claw_free
from graph_recognition.recognizers_n_4 import is_pretty
from graph_recognition.recognizers_n_5 import is_split_neighbourhood
from graph_recognition.recognizers_utils import current_module_recognizers, assign_class_id, assign_inherited_fisc
from graph_recognition.subgraphs import is_h_free


# Recognizers -------------------------------------------------------------------------------------
# ----- Subclasses of hole-free graphs ------------------------------------------------------------
# ---------- Subclasses of even-hole-free graphs --------------------------------------------------
@lru_cache(maxsize=None)
@assign_class_id("gc_547")
def is_even_hole_free(graph: nx.Graph):
    """
    Even-hole-free graphs contain no induced cycles whose number of vertices is even and >= 6.

    https://www.graphclasses.org/classes/gc_547.html

    :param graph:
    :return:
    """
    return is_hole_free(graph) or not any(
        len_c >= 6 and not len_c % 2 for len_c in map(len, nx.chordless_cycles(graph))  # noqa
    )


@lru_cache(maxsize=None)
@assign_class_id("gc_1325")
def is_gc_1325(graph: nx.Graph):
    """

    https://www.graphclasses.org/classes/gc_1325.html

    :param graph:
    :return:
    """
    return is_bipartite(graph) and is_h_free(graph, [
        "T_{2}", "X_{205}", "X_{206}", "X_{207}", "X_{208}"
    ]) and is_even_hole_free(graph)


# ---------- Subclasses of odd-hole-free graphs --------------------------------------------------
@lru_cache(maxsize=None)
@assign_class_id("gc_356")
def is_odd_hole_free(graph: nx.Graph):
    """
    Odd-hole-free graphs contain no induced cycles whose number of vertices is odd and >= 5.

    https://www.graphclasses.org/classes/gc_356.html

    :param graph:
    :return:
    """
    return is_hole_free(graph) or not any(
        len_c >= 5 and len_c % 2 for len_c in map(len, nx.chordless_cycles(graph))  # noqa
    )


@lru_cache(maxsize=None)
@assign_class_id("gc_610")
def is_odd_hole_free_and_pretty(graph: nx.Graph):
    """

    https://www.graphclasses.org/classes/gc_610.html

    :param graph:
    :return:
    """
    return is_pretty(graph) and is_odd_hole_free(graph)


@lru_cache(maxsize=None)
@assign_class_id("gc_711")
def is_gc_711(graph: nx.Graph):
    """

    https://www.graphclasses.org/classes/gc_711

    :param graph:
    :return:
    """
    return is_gc_180(graph) and is_odd_hole_free(graph)


@lru_cache(maxsize=None)
@assign_class_id("gc_965")
def is_co3k2_paw_odd_hole_free(graph: nx.Graph):
    """

    https://www.graphclasses.org/classes/gc_965

    :param graph:
    :return:
    """
    return is_paw_free(graph) and is_h_free(graph, ["co(3K_{2})"]) and is_odd_hole_free(graph)


@lru_cache(maxsize=None)
@assign_class_id("gc_1258")
def is_coc7_paw_odd_hole_free(graph: nx.Graph):
    """

    https://www.graphclasses.org/classes/gc_1258

    :param graph:
    :return:
    """
    return is_h_free(graph, ["co(C_{7})"]) and is_odd_hole_free(graph)


@lru_cache(maxsize=None)
@assign_class_id("gc_575")
def is_bull_house_odd_hole_free(graph: nx.Graph):
    """

    https://www.graphclasses.org/classes/gc_575

    :param graph:
    :return:
    """
    return is_gc_574(graph) and is_odd_hole_free(graph)


@lru_cache(maxsize=None)
@assign_class_id("AUTO_750")
def is_claw_odd_hole_free(graph: nx.Graph):
    """

    https://www.graphclasses.org/classes/AUTO_750

    :param graph:
    :return:
    """
    return is_claw_free(graph) and is_odd_hole_free(graph)


@lru_cache(maxsize=None)
@assign_class_id("AUTO_2772")
def is_co_claw_odd_hole_free(graph: nx.Graph):
    """

    https://www.graphclasses.org/classes/AUTO_2772

    :param graph:
    :return:
    """
    return is_co_claw_free(graph) and is_odd_hole_free(graph)


# ----- Subclasses of perfect graphs --------------------------------------------------------------
@lru_cache(maxsize=None)
@assign_class_id("gc_56")
def is_perfect(graph: nx.Graph) -> bool:
    """
    A graph is perfect if for all induced subgraphs H: chi(H) = omega(H), where chi is the
    chromatic number and omega is the size of a maximum clique.

    https://www.graphclasses.org/classes/gc_56.html

    :param graph:
    :return:
    """
    # Strong Perfect Graph Theorem (SPGT): https://en.wikipedia.org/wiki/Strong_perfect_graph_theorem
    # G is perfect iff it has no odd hole (an odd-length induced cycles of length at least 5) and
    # no odd anti-hole (complement of an odd hole).

    # this is exactly the characterization used in nx.is_perfect_graph(), which leads to an
    # exponential running time. Therefore, before we consider running it, we will look for
    # sufficient and necessary conditions for a graph to be perfect that can be checked quickly

    # note that a polynomial-time recognition exists, at least in theory; I haven't come across
    # an implementation yet. See https://www.graphclasses.org/classes/gc_56 for more details

    # 1) known subclasses of perfect graphs

    # the following families are included in the class of perfect graphs and membership is much
    # cheaper to check; ordered by increasing complexity
    profitable_recognizers_for_subclasses = (
        is_bipartite, is_cograph, is_chordal, is_co_bipartite, is_comparability
    )
    if any(recognizer(graph) for recognizer in profitable_recognizers_for_subclasses):
        return True

    # 2) contradictions for SPGT

    # none of the above worked, let's test sufficient conditions to conclude that the graph is NOT
    # perfect. I'm repeating some of the tests I've done above to avoid regressions later should we
    # modify what we did before; since all results are cached, calling a recognizer multiple times
    # is cheap
    if not is_bipartite(graph) and is_triangle_free(graph):
        # then graph contains an odd cycle of length >= 5, which contradicts perfectness
        return False

    # same condition as above but on the complement:
    if not is_co_bipartite(graph) and is_3k1_free(graph):
        # then complement contains an odd cycle of length >= 5, which contradicts perfectness
        return False

    # 3) no way around it: run the exponential algorithm and hope that it finishes "quickly"
    return nx.is_perfect_graph(graph)  # noqa (pycharm can't find is_perfect_graph)


# The following recognizers all run in exponential time, because they call is_perfect. There may
# very well exist much more efficient recognition algorithms.
@assign_inherited_fisc()
@lru_cache(maxsize=None)
@assign_class_id("gc_283")
def is_perfect_and_planar(graph: nx.Graph) -> bool:
    """
    https://www.graphclasses.org/classes/gc_283.html

    :param graph:
    :return:
    """
    return is_planar(graph) and is_perfect(graph)


@lru_cache(maxsize=None)
@assign_class_id("gc_626")
def is_perfect_and_split_neighbourhood(graph: nx.Graph) -> bool:
    """
    https://www.graphclasses.org/classes/gc_626.html

    :param graph:
    :return:
    """
    return is_split_neighbourhood(graph) and is_perfect(graph)


@assign_inherited_fisc()
@lru_cache(maxsize=None)
@assign_class_id("gc_1250")
def is_c4_free_and_perfect(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_1250.html

    :param graph:
    :return:
    """
    return is_c4_free(graph) and is_perfect(graph)


@assign_inherited_fisc()
@lru_cache(maxsize=None)
@assign_class_id("gc_598")
def is_k4_free_and_perfect(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_598.html

    :param graph:
    :return:
    """
    return is_k4_free(graph) and is_perfect(graph)


@assign_inherited_fisc()
@lru_cache(maxsize=None)
@assign_class_id("gc_64")
def is_bull_free_and_perfect(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_64.html

    :param graph:
    :return:
    """
    return is_bull_free(graph) and is_perfect(graph)


@assign_inherited_fisc()
@lru_cache(maxsize=None)
@assign_class_id("gc_139")
def is_claw_free_and_perfect(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_139.html

    :param graph:
    :return:
    """
    return is_claw_free(graph) and is_perfect(graph)


@assign_inherited_fisc()
@lru_cache(maxsize=None)
@assign_class_id("gc_603")
def is_diamond_free_and_perfect(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_603.html

    :param graph:
    :return:
    """
    return is_diamond_free(graph) and is_perfect(graph)


@assign_inherited_fisc()
@lru_cache(maxsize=None)
@assign_class_id("gc_253")
def is_line_and_perfect(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_253.html

    :param graph:
    :return:
    """
    return is_line(graph) and is_perfect(graph)


@assign_inherited_fisc()
@lru_cache(maxsize=None)
@assign_class_id("gc_1358")
def is_line_and_perfect(graph: nx.Graph) -> bool:
    """
    A graph is line perfect if its line graph is perfect graph.

    https://www.graphclasses.org/classes/gc_1358.html

    :param graph:
    :return:
    """
    return is_perfect(nx.line_graph(graph))


@assign_inherited_fisc()
@lru_cache(maxsize=None)
@assign_class_id("gc_278")
def is_paw_free_and_perfect(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_278.html

    :param graph:
    :return:
    """
    return is_paw_free(graph) and is_perfect(graph)


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
