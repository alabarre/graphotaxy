"""Anthony Labarre © 2023-2026

This file contains recognizers for profitable hereditary classes, i.e. classes that admit a
forbidden induced subgraph characterization, but can be recognized with a faster-than-naïve
algorithm.

Recognizers in this file have running time O(m+n).

"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
import os
from array import array
from collections import defaultdict
from collections.abc import Callable
from functools import lru_cache
from sys import maxsize
from typing import Any

# ----- Third-party imports -----------------------------------------------------------------------
import networkx as nx
from networkx.generators import line
from networkx.utils import arbitrary_element
from tralda.cograph import to_cotree

from graph_recognition.adjacency_matrix import HalfAdjacencyMatrix
# ----- My imports --------------------------------------------------------------------------------
from graph_recognition.misc_algo import (
    is_complete,
    degree_sequence,
    is_connected,
    is_h_u_k2_free, co_connected_components,
)
from graph_recognition.profitable_hereditary_constant import is_k2_free
from graph_recognition.recognizers_utils import (
    current_module_recognizers,
    assign_class_id,
    assign_fisc, undecorated_function,
)


# Auxiliary functions -----------------------------------------------------------------------------
@assign_fisc(["co(C_{4})", "co(C_{6})", "co(C_{7})", "co(C_{8})", "co(C_{5})", "3K_{1}"])
@lru_cache(maxsize=None)
def is_co_forest(graph: nx.Graph) -> bool:
    """
    Returns True iff the complement of the graph is a forest.

    Complexity: O(m+n).

    :type graph: nx.Graph
    :param graph:
    :return:
    """
    if len(graph) == 0:
        return False

    # check that each component of the complement is a co_tree
    return all(is_co_tree(graph.subgraph(cc)) for cc in co_connected_components(graph))


@lru_cache(maxsize=None)
def is_k_bounded_bipartite(graph: nx.Graph, k: int) -> bool:
    """
    A bipartite graph (X,Y,E) is k-bounded bipartite if every vertex in X, resp. Y, has at most k
    non-neighbors in Y, resp. X. In other words, the degree of each vertex v in X is >= |Y| - k,
    and the degree of each vertex in Y is at >= |X| - k.

    :param k:
    :param graph:
    :return:
    """
    # we have to check each component separately, because nx.bipartite.sets fails on disconnected
    # graphs
    for cc in nx.connected_components(graph):
        try:
            left, right = nx.bipartite.sets(graph.subgraph(cc))
            left_size_bound, right_size_bound = len(left) - k, len(right) - k
            if not (
                    all(graph.degree[u] >= right_size_bound for u in left)
                    and all(graph.degree[v] >= left_size_bound for v in right)
            ):
                return False

        except nx.NetworkXError:  # graph is not bipartite, quit early
            return False

    return True


@lru_cache(maxsize=None)
def is_disjoint_union_of_edgeless_graph_and_single_other(
        graph: nx.Graph, recognizer_for_other: Callable
) -> bool:
    """
    Returns True iff graph is the disjoint union of an edgeless graph and of a single graph defined
    by recognizer_for_other, False otherwise.

    :param recognizer_for_other:
    :type graph: networkx.Graph
    """
    already_found_other = False
    for cc in nx.connected_components(graph):
        if len(cc) != 1:  # skip isolated vertices
            if recognizer_for_other(graph.subgraph(cc)):
                if already_found_other:
                    return False
                already_found_other = True
            else:
                return False

    return True


# @lru_cache(maxsize=None) # don't: arrays are not hashable
def is_split_degree_sequence(degseq: array) -> bool:
    """
    Returns True iff the given degree sequence is that of a split graph, False otherwise. The
    degree sequence must be sorted decreasingly.

    See https://www.graphclasses.org/classes/gc_313

    Complexity: O(n).

    """
    # I'm using http://dx.doi.org/10.1007/BF02579333, Theorem 6
    # careful: all indices in the paper start at 1 but ours start at 0, which impacts points (1)
    # and (2) below
    # compute m = largest index k such that D[k] >= k-1
    m = 0
    for m, value in enumerate(degseq):
        if value < m + 1:  # and not m (1)
            break

    m -= 1  # decrease m's value (we stopped one step too far)

    return sum(degseq[: m + 1]) == (m + 1) * m + sum(degseq[m + 1:])  # and not m * (m-1) (2)


def my_inverse_line_graph(graph: nx.Graph) -> None:
    """
    Checks whether a connected graph is a line graph. Returns None if everything went fine, raises
    NetworkXError otherwise.

    This is essentially network's inverse_line_graph function without the part responsible for
    building the inverse line graph, since we only care about membership.
    """
    if graph.number_of_nodes() < 2:
        return

    elif graph.number_of_edges() == 0:
        msg = (
            "inverse_line_graph() doesn't work on an edgeless graph. "
            "Please use this function on each component separately."
        )
        raise nx.NetworkXError(msg)

    if nx.number_of_selfloops(graph) != 0:
        msg = (
            "A line graph as generated by NetworkX has no selfloops, so G has no "
            "inverse line graph. Please remove the selfloops from G and try again."
        )
        raise nx.NetworkXError(msg)

    starting_cell = line._select_starting_cell(graph)
    # count how many times each vertex appears in the partition set
    p_count = defaultdict(int)
    for p in line._find_partition(graph, starting_cell):
        for u in p:
            p_count[u] += 1

    if max(p_count.values()) > 2:
        msg = "G is not a line graph (vertex found in more than two partition cells)"
        raise nx.NetworkXError(msg)


# Recognizers -------------------------------------------------------------------------------------
@assign_fisc(
    ["triangle", "C_{4}", "C_{5}", "C_{6}", "C_{7}", "C_{8}"]
)  # partial fisc: graph is cycle-free
@assign_class_id("gc_342")
@lru_cache(maxsize=None)
def is_tree(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is a tree.

    See https://www.graphclasses.org/classes/gc_342

    Complexity: O(m+n).

    :type graph: networkx.Graph
    """
    # artificially deciding that a graph without any node is a tree in order to avoid crashes when
    # function is called on empty subgraphs
    return not graph.number_of_nodes() or nx.is_tree(graph)


@assign_fisc(["P_{3}"])
@assign_class_id("gc_406")
@lru_cache(maxsize=None)
def is_p3_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is P_{3}-free.

    See https://www.graphclasses.org/classes/gc_406

    Complexity: O(m+n) < O(n^3) (naïve)

    :type graph: networkx.Graph
    """
    # equivalent to https://www.graphclasses.org/classes/gc_1237.html :
    # a graph is a cluster graph iff it is a disjoint union of cliques
    return all(is_complete(graph.subgraph(cc)) for cc in nx.connected_components(graph))


@assign_fisc(["P_{3}", "3K_{1}"])
@assign_class_id("gc_1311")
@lru_cache(maxsize=None)
def is_3k1_p3_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (3K_{1}, P_{3})-free.

    See https://www.graphclasses.org/classes/gc_1311

    Complexity: O(m+n) < O(n^3) (naïve)

    :type graph: networkx.Graph
    """
    # a graph is (3K_{1}, P_{3})-free iff it is the disjoint union of two complete graphs
    is_disjoint_union_of_2_cliques = True
    for i, cc in enumerate(nx.connected_components(graph), 1):
        # too many components or found non-clique -> abort
        if i > 2 or not is_complete(graph.subgraph(cc)):
            is_disjoint_union_of_2_cliques = False
            break

    return is_disjoint_union_of_2_cliques


@assign_fisc(["3K_{1}", "co(P_{3})"])
@assign_class_id("gc_1302")
@lru_cache(maxsize=None)
def is_3k1_co_p3_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (3K_{1}, co(P_{3}))-free.

    See https://www.graphclasses.org/classes/gc_1302

    Complexity: O(m+n) < O(n^3) (naïve)

    :type graph: networkx.Graph
    """
    # True iff complement has maximum degree 1, i.e. if original graph has minimum degree n-2
    return degree_sequence(graph)[-1] >= graph.number_of_nodes() - 2


@assign_fisc(["P_{3}", "triangle"])
@assign_class_id("gc_1300")
@lru_cache(maxsize=None)
def is_p3_triangle_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{3}, triangle)-free.

    See https://www.graphclasses.org/classes/gc_1300

    Complexity: O(m+n) < O(n^3) (naïve)

    :type graph: networkx.Graph
    """
    # graph is (P_{3}, triangle)-free iff it has maximum degree 1
    ds = degree_sequence(graph)
    return not ds or ds[0] <= 1


@assign_fisc(["triangle", "co(P_{3})", "C_{4}"])
@assign_class_id("gc_1307")
@lru_cache(maxsize=None)
def is_gc_1307(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{4}, co(P_{3}), triangle)-free.

    See https://www.graphclasses.org/classes/gc_1307

    Complexity: O(m+n) < O(n^4) (naïve)

    :type graph: networkx.Graph
    """
    # a graph is (C_{4}, co(P_{3}), triangle)-free if it is either a star, or edgeless
    n = graph.number_of_nodes()
    return not graph.size() or degree_sequence(graph) == array("Q", [n - 1] + [1] * (n - 1))


@assign_fisc(["triangle", "P_{4}", "2K_{2}", "C_{4}"])
@assign_class_id("gc_1313")
@lru_cache(maxsize=None)
def is_gc_1313(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, C_{4}, P_{4}, triangle)-free.

    See https://www.graphclasses.org/classes/gc_1313

    Complexity: O(m+n) < O(n^4) (naïve)

    :type graph: networkx.Graph
    """
    # a graph is (2K_{2}, C_{4}, P_{4}, triangle)-free if it is the disjoint union of an edgeless
    # graph and a star
    return is_disjoint_union_of_edgeless_graph_and_single_other(
        graph,
        lambda subgraph: degree_sequence(subgraph)
                         == array(
            "Q",
            [subgraph.number_of_nodes() - 1] + [1] * (subgraph.number_of_nodes() - 1),
        ),
    )


@assign_fisc(["2K_{2}", "C_{4}", "C_{5}"])
@assign_class_id("gc_313")
@lru_cache(maxsize=None)
def is_split(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, C_{4}, C_{5})-free.

    See https://www.graphclasses.org/classes/gc_313

    Complexity: O(m+n) < O(n^5) (naïve)

    :type graph: networkx.Graph
    """
    return is_split_degree_sequence(degree_sequence(graph))


@assign_fisc(["P_{3}", "2K_{2}"])
@assign_class_id("gc_1312")
@lru_cache(maxsize=None)
def is_gc_1312(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, P_{3})-free.

    See https://www.graphclasses.org/classes/gc_1312

    Complexity: O(m+n) < O(n^4) (naïve)

    :type graph: networkx.Graph
    """
    # a graph is (2K_{2}, P_{3})-free if it is the disjoint union of a complete graph and an
    # edgeless graph
    return is_disjoint_union_of_edgeless_graph_and_single_other(graph, is_complete)


@assign_fisc(
    [
        "claw",
        "co(P_{2} U P_{3})",
        "K_{5} - e",
        "W_{5}",
        "co-twin-C_{5}",
        "co(R)",
        "co-twin-house",
        "co(A)",
        "co(C_{4} U 2K_{1})",
    ]
)
@assign_class_id("gc_249")
@lru_cache(maxsize=None)
def is_line(graph: nx.Graph) -> bool:
    """
    A graph G is a line graph if the edges of G can be partitioned into maximal complete subgraphs
    such that no vertex lies in more than two of the subgraphs.

    https://www.graphclasses.org/classes/gc_249.html

    Complexity: O(m+n) < O(n^6) (naïve)

    @param graph:
    @return:
    """
    for cc in nx.connected_components(graph):
        try:
            my_inverse_line_graph(graph.subgraph(cc))
        except nx.NetworkXError:
            return False

    return True


# note: the FISC is incomplete, but these are the only odd cycles that are stored as smallgraphs
@assign_fisc(["K_{3}", "C_{5}", "C_{7}"])
@assign_class_id("gc_1245")
@lru_cache(maxsize=None)
def is_complete_bipartite(graph: nx.Graph) -> bool:
    """
    A complete bipartite graph consists of non-empty independent sets U and W and (x, y) is an edge
    whenever x ∈ U and y ∈ W.

    https://www.graphclasses.org/classes/gc_1245

    Complexity: O(m+n)

    @param graph:
    @return:
    """
    # basic checks
    if not is_connected(graph) or not is_bipartite(graph):
        return False

    # check the node and edge counts in bipartite partition
    left, right = nx.bipartite.sets(graph)
    return sum(graph.degree[v] for v in left) == len(left) * len(right)


# note: the FISC below was found by minor_expander.py; it is incomplete, since planar graphs are
# characterized by forbidden induced **minors**; but this is as far as we can go since the other
# subgraphs produced by minor_expander.py are unknown to ISGCI
@assign_fisc(["K_{3,3}", "co(X_{86})", "K_{5}", "X_{46}", "co(K_{2} U claw)", "co(X_{120})"])
@assign_class_id("gc_43")
@lru_cache(maxsize=None)
def is_planar(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is planar.

    https://www.graphclasses.org/classes/gc_43

    :param graph:
    :return:
    """
    # this is merely a call to networkx's algorithm, except we avoid it if graph has too many edges
    # to be planar
    n = graph.number_of_nodes()
    m = graph.size()

    if not n or not m:
        return True

    if n >= 3 and m > 3 * n - 6 or degree_sequence(graph)[-1] > 5:
        return False

    # the first element of check_planarity's return value is the answer
    return nx.check_planarity(graph)[0]


# note: the FISC is incomplete, but these are the only odd cycles that are stored as smallgraphs
@assign_fisc(["K_{3}", "C_{5}", "C_{7}"])
@assign_class_id("gc_69")
@lru_cache(maxsize=None)
def is_bipartite(graph: nx.Graph | HalfAdjacencyMatrix) -> bool:
    """
    Returns True iff graph is bipartite. This is a mere cached call to networkx's function, except
    for a preliminary check to see if the call is actually needed.

    https://www.graphclasses.org/classes/gc_69

    @type graph: nx.Graph
    """
    # if there are too many edges, the graph cannot be bipartite
    n = graph.number_of_nodes()
    m = graph.number_of_edges()
    if m > (n ** 2) / 4:
        return False

    return nx.is_bipartite(graph)


# note: the FISC is incomplete, but these are the only C_{n+4} that are stored as smallgraphs
@assign_fisc(["diamond", "C_{4}", "C_{5}", "C_{6}", "C_{7}", "C_{8}"])
@assign_class_id("gc_93")
@lru_cache(maxsize=None)
def is_block(graph: nx.Graph) -> bool:
    """
    A graph is a block graph if every block (maximal 2-connected component) is a clique.

    https://www.graphclasses.org/classes/gc_93.html

    @type graph: nx.Graph
    @param graph:
    @return:
    """
    return all(
        bc.size() == (bc.order() * (bc.order() - 1)) // 2
        for bc in map(graph.subgraph, nx.biconnected_components(graph))
    )


@assign_fisc(
    {
        'co(C_{4})',
        'house',
        'co-paw',
        'K_{2,3}',
        '4K_{1}',
        'co-claw',
        'co-diamond',
        '2K_{2}',
        'diamond',
        'K_{4}'
    }
)  # basis of a partial fisc computed by filter.py
@assign_class_id("gc_108")
@lru_cache(maxsize=None)
def is_cactus(graph: nx.Graph) -> bool:
    """
    A graph is a cactus if every edge is part of at most one cycle.

    This is not the same as being diamond-free: the graph might contain larger cycles that share an
    edge. The partial FISC of this graph class is obtained by listing those smallgraphs that can be
    viewed as "glued cycles".

    https://www.graphclasses.org/classes/gc_108.html

    @param graph:
    @return:
    """
    # adapted from sagemath
    # Special cases
    if graph.order() < 4:
        return True

    # Every cactus graph is outerplanar
    # if not self.is_circular_planar():
    #     return False

    if not is_connected(graph):
        return False

    # every biconnected component must be a cycle or a single edge
    return all(
        degree_sequence(graph.subgraph(bc))
        in (array("b", [1, 1]), array("b", [2] * len(bc)))
        for bc in nx.biconnected_components(graph)
    )


@assign_fisc(["C_{5}", "co-butterfly", "co-diamond", "triangle"])
@assign_class_id("gc_685")
@lru_cache(maxsize=None)
def is_1_bounded_bipartite(graph: nx.Graph) -> bool:
    """
    A bipartite graph (X,Y,E) is 1-bounded bipartite if every vertex in X, resp. Y, has at most 1
    non-neighbor in Y, resp. X. In other words, the degree of each vertex v in X is at least
    |Y| - 1, and the degree of each vertex in Y is at least |X| - 1.

    https://www.graphclasses.org/classes/gc_685.html

    :param graph:
    :return:
    """
    return is_k_bounded_bipartite(graph, 1)


@assign_fisc(
    [
        "triangle",
        "C_{5}",
        "co(K_{5} - e)",
        "K_{3,3} U K_{1}",
        "C_{7}",
        "C_{6} U K_{1}",
        "K_{3,3}-e U K_{1}",
        "domino U K_{1}",
    ]
)
@assign_class_id("gc_687")
@lru_cache(maxsize=None)
def is_2_bounded_bipartite(graph: nx.Graph) -> bool:
    """
    A bipartite graph (X, Y, E) is 2-bounded bipartite if every vertex in X, resp. Y, has at most 2
    non-neighbors in Y, resp. X.

    https://www.graphclasses.org/classes/gc_687.html

    :param graph:
    :return:
    """
    return is_k_bounded_bipartite(graph, 2)


@assign_fisc(
    [
        "K_{5}",
        "K_{5} - e",
        "co(claw U K_{1})",
        "K_{1,4}",
        "co(P_{3} U 2K_{1})",
        "dart",
        "gem",
        "cricket",
        "W_{4}",
        "co(K_{3} U 2K_{1})",
        "butterfly",
    ]
)
@assign_class_id("gc_720")
@lru_cache(maxsize=None)
def is_maximum_degree_3(graph: nx.Graph) -> bool:
    """
    A graph is of maximum degree 3 if it is XC_{12}-free. The corresponding FISC was found by my
    xc_unpacker program.

    https://www.graphclasses.org/classes/gc_720.html

    @param graph:
    @return:
    """
    return degree_sequence(graph)[0] <= 3


@assign_fisc(
    [
        "4-fan",
        "co(co-fork U K_{1})",
        "W_{5}",
        "co(butterfly U K_{1})",
        "co(K_{3} U 3K_{1})",
        "co(W_{4} U K_{1})",
        "co(X_{198})",
        "K_{1,5}",
        "K_{6}",
        "co(X_{197})",
        "co(C_{4} U 2K_{1})",
        "co(gem U K_{1})",
    ]
)
@assign_class_id("gc_717")
@lru_cache(maxsize=None)
def is_maximum_degree_4(graph: nx.Graph) -> bool:
    """
    A graph is of maximum degree 4 if it is XC_{11}-free. The corresponding (partial) FISC was
    found by my xc_unpacker program.

    https://www.graphclasses.org/classes/gc_717

    @param graph:
    @return:
    """
    return degree_sequence(graph)[0] <= 4


@assign_fisc(
    [
        "X_{137}",
        "W_{6}",
        "X_{136}",
        "co(X_{183})",
        "co(X_{146})",
        "co(X_{165})",
        "co(A U K_{1})",
        "X_{110}",
        "co(X_{91})",
        "co(BW_{4})",
        "co(X_{142})",
        "co(X_{153})",
        "X_{108}",
        "X_{153}",
        "co(X_{25})",
        "co(net U K_{1})",
        "K_{7}",
        "K_{3,3,3}",
        "co(X_{155})",
        "X_{100}",
        "X_{83}",
        "co(X_{156})",
        "X_{154}",
        "co(X_{194})",
        "co(X_{144})",
        "X_{150}",
        "co(X_{135})",
        "co(X_{177})",
        "6-fan",
        "co(X_{152})",
        "co(X_{94})",
        "co(X_{160})",
        "co(X_{77})",
        "X_{54}",
        "co-star_{1,2,4}",
        "co(P_{8})",
        "co(X_{179})",
        "co(X_{143})",
        "co(X_{161})",
        "co(K_{3,3} U K_{1})",
        "co(claw U 3K_{1})",
        "X_{149}",
        "X_{145}",
        "co(S_{3} U K_{1})",
        "co(C_{6} U K_{1})",
        "co(X_{72})",
        "X_{55}",
        "X_{160}",
        "K_{1,6}",
        "co(K_{3,3}-e U K_{1})",
        "co(sunlet_{4})",
        "X_{140}",
        "X_{201}",
        "co(X_{154})",
        "co(domino U K_{1})",
        "X_{56}",
        "X_{161}",
        "co(X_{141})",
        "co(2P_{4})",
        "X_{147}",
        "friendship_{3}",
        "co(3P_{3})",
        "X_{151}",
        "co(X_{196})",
    ]
)  # <- basis of all smallgraphs with a vertex of degree >= 6, computed by compute_fisc_basis.py
@assign_class_id("gc_1139")
@lru_cache(maxsize=None)
def is_maximum_degree_5(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_1139

    @param graph:
    @return:
    """
    return degree_sequence(graph)[0] <= 5


@assign_fisc(
    [
        "X_{157}",
        "co(X_{138})",
        "co(X_{4})",
        "co(X_{141})",
        "co(X_{24})",
        "co(3P_{3})",
        "X_{155}",
        "W_{7}",
        "co(X_{183})",
        "co(X_{21})",
        "co(X_{157})",
        "co(X_{201})",
        "co(X_{94})",
        "co(X_{155})",
        "X_{156}",
        "X_{110}",
        "co(X_{91})",
        "co(X_{140})",
        "co-star_{1,2,5}",
        "co(X_{154})",
        "co(X_{208})",
        "co(X_{72})",
        "co(X_{81})",
        "co(X_{156})",
        "X_{183}",
        "co(X_{153})",
        "co(X_{207})",
        "X_{125}",
        "co(X_{76})",
        "co(X_{158})",
        "X_{158}",
        "X_{108}",
        "co(X_{73})",
        "co(X_{75})",
        "X_{57}",
        "co(X_{43})",
        "co(X_{206})",
        "co(X_{59})",
        "co(X_{139})",
    ]
)  # <- basis of all smallgraphs with a vertex of degree >= 7, computed by compute_fisc_basis.py
@assign_class_id("gc_1119")
@lru_cache(maxsize=None)
def is_maximum_degree_6(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_1119

    @param graph:
    @return:
    """
    return degree_sequence(graph)[0] <= 6


@assign_fisc(
    [
        "W_{7}",
        "X_{57}",
        "co(T_{3})",
        "co(X_{156})",
        "co(X_{157})",
        "co(X_{158})",
        "co(X_{208})",
        "co(X_{59})",
        "co(X_{75})",
        "co(X_{81})",
    ]
)  # <- basis of all smallgraphs with a vertex of degree >= 8, computed by compute_fisc_basis.py
@assign_class_id("gc_1090")
@lru_cache(maxsize=None)
def is_maximum_degree_7(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_1090

    @param graph:
    @return:
    """
    return degree_sequence(graph)[0] <= 7


# note: the FISC below was found by minor_expander.py; it is incomplete, since outerplanar graphs
# are characterized by forbidden induced **minors**; but this is as far as we can go since the
# other subgraphs produced by minor_expander.py are unknown to ISGCI
@assign_fisc(
    [
        "K_{2,3}",
        "co(X_{90})",
        "twin-C_{5}",
        "BW_{3}",
        "K_{3,3}-e",
        "K_{4}",
        "X_{203}",
        "X_{39}",
        "co(P_{2} U P_{3})",
        "co(X_{37})",
        "co(X_{88})",
        "co(X_{89})",
        "co-twin-C_{5}",
    ]
)
@assign_class_id("gc_110")
@lru_cache(maxsize=None)
def is_outerplanar(graph: nx.Graph) -> bool:
    """
    A graph is outerplanar if it has a crossing-free embedding in the plane such that all vertices
    are on the same face.

    https://www.graphclasses.org/classes/gc_110.html

    :type graph: nx.Graph
    :param graph:
    :return:
    """
    # avoid work if graph has too many edges
    if graph.size() > 2 * graph.number_of_nodes() - 3:
        return False

    # add a new vertex and connect it to all other vertices; G is outerplanar
    # iff G2 is planar (see https://link.springer.com/content/pdf/10.1007%2F3-540-17218-1_57.pdf)
    new_graph = graph.copy()
    new_graph.add_edges_from(("$", v) for v in graph)
    return is_planar(new_graph)


# note: incomplete FISC; this is the basis of all non-chordal smallgraphs in ISGCI
@assign_fisc(["C_{8}", "co(C_{5})", "C_{5}", "C_{7}", "C_{4}", "C_{6}"])
@assign_class_id("gc_32")
@lru_cache(maxsize=None)
def is_chordal(graph: nx.Graph | HalfAdjacencyMatrix) -> bool:
    """
    A graph is chordal if every cycle of length at least 4 it contains has a chord.

    https://www.graphclasses.org/classes/gc_32.html

    @param graph:
    @return:
    """
    # the following is basically a copy / paste of networkx.is_chordal, with a few minor changes so
    # it can be run on a HalfAdjacencyMatrix
    if len(graph) <= 3 or is_complete(graph):
        return True

    def _find_chordality_breaker(s=None, treewidth_bound=maxsize):
        """Given a graph G, starts a max cardinality search
        (starting from s if s is given and from an arbitrary node otherwise)
        trying to find a non-chordal cycle.

        If it does find one, it returns (u,v,w) where u,v,w are the three
        nodes that together with s are involved in the cycle.

        It ignores any self loops.
        """
        if len(graph) == 0:
            raise nx.NetworkXPointlessConcept("Graph has no nodes.")
        unnumbered = set(graph)
        if s is None:
            s = arbitrary_element(graph)
        unnumbered.remove(s)
        numbered = {s}
        current_treewidth = -1
        while unnumbered:  # and current_treewidth <= treewidth_bound:
            v = _max_cardinality_node(unnumbered, numbered)
            unnumbered.remove(v)
            numbered.add(v)
            clique_wanna_be = numbered.intersection(graph[v])
            sg = graph.subgraph(clique_wanna_be)
            if is_complete(sg):
                # The graph seems to be chordal by now. We update the treewidth
                current_treewidth = max(current_treewidth, len(clique_wanna_be))
                if current_treewidth > treewidth_bound:
                    raise nx.NetworkXTreewidthBoundExceeded(
                        f"treewidth_bound exceeded: {current_treewidth}"
                    )
            else:
                # sg is not a clique,
                # look for an edge that is not included in sg
                # (u, w) = arbitrary_element(nx.non_edges(sg))
                (u, w) = next(iter(nx.non_edges(sg)))
                return u, v, w
        return ()

    def _max_cardinality_node(choices, wanna_connect):
        """
        Returns a node in choices with the most connections in graph to nodes in wanna_connect.
        """
        max_number = -1
        max_cardinality_node = None
        for x in choices:
            number = sum(1 for y in graph[x] if y in wanna_connect)
            if number > max_number:
                max_number = number
                max_cardinality_node = x
        return max_cardinality_node

    return len(_find_chordality_breaker()) == 0


@assign_fisc(["triangle", "co(P_{3})"])
@assign_class_id("gc_1246")
@lru_cache(maxsize=None)
def is_gc_1246(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co(P_{3}), triangle)-free.

    See https://www.graphclasses.org/classes/gc_1246

    Complexity: O(m+n) < O(n^3) (naïve)

    :type graph: networkx.Graph
    """
    # a graph is (co(P_{3}), triangle)-free iff it either has no edge or is complete multipartite
    return not graph.size() or is_complete_bipartite(graph)


# @lru_cache(maxsize=None)  # cannot apply: unhashable type for indegree
def associated_forest(graph: nx.Graph, indegree: defaultdict[Any, int]) -> nx.DiGraph:
    """
    Returns the associated forest for the input graph.

    Complexity: O(m+n)

    @param graph:
    @param indegree:
    @return:
    """
    forest = nx.DiGraph()
    forest.add_nodes_from(graph)
    for vj in graph.nodes:
        if indegree[vj] >= 1:
            # find a neighbor with larger degree that maximizes indegree
            target = None
            largest = -1
            for vi in graph[vj]:
                if (
                        graph.degree[vi] > graph.degree[vj]
                        or (graph.degree[vi] == graph.degree[vj] and vi < vj)
                        and indegree[vi] > largest
                ):
                    target = vi
                    largest = indegree[vi]

            if target is not None:
                forest.add_edge(target, vj)

    return forest


@assign_fisc(["P_{4}", "C_{4}"])
@assign_class_id("gc_343")
@lru_cache(maxsize=None)
def is_quasi_threshold(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{4}, P_{4})-free.

    See https://www.graphclasses.org/classes/gc_343

    Complexity: O(m+n) < O(n^4) (naïve)

    :type graph: networkx.Graph
    """
    # this is the linear-time algorithm listed as Algorithm QT in
    # https://doi.org/10.1016/0166-218X(96)00094-7 (page 251)
    indegree = defaultdict(int)
    for vi, vj in graph.edges:
        if graph.degree[vi] > graph.degree[vj] or (
                graph.degree[vi] == graph.degree[vj] and vi < vj
        ):
            indegree[vj] += 1
        else:
            indegree[vi] += 1

    forest = associated_forest(graph, indegree)

    # use a depth-first search to compute the number anc(aj) of ancestors of Uj in F for each j;
    anc = {vj: len(nx.ancestors(forest, vj)) for vj in forest}
    return all(indegree[vj] == anc[vj] for vj in forest)


@assign_fisc(["3K_{1}", "2K_{2}", "C_{4}", "P_{4}"])
@assign_class_id("gc_1314")
@lru_cache(maxsize=None)
def is_gc_1314(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, 3K_{1}, C_{4}, P_{4})-free.

    See https://www.graphclasses.org/classes/gc_1314

    Complexity: O(m+n) < O(n^4) (naïve)

    :type graph: networkx.Graph
    """
    # A graph with n vertices is (2K_{2}, 3K_{1}, C_{4}, P_{4})-free if it contains a complete
    # graph on at least n−1 vertices.
    # so we simply iterate over each vertex v, and check whether G - {v} is complete
    all_vertices = set(graph.nodes)
    return any(is_complete(graph.subgraph(all_vertices - {v})) for v in graph.nodes)


# partial fisc: graph is cycle-free, but we will obtain those cycles through a call to is_tree
@assign_fisc(["T_{2}"])
@assign_class_id("gc_784")
@lru_cache(maxsize=None)
def is_caterpillar(graph: nx.Graph) -> bool:
    """
    A caterpillar is a tree that has a dominating path.

    https://www.graphclasses.org/classes/gc_784.html

    Complexity: O(m+n) < at least O(n^7) (naïve)

    :type graph: nx.Graph
    :param graph:
    :return:
    """
    if not is_tree(graph):
        return False

    # returns True iff subgraph induced by all nonleaves is a path
    pruned_graph = graph.subgraph(n for n, d in graph.degree if d != 1)

    # note: nx.is_path does not recognize paths ... so we check that pruned_graph is a tree with
    # degree sequence 2, 2, ... 2, 1, 1
    return degree_sequence(pruned_graph) == array(
        "Q", [2] * (pruned_graph.number_of_nodes() - 2) + [1, 1]
    ) and is_tree(pruned_graph)


# partial fisc: graph is cycle-free, but we will obtain those cycles through a call to is_tree
@assign_fisc(["T_{3}"])
@assign_class_id("gc_1341")
@lru_cache(maxsize=None)
def is_lobster(graph: nx.Graph) -> bool:
    """
    A lobster is a graph such that when we delete its leaves, we obtain a caterpillar.

    https://www.graphclasses.org/classes/gc_1341.html

    Complexity: O(m+n) < at least O(n^10) (naïve)

    @type graph: nx.Graph
    @param graph:
    @return:
    """
    # returns True iff subgraph induced by all nonleaves is a caterpillar
    return is_tree(graph) and is_caterpillar(  # just to avoid building subgraph if possible
        graph.subgraph(n for n, d in graph.degree if d != 1)
    )


@assign_fisc(["P_{4}"])
@assign_class_id("gc_152")
@lru_cache(maxsize=None)
def is_cograph(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is P_{4}-free.

    See https://www.graphclasses.org/classes/gc_152

    Complexity: O(m+n) < O(n^4) (naïve)

    :type graph: networkx.Graph
    """
    # an empty graph is necessarily P_{4}-free: catch case to prevent to_cotree from raising an
    # exception
    return not graph or to_cotree(graph) is not False


@assign_fisc(
    ["P_{4}", "K_{3}", "C_{4}", "C_{5}", "C_{6}", "C_{7}", "C_{8}"]
)  # partial fisc: graph is cycle-free
@assign_class_id("gc_1298")
@lru_cache(maxsize=None)
def is_p4_cycle_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_1298

    @param graph:
    @return:
    """
    return is_cograph(graph) and nx.is_forest(graph)


@assign_fisc(
    ["co(C_{4})", "co(C_{6})", "co(C_{7})", "co(C_{8})", "co(C_{5})", "3K_{1}"]
)  # partial fisc: graph is co-cycle-free
@assign_class_id("AUTO_2103")
@lru_cache(maxsize=None)
def is_co_tree(graph: nx.Graph) -> bool:
    """
    A graph is a co-tree if its complement is a tree.

    https://www.graphclasses.org/classes/AUTO_2103.html

    @type graph: nx.Graph
    @param graph:
    @return:
    """
    # the complement must have n-1 edges in order to be a tree
    n = graph.number_of_nodes()
    num_co_edges = (n * (n - 1)) // 2 - graph.size()
    if num_co_edges != n - 1:
        return False

    # since the complement has n-1 edges, it is a tree iff it has no isolated vertices
    return all(sum(1 for _ in nx.non_neighbors(graph, v)) for v in graph)


# the fisc will be obtained through calls to constituent class recognizers
@assign_class_id("gc_985")
@lru_cache(maxsize=None)
def is_chordal_and_planar(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_985

    @param graph:
    @return:
    """
    return is_chordal(graph) and is_planar(graph)


# note: the FISC is incomplete, but these are the only odd co-cycles that are stored as smallgraphs
@assign_fisc(["3K_{1}", "co(C_{5})", "co(C_{7})"])
@assign_class_id("gc_486")
@lru_cache(maxsize=None)
def is_co_bipartite(graph: nx.Graph) -> bool:
    """
    Returns True iff the complement of graph is bipartite.

    https://www.graphclasses.org/classes/gc_486.html

    :param graph:
    :return:
    """
    # the empty graph is trivially co-bipartite iff it has at most 2 nodes
    if not graph.size():
        return graph.order() <= 2

    # the complete graph is trivially co-bipartite
    if is_complete(graph):
        return True

    # if complement has too many edges, then it cannot be bipartite
    n = graph.number_of_nodes()
    m = (n * (n - 1)) // 2 - graph.number_of_edges()
    if m > (n ** 2) / 4:
        return False

    # launch a BFS from each vertex, since we don't know that the complement is connected
    # this is basically networkx.bipartite.color(graph) on non neighbors
    color = dict()
    for n in graph:
        if n in color:
            continue
        queue = [n]
        color[n] = 1  # nodes seen with color (1 or 0)
        while queue:
            v = queue.pop()
            c = 1 - color[v]  # opposite color of node v
            for w in nx.non_neighbors(graph, v):
                if w in color:
                    if color[w] == color[v]:
                        return False
                else:
                    color[w] = c
                    queue.append(w)

    return True


# the fisc will be obtained through calls to constituent class recognizers
@assign_class_id("gc_847")
@lru_cache(maxsize=None)
def is_binary_tree(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_847

    @param graph:
    @return:
    """
    return is_maximum_degree_3(graph) and is_tree(graph)


# this very long partial fisc is the list of all subgraphs with a vertex of degree > 3
@assign_fisc(
    [
        "4-fan",
        "6-fan",
        "BW_{4}",
        "K_{1,4}",
        "K_{1,5}",
        "K_{1,6}",
        "K_{3,3,3}",
        "K_{3,3}+e",
        "K_{3,4}",
        "K_{3,4}-e",
        "K_{4,4}",
        "K_{5}",
        "K_{5} - e",
        "K_{6}",
        "K_{7}",
        "R",
        "S_{3}",
        "S_{3} U K_{1}",
        "S_{4}",
        "W_{4}",
        "W_{4} U K_{1}",
        "W_{5}",
        "W_{6}",
        "W_{7}",
        "X_{100}",
        "X_{101}",
        "X_{102}",
        "X_{103}",
        "X_{104}",
        "X_{105}",
        "X_{106}",
        "X_{107}",
        "X_{108}",
        "X_{109}",
        "X_{10}",
        "X_{110}",
        "X_{112}",
        "X_{113}",
        "X_{114}",
        "X_{115}",
        "X_{116}",
        "X_{117}",
        "X_{118}",
        "X_{119}",
        "X_{11}",
        "X_{120}",
        "X_{121}",
        "X_{122}",
        "X_{123}",
        "X_{124}",
        "X_{125}",
        "X_{127}",
        "X_{128}",
        "X_{129}",
        "X_{12}",
        "X_{130}",
        "X_{131}",
        "X_{132}",
        "X_{133}",
        "X_{134}",
        "X_{135}",
        "X_{136}",
        "X_{137}",
        "X_{138}",
        "X_{139}",
        "X_{13}",
        "X_{140}",
        "X_{141}",
        "X_{142}",
        "X_{143}",
        "X_{144}",
        "X_{145}",
        "X_{146}",
        "X_{147}",
        "X_{148}",
        "X_{149}",
        "X_{14}",
        "X_{150}",
        "X_{151}",
        "X_{152}",
        "X_{153}",
        "X_{154}",
        "X_{155}",
        "X_{156}",
        "X_{157}",
        "X_{158}",
        "X_{159}",
        "X_{15}",
        "X_{160}",
        "X_{161}",
        "X_{162}",
        "X_{163}",
        "X_{167}",
        "X_{168}",
        "X_{169}",
        "X_{170}",
        "X_{175}",
        "X_{176}",
        "X_{178}",
        "X_{179}",
        "X_{17}",
        "X_{181}",
        "X_{182}",
        "X_{183}",
        "X_{184}",
        "X_{185}",
        "X_{186}",
        "X_{187}",
        "X_{188}",
        "X_{189}",
        "X_{190}",
        "X_{191}",
        "X_{192}",
        "X_{193}",
        "X_{194}",
        "X_{195}",
        "X_{196}",
        "X_{199}",
        "X_{1}",
        "X_{200}",
        "X_{201}",
        "X_{202}",
        "X_{205}",
        "X_{206}",
        "X_{208}",
        "X_{21}",
        "X_{22}",
        "X_{23}",
        "X_{24}",
        "X_{25}",
        "X_{26}",
        "X_{27}",
        "X_{28}",
        "X_{29}",
        "X_{31}",
        "X_{32}",
        "X_{33}",
        "X_{34}",
        "X_{35}",
        "X_{36}",
        "X_{3}",
        "X_{40}",
        "X_{42}",
        "X_{43}",
        "X_{46}",
        "X_{47}",
        "X_{48}",
        "X_{49}",
        "X_{4}",
        "X_{50}",
        "X_{51}",
        "X_{52}",
        "X_{53}",
        "X_{54}",
        "X_{55}",
        "X_{56}",
        "X_{57}",
        "X_{58}",
        "X_{5}",
        "X_{70}",
        "X_{72}",
        "X_{80}",
        "X_{82}",
        "X_{83}",
        "X_{86}",
        "X_{87}",
        "X_{88}",
        "X_{89}",
        "X_{90}",
        "X_{92}",
        "X_{93}",
        "X_{94}",
        "X_{96}",
        "X_{97}",
        "X_{98}",
        "X_{99}",
        "X_{9}",
        "butterfly",
        "butterfly U K_{1}",
        "co(2C_{4})",
        "co(2P_{3})",
        "co(2P_{4})",
        "co(3K_{2})",
        "co(3P_{3})",
        "co(5-pan)",
        "co(6-pan)",
        "co(A U K_{1})",
        "co(A)",
        "co(BW_{3})",
        "co(BW_{4})",
        "co(C_{4} U 2K_{1})",
        "co(C_{4} U P_{2})",
        "co(C_{6} U K_{1})",
        "co(C_{7})",
        "co(C_{8})",
        "co(E)",
        "co(H)",
        "co(K_{1,5})",
        "co(K_{2} U claw)",
        "co(K_{3,3} U K_{1})",
        "co(K_{3,3}-e U K_{1})",
        "co(K_{3,4}-e)",
        "co(K_{3} U 2K_{1})",
        "co(K_{3} U 3K_{1})",
        "co(P_{2} U P_{4})",
        "co(P_{3} U 2K_{1})",
        "co(P_{3} U P_{4})",
        "co(P_{6})",
        "co(P_{7})",
        "co(P_{8})",
        "co(R)",
        "co(S_{3} U K_{1})",
        "co(S_{4})",
        "co(T_{2})",
        "co(T_{3})",
        "co(W_{4} U K_{1})",
        "co(W_{7})",
        "co(X_{100})",
        "co(X_{101})",
        "co(X_{102})",
        "co(X_{103})",
        "co(X_{105})",
        "co(X_{107})",
        "co(X_{109})",
        "co(X_{10})",
        "co(X_{110})",
        "co(X_{111})",
        "co(X_{112})",
        "co(X_{113})",
        "co(X_{114})",
        "co(X_{115})",
        "co(X_{116})",
        "co(X_{117})",
        "co(X_{118})",
        "co(X_{119})",
        "co(X_{120})",
        "co(X_{121})",
        "co(X_{122})",
        "co(X_{123})",
        "co(X_{124})",
        "co(X_{125})",
        "co(X_{126})",
        "co(X_{127})",
        "co(X_{128})",
        "co(X_{129})",
        "co(X_{130})",
        "co(X_{131})",
        "co(X_{132})",
        "co(X_{133})",
        "co(X_{134})",
        "co(X_{135})",
        "co(X_{136})",
        "co(X_{137})",
        "co(X_{138})",
        "co(X_{139})",
        "co(X_{13})",
        "co(X_{140})",
        "co(X_{141})",
        "co(X_{142})",
        "co(X_{143})",
        "co(X_{144})",
        "co(X_{145})",
        "co(X_{146})",
        "co(X_{147})",
        "co(X_{148})",
        "co(X_{149})",
        "co(X_{14})",
        "co(X_{150})",
        "co(X_{151})",
        "co(X_{152})",
        "co(X_{153})",
        "co(X_{154})",
        "co(X_{155})",
        "co(X_{156})",
        "co(X_{157})",
        "co(X_{158})",
        "co(X_{159})",
        "co(X_{160})",
        "co(X_{161})",
        "co(X_{162})",
        "co(X_{163})",
        "co(X_{164})",
        "co(X_{165})",
        "co(X_{166})",
        "co(X_{167})",
        "co(X_{168})",
        "co(X_{169})",
        "co(X_{170})",
        "co(X_{171})",
        "co(X_{172})",
        "co(X_{173})",
        "co(X_{174})",
        "co(X_{175})",
        "co(X_{176})",
        "co(X_{177})",
        "co(X_{178})",
        "co(X_{179})",
        "co(X_{17})",
        "co(X_{180})",
        "co(X_{181})",
        "co(X_{182})",
        "co(X_{183})",
        "co(X_{185})",
        "co(X_{186})",
        "co(X_{187})",
        "co(X_{189})",
        "co(X_{18})",
        "co(X_{190})",
        "co(X_{191})",
        "co(X_{192})",
        "co(X_{193})",
        "co(X_{194})",
        "co(X_{195})",
        "co(X_{196})",
        "co(X_{197})",
        "co(X_{198})",
        "co(X_{199})",
        "co(X_{19})",
        "co(X_{1})",
        "co(X_{200})",
        "co(X_{201})",
        "co(X_{202})",
        "co(X_{204})",
        "co(X_{205})",
        "co(X_{206})",
        "co(X_{207})",
        "co(X_{208})",
        "co(X_{20})",
        "co(X_{21})",
        "co(X_{22})",
        "co(X_{23})",
        "co(X_{24})",
        "co(X_{25})",
        "co(X_{26})",
        "co(X_{27})",
        "co(X_{28})",
        "co(X_{29})",
        "co(X_{2})",
        "co(X_{30})",
        "co(X_{31})",
        "co(X_{32})",
        "co(X_{33})",
        "co(X_{34})",
        "co(X_{35})",
        "co(X_{36})",
        "co(X_{38})",
        "co(X_{39})",
        "co(X_{3})",
        "co(X_{40})",
        "co(X_{41})",
        "co(X_{42})",
        "co(X_{43})",
        "co(X_{45})",
        "co(X_{46})",
        "co(X_{47})",
        "co(X_{48})",
        "co(X_{49})",
        "co(X_{4})",
        "co(X_{50})",
        "co(X_{51})",
        "co(X_{52})",
        "co(X_{53})",
        "co(X_{54})",
        "co(X_{55})",
        "co(X_{56})",
        "co(X_{57})",
        "co(X_{58})",
        "co(X_{59})",
        "co(X_{6})",
        "co(X_{70})",
        "co(X_{71})",
        "co(X_{72})",
        "co(X_{73})",
        "co(X_{74})",
        "co(X_{75})",
        "co(X_{76})",
        "co(X_{77})",
        "co(X_{79})",
        "co(X_{7})",
        "co(X_{80})",
        "co(X_{81})",
        "co(X_{82})",
        "co(X_{83})",
        "co(X_{84})",
        "co(X_{85})",
        "co(X_{87})",
        "co(X_{8})",
        "co(X_{91})",
        "co(X_{92})",
        "co(X_{93})",
        "co(X_{94})",
        "co(X_{95})",
        "co(X_{96})",
        "co(X_{97})",
        "co(X_{99})",
        "co(X_{9})",
        "co(butterfly U K_{1})",
        "co(claw U 3K_{1})",
        "co(claw U K_{1})",
        "co(claw U triangle)",
        "co(co-fork U K_{1})",
        "co(domino U K_{1})",
        "co(gem U K_{1})",
        "co(net U K_{1})",
        "co(star_{1,2,3})",
        "co(sunlet_{4})",
        "co-6-fan",
        "co-X_{104}",
        "co-antenna",
        "co-cross",
        "co-eiffeltower",
        "co-longhorn",
        "co-rising sun",
        "co-star_{1,2,4}",
        "co-star_{1,2,5}",
        "cricket",
        "cross",
        "dart",
        "fish",
        "friendship_{3}",
        "gem",
        "gem U K_{1}",
        "parachute",
        "parapluie",
        "rising sun",
        "twin-house",
    ]
)
@assign_class_id("gc_1100")
@lru_cache(maxsize=None)
def is_cubic(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_1100

    @param graph:
    @return:
    """
    if 2 * graph.size() != 3 * graph.number_of_nodes():
        return False
    degseq = degree_sequence(graph)
    return degseq[0] == degseq[-1] == 3


# this very long partial fisc is the list of all subgraphs with a vertex of degree > 4
@assign_fisc(
    [
        "4-fan",
        "6-fan",
        "K_{1,5}",
        "K_{1,6}",
        "K_{3,3,3}",
        "K_{6}",
        "K_{7}",
        "S_{4}",
        "W_{5}",
        "W_{6}",
        "W_{7}",
        "X_{100}",
        "X_{102}",
        "X_{103}",
        "X_{105}",
        "X_{106}",
        "X_{107}",
        "X_{108}",
        "X_{109}",
        "X_{110}",
        "X_{112}",
        "X_{113}",
        "X_{114}",
        "X_{115}",
        "X_{116}",
        "X_{117}",
        "X_{118}",
        "X_{119}",
        "X_{120}",
        "X_{121}",
        "X_{122}",
        "X_{123}",
        "X_{124}",
        "X_{125}",
        "X_{128}",
        "X_{12}",
        "X_{131}",
        "X_{133}",
        "X_{135}",
        "X_{136}",
        "X_{137}",
        "X_{139}",
        "X_{140}",
        "X_{141}",
        "X_{143}",
        "X_{144}",
        "X_{145}",
        "X_{146}",
        "X_{147}",
        "X_{148}",
        "X_{149}",
        "X_{14}",
        "X_{150}",
        "X_{151}",
        "X_{153}",
        "X_{154}",
        "X_{155}",
        "X_{156}",
        "X_{157}",
        "X_{158}",
        "X_{159}",
        "X_{15}",
        "X_{160}",
        "X_{161}",
        "X_{162}",
        "X_{175}",
        "X_{178}",
        "X_{179}",
        "X_{182}",
        "X_{183}",
        "X_{184}",
        "X_{193}",
        "X_{194}",
        "X_{196}",
        "X_{199}",
        "X_{1}",
        "X_{200}",
        "X_{201}",
        "X_{23}",
        "X_{24}",
        "X_{31}",
        "X_{34}",
        "X_{47}",
        "X_{48}",
        "X_{49}",
        "X_{4}",
        "X_{50}",
        "X_{51}",
        "X_{52}",
        "X_{53}",
        "X_{54}",
        "X_{55}",
        "X_{56}",
        "X_{57}",
        "X_{82}",
        "X_{83}",
        "X_{97}",
        "co(2C_{4})",
        "co(2P_{4})",
        "co(3P_{3})",
        "co(6-pan)",
        "co(A U K_{1})",
        "co(BW_{4})",
        "co(C_{4} U 2K_{1})",
        "co(C_{6} U K_{1})",
        "co(C_{8})",
        "co(K_{3,3} U K_{1})",
        "co(K_{3,3}-e U K_{1})",
        "co(K_{3} U 3K_{1})",
        "co(P_{3} U P_{4})",
        "co(P_{7})",
        "co(P_{8})",
        "co(S_{3} U K_{1})",
        "co(S_{4})",
        "co(T_{2})",
        "co(T_{3})",
        "co(W_{4} U K_{1})",
        "co(W_{7})",
        "co(X_{127})",
        "co(X_{129})",
        "co(X_{130})",
        "co(X_{131})",
        "co(X_{132})",
        "co(X_{134})",
        "co(X_{135})",
        "co(X_{136})",
        "co(X_{137})",
        "co(X_{138})",
        "co(X_{139})",
        "co(X_{13})",
        "co(X_{140})",
        "co(X_{141})",
        "co(X_{142})",
        "co(X_{143})",
        "co(X_{144})",
        "co(X_{145})",
        "co(X_{146})",
        "co(X_{147})",
        "co(X_{148})",
        "co(X_{149})",
        "co(X_{150})",
        "co(X_{151})",
        "co(X_{152})",
        "co(X_{153})",
        "co(X_{154})",
        "co(X_{155})",
        "co(X_{156})",
        "co(X_{157})",
        "co(X_{158})",
        "co(X_{159})",
        "co(X_{160})",
        "co(X_{161})",
        "co(X_{162})",
        "co(X_{164})",
        "co(X_{165})",
        "co(X_{174})",
        "co(X_{176})",
        "co(X_{177})",
        "co(X_{178})",
        "co(X_{179})",
        "co(X_{180})",
        "co(X_{181})",
        "co(X_{182})",
        "co(X_{183})",
        "co(X_{185})",
        "co(X_{189})",
        "co(X_{194})",
        "co(X_{195})",
        "co(X_{196})",
        "co(X_{197})",
        "co(X_{198})",
        "co(X_{199})",
        "co(X_{19})",
        "co(X_{201})",
        "co(X_{204})",
        "co(X_{205})",
        "co(X_{206})",
        "co(X_{207})",
        "co(X_{208})",
        "co(X_{20})",
        "co(X_{21})",
        "co(X_{22})",
        "co(X_{23})",
        "co(X_{24})",
        "co(X_{25})",
        "co(X_{26})",
        "co(X_{28})",
        "co(X_{29})",
        "co(X_{2})",
        "co(X_{30})",
        "co(X_{31})",
        "co(X_{32})",
        "co(X_{3})",
        "co(X_{41})",
        "co(X_{43})",
        "co(X_{47})",
        "co(X_{48})",
        "co(X_{49})",
        "co(X_{4})",
        "co(X_{50})",
        "co(X_{51})",
        "co(X_{52})",
        "co(X_{54})",
        "co(X_{55})",
        "co(X_{57})",
        "co(X_{59})",
        "co(X_{6})",
        "co(X_{70})",
        "co(X_{71})",
        "co(X_{72})",
        "co(X_{73})",
        "co(X_{74})",
        "co(X_{75})",
        "co(X_{76})",
        "co(X_{77})",
        "co(X_{81})",
        "co(X_{83})",
        "co(X_{85})",
        "co(X_{91})",
        "co(X_{92})",
        "co(X_{94})",
        "co(X_{99})",
        "co(butterfly U K_{1})",
        "co(claw U 3K_{1})",
        "co(claw U triangle)",
        "co(co-fork U K_{1})",
        "co(domino U K_{1})",
        "co(gem U K_{1})",
        "co(net U K_{1})",
        "co(star_{1,2,3})",
        "co(sunlet_{4})",
        "co-eiffeltower",
        "co-longhorn",
        "co-star_{1,2,4}",
        "co-star_{1,2,5}",
        "friendship_{3}",
        "parachute",
        "parapluie",
        "rising sun",
    ]
)
@assign_class_id("gc_1101")
@lru_cache(maxsize=None)
def is_4_regular(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_1101

    @param graph:
    @return:
    """
    if 2 * graph.size() != 4 * graph.number_of_nodes():
        return False
    degseq = degree_sequence(graph)
    return degseq[0] == degseq[-1] == 4


# the fisc will be obtained through calls to constituent class recognizers
@assign_class_id("gc_1103")
@lru_cache(maxsize=None)
def is_4_regular_planar(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_1103

    @param graph:
    @return:
    """
    return is_4_regular(graph) and is_planar(graph)


# this very long partial fisc is the list of all subgraphs with a vertex of degree > 5
@assign_fisc(
    [
        "6-fan",
        "K_{1,6}",
        "K_{3,3,3}",
        "K_{7}",
        "W_{6}",
        "W_{7}",
        "X_{100}",
        "X_{108}",
        "X_{110}",
        "X_{125}",
        "X_{136}",
        "X_{137}",
        "X_{140}",
        "X_{141}",
        "X_{145}",
        "X_{147}",
        "X_{149}",
        "X_{150}",
        "X_{151}",
        "X_{153}",
        "X_{154}",
        "X_{155}",
        "X_{156}",
        "X_{157}",
        "X_{158}",
        "X_{160}",
        "X_{161}",
        "X_{183}",
        "X_{196}",
        "X_{201}",
        "X_{54}",
        "X_{55}",
        "X_{56}",
        "X_{57}",
        "X_{83}",
        "co(2P_{4})",
        "co(3P_{3})",
        "co(A U K_{1})",
        "co(BW_{4})",
        "co(C_{6} U K_{1})",
        "co(K_{3,3} U K_{1})",
        "co(K_{3,3}-e U K_{1})",
        "co(P_{8})",
        "co(S_{3} U K_{1})",
        "co(T_{3})",
        "co(W_{7})",
        "co(X_{135})",
        "co(X_{138})",
        "co(X_{139})",
        "co(X_{140})",
        "co(X_{141})",
        "co(X_{142})",
        "co(X_{143})",
        "co(X_{144})",
        "co(X_{146})",
        "co(X_{152})",
        "co(X_{153})",
        "co(X_{154})",
        "co(X_{155})",
        "co(X_{156})",
        "co(X_{157})",
        "co(X_{158})",
        "co(X_{160})",
        "co(X_{161})",
        "co(X_{165})",
        "co(X_{174})",
        "co(X_{177})",
        "co(X_{179})",
        "co(X_{183})",
        "co(X_{194})",
        "co(X_{196})",
        "co(X_{19})",
        "co(X_{201})",
        "co(X_{206})",
        "co(X_{207})",
        "co(X_{208})",
        "co(X_{21})",
        "co(X_{22})",
        "co(X_{23})",
        "co(X_{24})",
        "co(X_{25})",
        "co(X_{29})",
        "co(X_{43})",
        "co(X_{4})",
        "co(X_{57})",
        "co(X_{59})",
        "co(X_{71})",
        "co(X_{72})",
        "co(X_{73})",
        "co(X_{75})",
        "co(X_{76})",
        "co(X_{77})",
        "co(X_{81})",
        "co(X_{91})",
        "co(X_{94})",
        "co(claw U 3K_{1})",
        "co(domino U K_{1})",
        "co(net U K_{1})",
        "co(sunlet_{4})",
        "co-star_{1,2,4}",
        "co-star_{1,2,5}",
        "friendship_{3}",
    ]
)
@assign_class_id("gc_1104")
@lru_cache(maxsize=None)
def is_5_regular(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_1104

    @param graph:
    @return:
    """
    if 2 * graph.size() != 5 * graph.number_of_nodes():
        return False
    degseq = degree_sequence(graph)
    return degseq[0] == degseq[-1] == 5


# the fisc will be obtained through calls to constituent class recognizers
@assign_class_id("gc_1106")
@lru_cache(maxsize=None)
def is_5_regular_planar(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_1106

    @param graph:
    @return:
    """
    return is_5_regular(graph) and is_planar(graph)


# the fisc will be obtained through calls to constituent class recognizers
@assign_class_id("gc_1069")
@lru_cache(maxsize=None)
def is_bipartite_and_planar(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_1069

    @param graph:
    @return:
    """
    return is_bipartite(graph) and is_planar(graph)


# the fisc will be obtained through calls to constituent class recognizers
@assign_class_id("gc_1102")
@lru_cache(maxsize=None)
def is_cubic_planar(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_1102

    @param graph:
    @return:
    """
    return is_cubic(graph) and is_planar(graph)


# the fisc will be obtained through calls to constituent class recognizers
@assign_class_id("gc_1183")
@lru_cache(maxsize=None)
def is_2_connected_cubic_planar(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_1183

    @param graph:
    @return:
    """
    return nx.is_biconnected(graph) and is_cubic_planar(graph)


# the fisc will be obtained through calls to constituent class recognizers
@assign_class_id("gc_941")
@lru_cache(maxsize=None)
def is_bipartite_and_maximum_degree_3(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_941

    @param graph:
    @return:
    """
    return is_maximum_degree_3(graph) and is_bipartite(graph)


# the fisc will be obtained through calls to constituent class recognizers
@assign_class_id("gc_1055")
@lru_cache(maxsize=None)
def is_bipartite_and_maximum_degree_3_and_planar(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_1055

    @param graph:
    @return:
    """
    return is_maximum_degree_3(graph) and is_bipartite_and_planar(graph)


# the fisc will be obtained through calls to constituent class recognizers
@assign_class_id("gc_1153")
@lru_cache(maxsize=None)
def is_bipartite_and_maximum_degree_4_and_planar(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_1153

    @param graph:
    @return:
    """
    return is_maximum_degree_4(graph) and is_bipartite_and_planar(graph)


# the fisc will be obtained through calls to constituent class recognizers
@assign_class_id("gc_1334")
@lru_cache(maxsize=None)
def is_bipartite_cubic_planar(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_1334

    @param graph:
    @return:
    """
    return is_bipartite(graph) and is_cubic_planar(graph)


# the fisc will be obtained through calls to constituent class recognizers
@assign_class_id("gc_412")
@lru_cache(maxsize=None)
def is_planar_and_maximum_degree_3(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_412

    @param graph:
    @return:
    """
    return is_maximum_degree_3(graph) and is_planar(graph)


# the fisc will be obtained through calls to constituent class recognizers
@assign_class_id("gc_909")
@lru_cache(maxsize=None)
def is_planar_and_maximum_degree_4(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_909

    @param graph:
    @return:
    """
    return is_maximum_degree_4(graph) and is_planar(graph)


@assign_fisc(
    [
        "5K_{1}",  # complement of "K_{5}",
        "co(K_{5} - e)",  # complement of "K_{5} - e",
        "claw U K_{1}",  # complement of "co(claw U K_{1})",
        "co(K_{1,4})",  # complement of "K_{1,4}",
        "P_{3} U 2K_{1}",  # complement of "co(P_{3} U 2K_{1})",
        "co-dart",  # complement of "dart",
        "co-gem",  # complement of "gem",
        "co-cricket",  # complement of "cricket",
        "co(W_{4})",  # complement of "W_{4}",
        "K_{3} U 2K_{1}",  # complement of "co(K_{3} U 2K_{1})",
        "co-butterfly",  # complement of "butterfly",
    ]
)
@assign_class_id("AUTO_2122")
@lru_cache(maxsize=None)
def is_co_maximum_degree_3(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_2122.html

    @param graph:
    @return:
    """
    # the complement has maximum degree 3 iff the original graph has minimum degree n-4
    return degree_sequence(graph)[-1] >= graph.number_of_nodes() - 4


# the fisc will be obtained through calls to constituent class recognizers
@assign_class_id("gc_1361")
@lru_cache(maxsize=None)
def is_bipartite_or_co_bipartite_or_split(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_1361

    @param graph:
    @return:
    """
    return is_bipartite(graph) or is_co_bipartite(graph) or is_split(graph)


# the fisc will be obtained through calls to constituent class recognizers
@assign_class_id("AUTO_2145")
@lru_cache(maxsize=None)
def is_co_binary_tree(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_2145

    @param graph:
    @return:
    """
    return is_co_maximum_degree_3(graph) and is_co_tree(graph)


# the fisc will be obtained through calls to constituent class recognizers
@assign_class_id("AUTO_2158")
@lru_cache(maxsize=None)
def is_co_bipartite_and_maximum_degree_3(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_2158

    @param graph:
    @return:
    """
    return is_co_maximum_degree_3(graph) and is_co_bipartite(graph)


# derived from the fisc for maximum_degree_4
@assign_fisc(
    [
        "co-4-fan",  # complement of "4-fan",
        "co-fork U K_{1}",  # complement of "co(co-fork U K_{1})",
        "co(W_{5})",  # complement of "W_{5}",
        "butterfly U K_{1}",  # complement of "co(butterfly U K_{1})",
        "K_{3} U 3K_{1}",  # complement of "co(K_{3} U 3K_{1})",
        "W_{4} U K_{1}",  # complement of "co(W_{4} U K_{1})",
        "X_{198}",  # complement of "co(X_{198})",
        "co(K_{1,5})",  # complement of "K_{1,5}",
        "6K_{1}",  # complement of "K_{6}",
        "X_{197}",  # complement of "co(X_{197})",
        "C_{4} U 2K_{1}",  # complement of "co(C_{4} U 2K_{1})",
        "gem U K_{1}",  # complement of "co(gem U K_{1})",
    ]
)
@assign_class_id("AUTO_2121")
@lru_cache(maxsize=None)
def is_co_maximum_degree_4(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_2121.html

    @param graph:
    @return:
    """
    # the complement has maximum degree 4 iff the original graph has minimum degree n-5
    return degree_sequence(graph)[-1] >= graph.number_of_nodes() - 5


# the fisc will be obtained through calls to constituent class recognizers
@assign_class_id("AUTO_3081")
@lru_cache(maxsize=None)
def is_co_xc11_odd_cycle_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_3081

    @param graph:
    @return:
    """
    return is_co_maximum_degree_4(graph) and is_co_bipartite(graph)


# the fisc will be obtained through calls to constituent class recognizers
@assign_class_id("AUTO_823")
@lru_cache(maxsize=None)
def is_xc11_odd_cycle_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_823

    @param graph:
    @return:
    """
    return is_maximum_degree_4(graph) and is_bipartite(graph)


@assign_fisc(["2K_{2}"])
@assign_class_id("gc_394")
@lru_cache(maxsize=None)
def is_2k2_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is 2K_{2}-free.

    See https://www.graphclasses.org/classes/gc_394

    Complexity: O(m+n) < O(n^4) (naïve)

    :type graph: networkx.Graph
    """
    # if graph has at least two components with at least one edge each, then it contains a 2K_{2}
    # O(m+n)
    nontrivial_ccs = 0
    for cc in nx.connected_components(graph):
        nontrivial_ccs += len(cc) > 1
        if nontrivial_ccs >= 2:
            return False

    # otherwise, go through every edge and remove it with its neighbors; if the resulting graph is
    # empty, then it is K_{2}-free, and so our graph is 2K_{2}-free
    # O(m)
    return is_h_u_k2_free(graph, undecorated_function(is_k2_free))


@assign_fisc(
    [
        "co(W_{5})",
        "K_{2,3}",
        "co(X_{90})",
        "diamond",
        "K_{4}",
        "twin-C_{5}",
        "domino",
        "butterfly",
        "house",
    ]
)
# partial fisc found by querying all smallgraphs with at least 2 cycles, then computing a basis
# with tools.compute_fisc_basis
@assign_class_id("gc_1202")
@lru_cache(maxsize=None)
def is_unicyclic(graph: nx.Graph) -> bool:
    """A graph is unicyclic if it is connected and contains precisely one
    cycle.

    https://www.graphclasses.org/classes/gc_1202.html

    """
    return is_connected(graph) and graph.size() == graph.number_of_nodes()


@assign_fisc(["P_{4}", "2K_{2}"])
@assign_class_id("gc_171")
@lru_cache(maxsize=None)
def is_2k2_p4_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, P_{4})-free.

    See https://www.graphclasses.org/classes/gc_171

    Complexity: O(m+n) < O(n^4) (naïve)

    :type graph: networkx.Graph
    """
    return is_cograph(graph) and is_2k2_free(graph)


@assign_fisc(["triangle", "2K_{2}", "C_{5}"])
@assign_class_id("gc_1301")
@lru_cache(maxsize=None)
def is_gc_1301(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, C_{5}, triangle)-free.

    See https://www.graphclasses.org/classes/gc_1301

    Complexity: O(m+n) < O(n^5) (naïve)

    :type graph: networkx.Graph
    """
    # equivalent to https://www.graphclasses.org/classes/gc_443.html = 2K_{2}-free and bipartite
    return is_bipartite(graph) and is_2k2_free(graph)


@assign_class_id("gc_981")
@lru_cache(maxsize=None)
def is_maximal_planar(graph: nx.Graph) -> bool:
    """
    A planar graph is maximal planar if it is not possible to add an edge such that the graph is
    still planar.

    https://www.graphclasses.org/classes/gc_981

    Complexity: O(m+n); the algorithm simply checks that the graph is planar and that it contains
    the largest possible number of edges.

    :param graph:
    :return:
    """
    return graph.number_of_edges() == 3 * graph.number_of_nodes() - 6 and is_planar(graph)


@assign_class_id("gc_982")
@lru_cache(maxsize=None)
def is_chordal_and_maximal_planar(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_982

    @param graph:
    @return:
    """
    return is_chordal(graph) and is_maximal_planar(graph)


@assign_class_id("gc_723")
@lru_cache(maxsize=None)
def is_maximal_outerplanar(graph: nx.Graph) -> bool:
    """
    An outerplanar graph is maximal outerplanar if it is not possible to add an edge such that the
    resulting graph is still outerplanar.

    https://www.graphclasses.org/classes/gc_723

    Complexity: O(m+n); check that the graph is outerplanar and that it has the maximum number of
    edges.

    :param graph:
    :return:
    """
    return (
            graph.number_of_edges() == 2 * graph.number_of_nodes() - 3
            and is_outerplanar(graph)
    )


# the following fisc is partial for now: it comes from https://doi.org/10.1016/j.disc.2018.04.023
# in which Theorem 18 lists all cycles and co-cycles of length >= 5 ... as well as 318 other
# graphs, which may or may not be in ISGCI
@assign_fisc(
    [
        "C_{5}",
        "C_{6}",
        "C_{7}",
        "C_{8}",
        "co(C_{5})",
        "co(C_{6})",
        "co(C_{7})",
        "co(C_{8})",
        # TODO the 318 other graphs:
        # forbidden graphs from fig 6 p. 2173: all of them should appear here AND their complements
        # fig 6 line 1
        "domino",  # fig 6 line 1 column 1
        "co-domino",
        "2K_{3}",  # fig 6 line 1 column 2
        "K_{3,3}",
        "2K_{3} + e",  # fig 6 line 1 column 3
        "K_{3,3}-e",
        # TODO line 1 column 4 not found
        "X_{7}",  # fig 6 line 1 column 5
        "co(X_{7})",
        # fig 6 line 2
        "X_{27}",  # fig 6 line 2 column 1
        "co(X_{27})",
        # TODO line 2 column 2 not found
        # TODO line 2 column 3 not found; how does it differ from the next entry?
        # TODO line 2 column 4 not found; how does it differ from the previous entry?
        # TODO line 2 column 5
        # TODO line 3 column 1
        # TODO line 3 column 2
        # TODO line 3 column 3
        # TODO line 3 column 4
        # TODO line 3 column 5
        # TODO line 4 column 1 not found
        # TODO line 4 column 2 not found
        # end of fig 6
        # TODO the graphs from figure 7 + their complements
        # forbidden graphs from fig 7 p. 2174: all of them should appear here AND their complements
        "S_{4}",  # fig 7 (1, 1), self-complementary
        # TODO fig 7 line 1 column 2
        # TODO fig 7 line 1 column 3
        # TODO fig 7 line 1 column 4
        # TODO fig 7 line 1 column 5
        # TODO fig 7 line 2 column 1
        # TODO fig 7 line 2 column 2
        # TODO fig 7 line 2 column 3
        # TODO fig 7 line 2 column 4
        # TODO fig 7 line 2 column 5
        # TODO fig 7 line 3 column 1
        # TODO fig 7 line 3 column 2
        # TODO fig 7 line 3 column 3
        # TODO fig 7 line 3 column 4
        # TODO fig 7 line 3 column 5
        # TODO fig 7 line 4 column 1
        # TODO fig 7 line 4 column 2
        "2C_{4}",  # fig 7 line 4 column 3
        "co(2C_{4})",
        # TODO fig 7 line 4 column 4
        # TODO fig 7 line 4 column 5
        # TODO fig 7 line 5 column 1
        # TODO fig 7 line 5 column 2
        # TODO fig 7 line 5 column 3
        # TODO fig 7 line 5 column 4
        # TODO fig 7 line 5 column 5
        # TODO fig 7 line 6 column 1
        # TODO fig 7 line 6 column 2
        # TODO fig 7 line 6 column 3
        # TODO fig 7 line 6 column 4
        # TODO fig 7 line 6 column 5
        # TODO fig 7 line 7 column 1
        # TODO fig 7 line 7 column 2
        # TODO fig 7 line 7 column 3
        # TODO fig 7 line 7 column 4
        # TODO fig 7 line 7 column 5
        # TODO fig 7 line 8 column 1
        # TODO fig 7 line 8 column 2
        # TODO fig 7 line 8 column 3
        # TODO fig 7 line 8 column 4
        # TODO fig 7 line 8 column 5
        # TODO the graphs from figure 8 + their complements
        # TODO the graphs from figure 9 + their complements
        # TODO the graphs from figure 10 + their complements
    ]
)
@assign_class_id("gc_1289")
@lru_cache(maxsize=None)
def is_mock_threshold(graph: nx.Graph) -> bool:
    """
    A graph G is mock threshold if there is a vertex ordering v1, ... ,vn such that for every i the
    degree of vi in G[v1,...,vi] is 0, 1, i−2 or i−1.

    https://www.graphclasses.org/classes/gc_1289

    Complexity: O(m+n) < O(n^10) (naïve).

    :type graph: networkx.Graph
    :param graph:
    :return:
    """
    # see https://www.sciencedirect.com/science/article/pii/S0012365X18301286
    num_nodes = graph.order()
    degseq = degree_sequence(graph)
    # Every graph on at most five vertices except C_5 is mock threshold (Proposition 13)
    if num_nodes <= 5:
        return degseq != array('b', [2, 2, 2, 2, 2])

    # if 2 <= mindegree <= maxdegree <= n - 3, then the answer is no (Lemma 6)
    maxdegree, *_, mindegree = degseq
    if 2 <= mindegree <= maxdegree <= num_nodes - 3:
        return False

    # copy degrees
    degrees = dict(graph.degree)

    # retrieve all valid candidates
    candidates = {v for v, d in degrees.items() if d in {0, 1, num_nodes - 1, num_nodes - 2}}

    retrieved = set()
    while candidates:
        # retrieve all candidates
        retrieved.update(candidates)
        # decrement the degree of all neighbors of each candidate
        for v in candidates:
            for w in graph[v]:
                degrees[w] -= 1

        # update number of nodes and record the new candidates; discard those that have already
        # been retrieved
        num_nodes -= len(candidates)
        candidates = {
                         v for v, d in degrees.items() if d in {0, 1, num_nodes - 1, num_nodes - 2}
                     } - retrieved

    # the graph is empty iff all vertices were retrieved
    return len(retrieved) == graph.number_of_nodes()

    # NOTE: the following one-liner also works, but is slower as the graph's size increases
    # return empty_graph_by_removing_vertices(graph, vertex_has_degree_or_codegree_at_most_1)


@assign_fisc(["co(C_{4})", "co(C_{6})", "co(C_{7})", "co(C_{8})", "co(C_{5})", "3K_{1}"])
@assign_class_id("AUTO_2511")
@lru_cache(maxsize=None)
def is_p4_co_cycle_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is a co-cycle-free cograph.

    Complexity: O(m+n).

    @param graph:
    @return:
    """
    return is_cograph(graph) and is_co_forest(graph)


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
