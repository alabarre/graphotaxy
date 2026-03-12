"""Anthony Labarre © 2023-2026

This file contains recognizers for profitable hereditary classes, i.e. classes that admit a
forbidden induced subgraph characterization, but can be recognized with a faster-than-naïve
algorithm.

Recognizers in this file have running time O(n^5).

"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
import os
from functools import lru_cache
from typing import Hashable

# ----- Third-party imports -----------------------------------------------------------------------
import networkx as nx

# ----- My imports --------------------------------------------------------------------------------
from graph_recognition.misc_algo import (
    is_h_u_k2_free,
    enumerate_all_p4s,
    empty_graph_by_removing_vertices,
)
from graph_recognition.profitable_hereditary_n import (
    is_p3_free,
)
from graph_recognition.profitable_hereditary_n_2 import is_co_diamond_free
from graph_recognition.profitable_hereditary_n_3 import is_triangle_free
from graph_recognition.recognizers_utils import (
    current_module_recognizers,
    assign_class_id,
    assign_fisc,
)


# Recognizers -----------------------------------------------------------------
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
        for w in nx.common_neighbors(graph, u, v):
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

    Complexity: O(m^2n) <= O(n^5) (naïve)
    :type graph: networkx.Graph
    """
    return is_h_u_k2_free(graph, is_triangle_free)


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


@lru_cache(maxsize=None)
def vertex_is_superbrittle(graph: nx.Graph, v: Hashable) -> bool:
    """
    Returns True if either v is not the endpoint of any P_4 in graph, or it is not the midpoint of
    any P_4 in graph.

    :param graph:
    :param v:
    :return:
    """
    # since a P_4 that contains v is made of vertices at distance <= 3 from v, restrict our search
    # for P_4s to the subgraph induced by those vertices
    subgraph = graph.subgraph(nx.bfs_tree(graph, v, depth_limit=3))
    is_endpoint, is_midpoint = False, False
    for p4 in enumerate_all_p4s(subgraph):
        # extract endpoints, and check whether v is a midpoint or an endpoint of the current P_4
        endpoints = {v for v, deg in subgraph.subgraph(p4).degree if deg == 1}
        if v in endpoints:
            is_endpoint = True
        elif v in p4:
            is_midpoint = True

        # if at any point v is both, then it is not soft
        if is_endpoint and is_midpoint:
            return False

    return True




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
