"""
Anthony Labarre © 2023-2026

This file contains recognizers for profitable hereditary classes, i.e. classes that admit a
forbidden induced subgraph characterization, but can be recognized with a faster-than-naïve
algorithm.

Recognizers in this file have running time O(n^5).

"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
import os
from functools import lru_cache

# ----- Third-party imports -----------------------------------------------------------------------
import networkx as nx

# ----- My imports --------------------------------------------------------------------------------
from graph_recognition.misc_algo import common_neighbors, complement_as_adj_mat, co_connected_components
from graph_recognition.profitable_hereditary_n import (
    is_p3_free, is_bipartite,
)
from graph_recognition.profitable_hereditary_n_2 import is_co_diamond_free, is_comparability
from graph_recognition.recognizers_utils import (
    current_module_recognizers,
    assign_class_id,
    assign_fisc, assign_inherited_fisc,
)
from graph_recognition.subgraphs import is_h_free


# Recognizers -------------------------------------------------------------------------------------
@assign_fisc(["2P_{3}"])
@assign_class_id("gc_931")
@lru_cache(maxsize=None)
def is_2p3_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is 2P_{3}-free.

    See https://www.graphclasses.org/classes/gc_931

    Complexity: O(n^3(m+n)) = O(n^5) < O(n^6) (naïve)

    :type graph: networkx.Graph
    """
    if is_p3_free(graph):
        return True

    # iterate over P_{3}'s in graph by iterating over all non-edges, and in turn iterating over all
    # common neighbors of those non-edges
    all_nodes = set(graph.nodes)
    for u, v in nx.non_edges(graph):
        for w in common_neighbors(graph, u, v):
            #  now check whether removing u, v, w and their neighbors yields a P_{3}-free graph
            if not is_p3_free(
                    graph.subgraph(
                        all_nodes
                        - {u, v, w}.union(
                            graph.neighbors(u), graph.neighbors(v), graph.neighbors(w)
                        )
                    )
            ):
                return False

    return True


@assign_fisc(["K_{2} U K_{3}"])
@assign_class_id("gc_456")
@lru_cache(maxsize=None)
def is_k2_u_k3_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is K_{2} U K_{3}-free.

    See https://www.graphclasses.org/classes/gc_456

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    # note: cannot move to fisc_based_recognizers due to circular import issues
    return is_h_free(graph, ["K_{2} U K_{3}"])
    # faster than:
    # return is_h_u_k2_free(graph, is_triangle_free)


@assign_inherited_fisc()
@assign_class_id("AUTO_1482")
@lru_cache(maxsize=None)
def is_auto_1482(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{2} U K_{3}, co-diamond)-free.

    See https://www.graphclasses.org/classes/AUTO_1482

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_co_diamond_free(graph) and is_k2_u_k3_free(graph)


# @assign_inherited_fisc() # DON'T: results would be wrong (combinations of "or", not "and")
@assign_class_id("gc_148")
@lru_cache(maxsize=None)
def is_comparability_or_co_comparability(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_148

    @param graph:
    @return:
    """
    return is_comparability(graph) or is_co_comparability(graph)


@assign_fisc(
    [
        "C_{6}",  # complement of "co(C_{6})",
        "C_{7}",  # complement of "co(C_{7})",
        "C_{8}",  # complement of "co(C_{8})",
        "T_{2}",  # complement of "co(T_{2})",
        "X_{2}",  # complement of "co(X_{2})",
        "X_{3}",  # complement of "co(X_{3})",
        "X_{30}",  # complement of "co(X_{30})",
        "X_{31}",  # complement of "co(X_{31})",
        "X_{32}",  # complement of "co(X_{32})",
        "X_{33}",  # complement of "co(X_{33})",
        "X_{34}",  # complement of "co(X_{34})",
        "X_{35}",  # complement of "co(X_{35})",
        "X_{36}",  # complement of "co(X_{36})",
        "co(C_{5})",  # complement of "C_{5}",
        "co(C_{7})",  # complement of "C_{7}",
    ]
)
@assign_class_id("gc_147")
@lru_cache(maxsize=None)
def is_co_comparability(graph: nx.Graph) -> bool:
    """
    A graph is a co-comparability if it is the intersection graph of curves from a line to a parallel
    line.

    https://www.graphclasses.org/classes/gc_147.html

    @param graph:
    @return:
    """
    '''
    if not is_h_free(graph, [
        "C_{6}",  # complement of "co(C_{6})",
        "C_{7}",  # complement of "co(C_{7})",
        "C_{8}",  # complement of "co(C_{8})",
        "T_{2}",  # complement of "co(T_{2})",
        "X_{2}",  # complement of "co(X_{2})",
        "X_{3}",  # complement of "co(X_{3})",
        "X_{30}",  # complement of "co(X_{30})",
        "X_{31}",  # complement of "co(X_{31})",
        "X_{32}",  # complement of "co(X_{32})",
        "X_{33}",  # complement of "co(X_{33})",
        "X_{34}",  # complement of "co(X_{34})",
        "X_{35}",  # complement of "co(X_{35})",
        "X_{36}",  # complement of "co(X_{36})",
        "co(C_{5})",  # complement of "C_{5}",
        "co(C_{7})",  # complement of "C_{7}",
    ]):
        return False
    '''
    if not is_h_free(graph, ["C_{5}"]):
        return False

    # iterate over co-connected components instead of complementing the whole graph, in the hope
    # that we can thereby stop early
    return all(
        is_comparability(complement_as_adj_mat(graph, cc)) for cc in co_connected_components(graph)
    )

@assign_inherited_fisc()
@assign_class_id("gc_23")
@lru_cache(maxsize=None)
def is_permutation(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_comparability(graph) and is_co_comparability(graph)


@assign_inherited_fisc()
@assign_class_id("gc_81")
@lru_cache(maxsize=None)
def is_bipartite_permutation(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_bipartite(graph) and is_permutation(graph)


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
