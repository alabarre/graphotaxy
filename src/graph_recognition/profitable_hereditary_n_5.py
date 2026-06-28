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
from pyroaring import BitMap

# ----- My imports --------------------------------------------------------------------------------
from graph_recognition.misc_algo import complement_as_adj_mat, co_connected_components, neighbors
from graph_recognition.profitable_hereditary_n import (
    is_p3_free, is_bipartite,
)
from graph_recognition.profitable_hereditary_n_2 import is_comparability
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

    nodes = BitMap(graph)
    adj = {v: neighbors(graph, v) for v in graph}

    def contains_p3(subset: BitMap) -> bool:
        """
        Returns True iff G[subset] contains an induced P3.
        """
        for center in subset:
            local_neighbors = adj[center] & subset

            if len(local_neighbors) < 2:
                continue

            for a in local_neighbors:
                witnesses = local_neighbors - adj[a]
                witnesses.discard(a)

                if witnesses:
                    return True

        return False

    # Enumerate P3s as u-w-v, where u and v are non-adjacent
    # and w is a common neighbor.
    for u, v in nx.non_edges(graph):
        for w in adj[u] & adj[v]:
            remaining = nodes - adj[u] - adj[v] - adj[w]
            remaining.discard(u)
            remaining.discard(v)
            remaining.discard(w)

            if contains_p3(remaining):
                return False

    return True


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
