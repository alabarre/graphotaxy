"""
Anthony Labarre © 2023-2026

Algorithms related to domination in graphs.

"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
from functools import lru_cache
from itertools import combinations
from typing import Any

# ----- Third-party imports -----------------------------------------------------------------------
from networkx import Graph

# ----- My imports --------------------------------------------------------------------------------
from graph_recognition.misc_algo import degree_sequence


@lru_cache(maxsize=None)
def dominates(graph: Graph, a: Any, b: Any) -> bool:
    """
    Returns True iff a dominates b, i.e. if the neighborhood of a contains the neighborhood of
    b (excluding a).

    :param b:
    :param a:
    :type graph: Graph
    """
    return set(graph[b]) - {a} <= set(graph[a])


@lru_cache(maxsize=None)
def has_dominating_set_of_size_at_most_2(graph: Graph) -> bool:
    """
    Return True if graph has a dominating set of size <= 2, False otherwise.

    :param graph:
    :return:
    """
    # if there is a dominating vertex, say yes
    if degree_sequence(graph)[0] == graph.number_of_nodes() - 1:
        return True

    # if there is a pair of dominating vertices, say yes
    all_nodes = set(graph)
    return any(
        # x, y is a dominating pair if {x, y} U N(x) U N(y) = G.nodes
        {x}.union({y}).union(graph[x]).union(graph[y]) == all_nodes
        for x, y in combinations(graph, 2)
    )
