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
from graph_recognition.profitable_hereditary_n import (
    is_p3_free,
)
from graph_recognition.profitable_hereditary_n_2 import is_co_diamond_free
from graph_recognition.recognizers_utils import (
    current_module_recognizers,
    assign_class_id,
    assign_fisc,
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

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["K_{2} U K_{3}"])
    # faster than:
    # return is_h_u_k2_free(graph, is_triangle_free)


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
