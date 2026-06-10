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
from pysat.solvers import Cadical153

# ----- My imports --------------------------------------------------------------------------------
from graph_recognition.fisc_based_recognizers import is_bull_free, is_diamond_free, is_gc_180, is_gc_574, is_net_free, \
    is_e_free, is_p5_bull_free, is_p6_free
from graph_recognition.misc_algo import complement, degeneracy
from graph_recognition.profitable_hereditary_n import is_planar, is_line, is_bipartite, is_cograph, is_chordal, \
    is_co_bipartite, is_2k2_free
from graph_recognition.profitable_hereditary_n_2 import is_comparability, is_co_paw_free, \
    is_co_gem_free
from graph_recognition.profitable_hereditary_n_3 import is_paw_free, is_triangle_free, is_3k1_free, is_p2up4_free
from graph_recognition.profitable_hereditary_n_4 import is_c4_free, is_k4_free, is_claw_free, is_hole_free, \
    is_co_claw_free, is_4k1_free, is_anti_hole_free, is_co_diamond_free
from graph_recognition.recognizers_n_4 import is_pretty
from graph_recognition.recognizers_n_5 import is_split_neighbourhood
from graph_recognition.recognizers_utils import current_module_recognizers, assign_class_id, assign_inherited_fisc, \
    assign_fisc
from graph_recognition.subgraphs import is_h_free


# Recognizers -------------------------------------------------------------------------------------
# ----- Subclasses of hole-free graphs ------------------------------------------------------------
# ---------- Subclasses of even-hole-free graphs --------------------------------------------------
@assign_fisc(["C_{6}", "C_{8}"])
@lru_cache(maxsize=None)
@assign_class_id("gc_547")
def is_even_hole_free(graph: nx.Graph) -> bool:
    """
    Even-hole-free graphs contain no induced cycles whose number of vertices is even and >= 6.

    https://www.graphclasses.org/classes/gc_547.html

    :param graph:
    :return:
    """
    return is_hole_free(graph) or not any(
        len_c >= 6 and not len_c % 2 for len_c in map(len, nx.chordless_cycles(graph))  # noqa
    )


@assign_inherited_fisc()
@lru_cache(maxsize=None)
@assign_class_id("gc_1325")
def is_gc_1325(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_1325.html

    :param graph:
    :return:
    """
    return is_bipartite(graph) and is_h_free(graph, [
        "T_{2}", "X_{205}", "X_{206}", "X_{207}", "X_{208}"
    ]) and is_even_hole_free(graph)


# ---------- Subclasses of odd-hole-free graphs --------------------------------------------------
@assign_fisc(["C_{5}", "C_{7}"])
@lru_cache(maxsize=None)
@assign_class_id("gc_356")
def is_odd_hole_free(graph: nx.Graph) -> bool:
    """
    Odd-hole-free graphs contain no induced cycles whose number of vertices is odd and >= 5.

    https://www.graphclasses.org/classes/gc_356.html

    :param graph:
    :return:
    """
    # if graph has no odd cycles, then it has no odd holes
    if is_bipartite(graph):
        return True

    # if graph has odd cycles but no triangles, then it has an odd hole
    elif is_triangle_free(graph):
        return False

    # try detecting holes first in the hope that we don't need to run the exponential time
    # algorithm
    return is_hole_free(graph) or not any(
        len_c >= 5 and len_c % 2 for len_c in map(len, nx.chordless_cycles(graph))  # noqa
    )


@assign_inherited_fisc()
@assign_class_id("gc_938")
@lru_cache(maxsize=None)
def is_gc_938(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_h_free(
        graph, [
            "K_{4}", "S_{3}", "X_{36}", "co(C_{7})", "co(X_{175})", "co(X_{176})", "co(X_{42})",
            "antenna", "co-claw", "net"
        ]
    ) and is_odd_hole_free(graph)


@lru_cache(maxsize=None)
@assign_class_id("gc_843")
def is_anti_hole_bull_odd_hole_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_843.html

    :param graph:
    :return:
    """
    return is_anti_hole_free(graph) and is_bull_free(graph) and is_odd_hole_free(graph)


@lru_cache(maxsize=None)
@assign_class_id("gc_968")
def is_s3_co_3k2_co_e_odd_hole_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_968.html

    :param graph:
    :return:
    """
    return is_h_free(graph, ["S_{3}", "co(3K_{2})", "co(E)"]) and is_odd_hole_free(graph)


@lru_cache(maxsize=None)
@assign_class_id("AUTO_766")
def is_auto_766(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_766

    :param graph:
    :return:
    """
    return is_s3_co_3k2_co_e_odd_hole_free(graph) and is_h_free(graph, ["co(P_{2} U P_{4})"]) and is_odd_anti_hole_free(
        graph)


@lru_cache(maxsize=None)
@assign_class_id("AUTO_1489")
def is_p5_bull_odd_anti_hole_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_1489.html

    :param graph:
    :return:
    """
    return is_p5_bull_free(graph) and is_odd_anti_hole_free(graph)


@assign_fisc(["C_{5}", "C_{7}"])
@lru_cache(maxsize=None)
@assign_class_id("gc_610")
def is_odd_hole_free_and_pretty(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_610.html

    :param graph:
    :return:
    """
    return is_pretty(graph) and is_odd_hole_free(graph)


@assign_inherited_fisc()
@lru_cache(maxsize=None)
@assign_class_id("gc_711")
def is_gc_711(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_711

    :param graph:
    :return:
    """
    return is_gc_180(graph) and is_odd_hole_free(graph)


@assign_inherited_fisc()
@lru_cache(maxsize=None)
@assign_class_id("gc_965")
def is_co3k2_paw_odd_hole_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_965

    :param graph:
    :return:
    """
    return is_paw_free(graph) and is_h_free(graph, ["co(3K_{2})"]) and is_odd_hole_free(graph)


@assign_fisc(["C_{5}", "C_{7}", "co(C_{7})"])
@lru_cache(maxsize=None)
@assign_class_id("gc_1258")
def is_coc7_paw_odd_hole_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_1258

    :param graph:
    :return:
    """
    return is_h_free(graph, ["co(C_{7})"]) and is_odd_hole_free(graph)


@assign_inherited_fisc()
@lru_cache(maxsize=None)
@assign_class_id("gc_575")
def is_bull_house_odd_hole_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_575

    :param graph:
    :return:
    """
    return is_gc_574(graph) and is_odd_hole_free(graph)


@assign_inherited_fisc()
@lru_cache(maxsize=None)
@assign_class_id("AUTO_750")
def is_claw_odd_hole_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_750

    :param graph:
    :return:
    """
    return is_claw_free(graph) and is_odd_hole_free(graph)


@assign_inherited_fisc()
@lru_cache(maxsize=None)
@assign_class_id("AUTO_2772")
def is_co_claw_odd_hole_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_2772

    :param graph:
    :return:
    """
    return is_co_claw_free(graph) and is_odd_hole_free(graph)


# ----- Subclasses of anti-hole-free graphs -------------------------------------------------------
@assign_fisc(["co(C_{5})", "co(C_{7})"])
@lru_cache(maxsize=None)
@assign_class_id("gc_623")
def is_odd_anti_hole_free(graph: nx.Graph) -> bool:
    """
    Odd anti-hole-free graphs are graphs whose complement contains no induced cycles whose number
    of vertices is odd and >= 5.

    https://www.graphclasses.org/classes/gc_623.html

    :param graph:
    :return:
    """
    # if graph has no odd anti-cycle, then it has no odd anti-hole
    if is_co_bipartite(graph):
        return True
    # if graph odd anti-cycles but no co(K_{3}), then it has an odd anti-hole
    elif is_3k1_free(graph):
        return False

    # note: complement_as_adj_mat not usable because of missing attribute graph.adj
    return is_odd_hole_free(complement(graph))


@lru_cache(maxsize=None)
@assign_class_id("gc_977")
def is_anti_hole_odd_hole_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_977


    :param graph:
    :return:
    """
    return is_anti_hole_free(graph) and is_odd_hole_free(graph)


@lru_cache(maxsize=None)
@assign_class_id("gc_976")
def is_hole_odd_anti_hole_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_976

    :param graph:
    :return:
    """
    return is_hole_free(graph) and is_odd_anti_hole_free(graph)


@lru_cache(maxsize=None)
@assign_class_id("AUTO_1457")
def is_bull_hole_odd_anti_hole_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_1457

    :param graph:
    :return:
    """
    return is_bull_free(graph) and is_hole_odd_anti_hole_free(graph)


@assign_inherited_fisc()
@lru_cache(maxsize=None)
@assign_class_id("AUTO_1611")
def is_2k2_odd_anti_hole_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_1611.html

    :param graph:
    :return:
    """
    return is_2k2_free(graph) and is_odd_anti_hole_free(graph)


@assign_inherited_fisc()
@lru_cache(maxsize=None)
@assign_class_id("AUTO_1561")
def is_3k2_e_net_odd_anti_hole_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_1561.html


    :param graph:
    :return:
    """
    return is_h_free(graph, ["3K_{2}"]) and is_e_free(graph) and is_net_free(graph) and is_odd_anti_hole_free(graph)


@assign_inherited_fisc()
@lru_cache(maxsize=None)
@assign_class_id("AUTO_2770")
def is_co_diamond_odd_anti_hole_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_2770.html

    :param graph:
    :return:
    """
    return is_co_diamond_free(graph) and is_odd_anti_hole_free(graph)


@assign_inherited_fisc()
@lru_cache(maxsize=None)
@assign_class_id("AUTO_2771")
def is_co_claw_odd_anti_hole_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_2771.html

    :param graph:
    :return:
    """
    return is_co_claw_free(graph) and is_odd_anti_hole_free(graph)


@assign_inherited_fisc()
@lru_cache(maxsize=None)
@assign_class_id("AUTO_2781")
def is_co_claw_odd_anti_hole_odd_hole_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_2781.html

    :param graph:
    :return:
    """
    return is_co_claw_odd_anti_hole_free(graph) and is_odd_hole_free(graph)


@assign_inherited_fisc()
@lru_cache(maxsize=None)
@assign_class_id("AUTO_2769")
def is_4k1_odd_anti_hole_odd_hole_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_2769.html

    :param graph:
    :return:
    """
    return is_4k1_free(graph) and is_odd_hole_free(graph) and is_odd_anti_hole_free(graph)


@lru_cache(maxsize=None)
@assign_class_id("gc_630")
def is_even_anti_hole_free(graph: nx.Graph):
    """
    Even anti-hole-free graphs are graphs whose complement contains no induced cycles whose number
    of vertices is odd and >= 6.

    https://www.graphclasses.org/classes/gc_630.html

    :param graph:
    :return:
    """
    # note: complement_as_adj_mat not usable because of missing attribute graph.adj
    return is_even_hole_free(complement(graph))


@lru_cache(maxsize=None)
@assign_class_id("AUTO_2581")
def is_auto_2581(graph: nx.Graph):
    """

    https://www.graphclasses.org/classes/AUTO_2581

    :param graph:
    :return:
    """
    return is_co_bipartite(graph) and is_h_free(
        graph, ["co(T_{2})", "co(X_{205})", "co(X_{206})", "co(X_{207})", "co(X_{208})"]
    ) and is_even_anti_hole_free(graph)


@assign_inherited_fisc()
@lru_cache(maxsize=None)
@assign_class_id("AUTO_2839")
def is_3k2_e_p2up4_net_odd_anti_hole_odd_hole_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_2839


    :param graph:
    :return:
    """
    return is_p2up4_free(graph) and is_3k2_e_net_odd_anti_hole_free(graph) and is_odd_hole_free(graph)


@assign_inherited_fisc()
@lru_cache(maxsize=None)
@assign_class_id("gc_969")
def is_gc_969(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_969


    :param graph:
    :return:
    """
    return is_line(graph) and is_s3_co_3k2_co_e_odd_hole_free(graph)


@lru_cache(maxsize=None)
@assign_class_id("AUTO_1562")
def is_3k2_co_paw_odd_anti_hole_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_1562


    :param graph:
    :return:
    """
    return is_co_paw_free(graph) and is_h_free(graph, ["3K_{2}"]) and is_odd_anti_hole_free(graph)


@lru_cache(maxsize=None)
@assign_class_id("AUTO_1789")
def is_c7_odd_anti_hole_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_1789


    :param graph:
    :return:
    """
    return is_h_free(graph, ["C_{7}"]) and is_odd_anti_hole_free(graph)


@lru_cache(maxsize=None)
@assign_class_id("AUTO_748")
def is_claw_odd_anti_hole_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_748


    :param graph:
    :return:
    """
    return is_claw_free(graph) and is_odd_anti_hole_free(graph)


@assign_fisc(["4K_{1}", "C_{7}", "S_{3}", "X_{175}", "X_{176}", "X_{42}", "X_{36}", "claw", "co-antenna", "net"])
@lru_cache(maxsize=None)
@assign_class_id("AUTO_2155")
def is_auto_2155(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_2155

    :param graph:
    :return:
    """
    return is_h_free(
        graph,
        ["4K_{1}", "C_{7}", "S_{3}", "X_{175}", "X_{176}", "X_{42}", "X_{36}", "claw", "co-antenna", "net"]
    ) and is_odd_anti_hole_free(graph)


@assign_inherited_fisc()
@lru_cache(maxsize=None)
@assign_class_id("AUTO_2119")
def is_auto_2119(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_2119


    :param graph:
    :return:
    """
    return is_co_gem_free(graph) and is_co_claw_free(graph) and is_h_free(
        graph, ["co(W_{4})"]
    ) and is_odd_anti_hole_free(graph)


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

    # the following families are included in the class of perfect graphs and membership is much
    # cheaper to check; ordered by increasing complexity
    profitable_recognizers_for_subclasses = (
        is_bipartite, is_cograph, is_chordal, is_co_bipartite, is_comparability
    )
    if any(recognizer(graph) for recognizer in profitable_recognizers_for_subclasses):
        return True

    # if there's no way around it: run the exponential algorithm and hope that it finishes
    # "quickly"
    # this is exactly what nx.is_perfect_graph does, but we call our versions instead because they
    # are cached and feature additional tricks to short-circuit the actual search for (anti-)holes
    return is_odd_hole_free(graph) and is_odd_anti_hole_free(graph)


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


@lru_cache(maxsize=None)
@assign_class_id("gc_1358")
def is_line_perfect(graph: nx.Graph) -> bool:
    """
    A graph is line perfect if its line graph is a perfect graph.

    https://www.graphclasses.org/classes/gc_1358.html

    :param graph:
    :return:
    """
    # see https://link.springer.com/article/10.1007/BF01593791: a graph is line perfect iff it has
    # no odd cycle of size > 3, so this class actually equivalent to odd-hole-free
    return is_odd_hole_free(graph)


# ----- Subclasses of even-cycle-free graphs ------------------------------------------------------
# Note: this is more restricted than even-hole-free graphs: an even hole has length >= 6, but an
# even cycle has length >= 4.
@assign_inherited_fisc()
@lru_cache(maxsize=None)
@assign_class_id("gc_706")
def is_even_cycle_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_706.html

    :param graph:
    :return:
    """
    return is_c4_free(graph) and is_even_hole_free(graph)


@assign_inherited_fisc()
@lru_cache(maxsize=None)
@assign_class_id("gc_829")
def is_diamond_even_cycle_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_829.html

    :param graph:
    :return:
    """
    return is_diamond_free(graph) and is_even_cycle_free(graph)


@assign_inherited_fisc()
@lru_cache(maxsize=None)
@assign_class_id("gc_991")
def is_x37_diamond_even_cycle_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_991.html

    :param graph:
    :return:
    """
    return is_h_free(graph, ["X_{37}"]) and is_diamond_even_cycle_free(graph)


# ----- Subclasses of even-anti-cycle-free graphs -------------------------------------------------
@lru_cache(maxsize=None)
@assign_class_id("AUTO_2118")
def is_even_anti_cycle_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_2118.html

    :param graph:
    :return:
    """
    return is_2k2_free(graph) and is_even_anti_hole_free(graph)


@lru_cache(maxsize=None)
@assign_class_id("AUTO_2206")
def is_co_diamond_even_anti_cycle_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_2206

    :param graph:
    :return:
    """
    return is_co_diamond_free(graph) and is_even_anti_cycle_free(graph)


@lru_cache(maxsize=None)
@assign_class_id("AUTO_2207")
def is_co_x_37_co_diamond_even_anti_cycle_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_2207

    :param graph:
    :return:
    """
    return is_co_diamond_free(graph) and is_h_free(graph, ["co(X_{37})"]) and is_even_anti_cycle_free(graph)


# 3-colorable classes -----------------------------------------------------------------------------
@lru_cache(maxsize=None)
@assign_class_id("gc_453")
def is_tripartite(graph: nx.Graph) -> bool:
    """
    A graph is tripartite iff it can be partitioned in 3 independent sets.

    https://www.graphclasses.org/classes/gc_453

    :param graph:
    :return:
    """

    def vertex_color(vertex: int, color: int) -> int:
        """
        Returns an id for the assignment of color to vertex.

        :param color:
        :param vertex:
        :return:
        """
        return 3 * vertex + color + 1

    # simple conditions checkable in linear-time to avoid running the SAT solver
    if not graph or is_bipartite(graph) or degeneracy(graph) <= 2:
        return True

    with Cadical153() as s:
        for v in graph:
            # vertex v receives at least one color in {0, 1, 2}
            s.add_clause([vertex_color(v, 0), vertex_color(v, 1), vertex_color(v, 2)])
            # vertex v receives at most one color in {0, 1, 2}
            s.add_clause([-vertex_color(v, 0), -vertex_color(v, 1)])
            s.add_clause([-vertex_color(v, 0), -vertex_color(v, 2)])
            s.add_clause([-vertex_color(v, 1), -vertex_color(v, 2)])

        for u, v in graph.edges:
            for c in range(3):
                # adjacent vertices u and v cannot receive the same color
                s.add_clause([-vertex_color(u, c), -vertex_color(v, c)])

        return s.solve()


@lru_cache(maxsize=None)
@assign_class_id("gc_639")
def is_p6_free_and_tripartite(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_639

    :param graph:
    :return:
    """
    return is_p6_free(graph) and is_tripartite(graph)


@lru_cache(maxsize=None)
@assign_class_id("AUTO_749")
def is_claw_odd_anti_hole_free_and_tripartite(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_749

    :param graph:
    :return:
    """
    return is_claw_odd_anti_hole_free(graph) and is_tripartite(graph)


@lru_cache(maxsize=None)
@assign_class_id("AUTO_751")
def is_claw_odd_hole_free_and_tripartite(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_751

    :param graph:
    :return:
    """
    return is_claw_odd_hole_free(graph) and is_tripartite(graph)


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
