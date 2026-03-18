"""
Anthony Labarre © 2023-2026

O(m+n) recognizers.

"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
import os
from array import array
from functools import lru_cache

# ----- Third-party imports -----------------------------------------------------------------------
import networkx as nx

# ----- My imports --------------------------------------------------------------------------------
from graph_recognition.misc_algo import (
    degree_sequence,
)
from graph_recognition.profitable_hereditary_n import (
    is_bipartite,
)
from graph_recognition.recognizers_utils import (
    assign_class_id,
    current_module_recognizers,
    cached_function,
)

# Cache imported functions that are not already cached --------------------------------------------
__functions_to_cache = [
    # nx.biconnected_components,  # DON'T: it returns a generator
    nx.is_biconnected,
    nx.is_k_edge_connected,
    nx.is_regular,
    nx.non_neighbors,
]
for i, function in enumerate(__functions_to_cache):
    __functions_to_cache[i] = cached_function(function)


# Functions ---------------------------------------------------------------------------------------
@assign_class_id("gc_1194")
@lru_cache(maxsize=None)
def is_planar_and_strongly_regular(graph: nx.Graph) -> bool:
    """
    A connected graph is in planar ∩ strongly regular iff it is one of K_{1}, K_{2}, K_{3}, K_{4},
    C_{4}, C_{5}, co(3K_{2}).

    https://www.graphclasses.org/classes/gc_1194

    :param graph:
    :return:
    """
    order = graph.number_of_nodes()
    if order == 1:
        return True

    size = graph.size()
    if order in {2, 3}:
        return order == size

    deg_seq = degree_sequence(graph)
    if order == 4:
        return deg_seq in (array('b', [3] * 4), array('b', [2] * 4))

    if order == 5:
        return deg_seq == array('b', [2] * 5)

    if order == 6:
        return deg_seq == array('b', [4] * 6)

    return False


@assign_class_id("gc_1099")
@lru_cache(maxsize=None)
def is_regular_with_k_at_least_3(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    degrees = set(degree_sequence(graph))
    return len(degrees) == 1 and degrees.pop() >= 3


@assign_class_id("gc_1105")
@lru_cache(maxsize=None)
def is_regular_with_k_at_least_6(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    degrees = set(degree_sequence(graph))
    return len(degrees) == 1 and degrees.pop() >= 6


@assign_class_id("gc_721")
@lru_cache(maxsize=None)
def is_2_tree(graph: nx.Graph) -> bool:
    """
    Returns true if G is a 2-tree, false otherwise.

    https://www.graphclasses.org/classes/gc_721.html

    :type graph: nx.Graph
    :param graph:
    :return:
    """
    # The algorithm runs in O(n) time and uses only the degree sequence of G.
    # See https://doi.org/10.1002/jgt.20302 , Theorem 1. Also available here:
    # https://cglab.ca/~morin/publications/gt/2trees.pdf
    degseq = degree_sequence(graph)
    n = len(degseq)
    n_2 = degseq.count(2)
    min_degree, max_degree = degseq[-1], degseq[0]

    # checking conditions a, b and c in Theorem 1; requiring that sum(degseq) = 4n - 6 = 2|E| is
    # equivalent to requiring that |E| = 2n - 3
    if graph.size() == 2 * n - 3 and max_degree <= n - 1 and min_degree == 2 and n_2 >= 2:
        # condition d: D is NOT of the form 2^{n-4} d^{4} for any d >= 5; for this to happen, we
        # would need len(D) >= 4
        if len(degseq) >= 4 and degseq[0] == 2 and degseq[-4] == degseq[-1] and degseq[-1] >= 5:
            return False

        # condition e: if all elements of D are even, then we must have n_2 >= n/3 + 1
        if all(e % 2 == 0 for e in degseq) and n_2 < n / 3 + 1:
            return False

        return True

    return False


@assign_class_id("gc_1151")
@lru_cache(maxsize=None)
def is_star_convex(graph: nx.Graph) -> bool:
    """
    A bipartite graph B = (X, Y, E) is star convex if a tree T=(X, F) can be defined such that T is
    a star and for every vertex y ∈ Y, the neighborhood of y induces a subtree in T.

    https://www.graphclasses.org/classes/gc_1151.html

    :param graph:
    :return:
    """
    try:
        left, right = nx.bipartite.sets(graph)
    except nx.exception.NetworkXError:  # graph is not bipartite
        return False
    except nx.exception.AmbiguousSolution:  # graph is disconnected
        # check bipartiteness
        if not is_bipartite(graph):
            return False

        # G is bipartite: nx.is_bipartite wrote 0s and 1s on vertices, retrieve
        # them to build the bipartition
        left = {n for n, d in graph.nodes(data=True) if d == 0}
        right = set(graph) - left

    # let X = left elements of partition and Y = right elements of partition
    # according to https://www.graphclasses.org/classes/refs1600.html#ref_1655 :
    #
    # Graph G = (X, Y, E) is star convex if and only if there exists vertex
    # x ∈ X such that (x, y) ∈ E for all y ∈ Y ∣ deg(y) ≥ 2. If there is such
    # x, then x can be center of star T. If there is no such x then for any
    # center z of star T there exists vertex y ∈ Y such that it is adjacent to
    # two leaves of T, but not adjacent to the center of T.

    # store all degree >= 2 nodes in Y
    nonleaves_in_Y = {v for v, d in graph.degree if d >= 2}.intersection(right)

    # find an x in X that is connected to all elements of nonleaves_in_Y
    if any(graph[x] == nonleaves_in_Y for x in left):
        return True

    # search Y and do the opposite direction
    # store all degree >= 2 nodes in X
    nonleaves_in_X = {v for v, d in graph.degree if d >= 2}.intersection(left)
    # find a y in Y that is connected to all elements of nonleaves_in_X
    if any(graph[y] == nonleaves_in_X for y in right):
        return True

    return False


# -------------------------------------------------------------------------------------------------
# The following classes are unlikely to have even a partial FISC: induced subgraphs are too local
# to capture their properties.
# -------------------------------------------------------------------------------------------------
@assign_class_id("gc_1362")
@lru_cache(maxsize=None)
def is_2_edge_connected(graph: nx.Graph) -> bool:
    """
    A graph is 2-edge-connected if it cannot be disconnected by removing less than 2 edges.

    https://www.graphclasses.org/classes/gc_1362

    @param graph:
    @return:
    """
    return nx.is_k_edge_connected(graph, 2)


@assign_class_id("gc_581")
@lru_cache(maxsize=None)
def is_reflexive(graph: nx.Graph) -> bool:
    """
    A graph is reflexive if for every node v there is an edge (v, v) (a loop).

    https://www.graphclasses.org/classes/gc_581

    @param graph:
    @return:
    """
    return nx.number_of_selfloops(graph) == graph.number_of_nodes()


# This code segment must always be at the END of a recognizer file --------------------------------
RECOGNIZERS = current_module_recognizers(
    ".".join(
        [
            os.path.basename(os.path.dirname(__file__)),
            os.path.basename(__file__).removesuffix(".py"),
        ]
    )
)
RECOGNIZERS.update(
    {
        "gc_1149": cached_function(nx.is_regular),
        "gc_771": cached_function(nx.is_biconnected),
    }
)
# -------------------------------------------------------------------------------------------------
