"""
Anthony Labarre © 2023-2026

Algorithms related to domination in graphs.

"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
from functools import lru_cache
from itertools import combinations
from typing import Any, Iterable

# ----- Third-party imports -----------------------------------------------------------------------
from networkx import Graph
from pyroaring import BitMap

# ----- My imports --------------------------------------------------------------------------------
from graph_recognition.adjacency_matrix import HalfAdjacencyMatrix
from graph_recognition.misc_algo import degree_sequence, number_of_nodes, number_of_edges, neighbors


@lru_cache(maxsize=None)
def dominates(graph: Graph | HalfAdjacencyMatrix, a: Any, b: Any) -> bool:
    """
    Returns True iff a dominates b, i.e. if the neighborhood of a contains the neighborhood of
    b (excluding a).

    :param b:
    :param a:
    :type graph: Graph
    """
    return neighbors(graph, b) - BitMap({a}) <= neighbors(graph, a)


@lru_cache(maxsize=None)
def is_dominating_set(graph: Graph, vset: Iterable) -> bool:
    """
    Returns True if vset is a dominating set for graph, False otherwise.

    :param graph:
    :param vset:
    :return:
    """
    # vset is a dominating set for graph iff the union of vset's elements and their neighborhoods
    # is the whole vertex set
    return set.union(*({v}.union(graph[v]) for v in vset)) == set(graph)


@lru_cache(maxsize=None)
def has_dominating_set_of_size_at_most_2(graph: Graph) -> bool:
    """
    Return True if graph has a dominating set of size <= 2, False otherwise.

    :param graph:
    :return:
    """
    # if there is a dominating vertex, say yes
    if degree_sequence(graph)[0] == number_of_nodes(graph) - 1:
        return True

    # if there is a pair of dominating vertices, say yes
    return any(is_dominating_set(graph, pair) for pair in combinations(graph, 2))


@lru_cache(maxsize=None)
def has_dominating_triangle_or_p3(graph: Graph) -> bool:
    """
    Return True if graph has a dominating set of size 3 that induces a K_{3} or a P_{3}, False
    otherwise.

    :param graph:
    :return:
    """
    # a triplet induces a P_{3} or a K_{3} if it has at least two edges
    return any(
        is_dominating_set(graph, triplet) for triplet in combinations(graph, 3)
        if number_of_edges(graph.subgraph(triplet)) >= 2
    )
