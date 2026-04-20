"""
Anthony Labarre © 2023-2026

O(n^2) recognizers.

"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
import os
from array import array
from functools import lru_cache
from itertools import combinations

# ----- Third-party imports -----------------------------------------------------------------------
import networkx as nx
from networkx.utils.misc import arbitrary_element

# ----- My imports --------------------------------------------------------------------------------
from graph_recognition.misc_algo import (
    complement,
    number_of_common_neighbors,
    degree_sequence,
    is_connected, is_co_connected, co_connected_components, is_regular,
)
from graph_recognition.profitable_hereditary_n import (
    is_planar,
    is_cograph,
)
from graph_recognition.recognizers_n_10 import is_b_perfect_and_chordal
from graph_recognition.recognizers_utils import (
    assign_class_id,
    current_module_recognizers,
    cached_function,
)

# Cache imported functions that are not already cached --------------------------------------------
__functions_to_cache = [
    # nx.connected_components,  # DON'T: this is a generator
    nx.inverse_line_graph,
    nx.is_chordal,
    nx.is_regular,
    # nx.non_edges,  # DON'T: this is a generator
    nx.non_neighbors,
]


for i, function in enumerate(__functions_to_cache):
    __functions_to_cache[i] = cached_function(function)


# Recognizers -------------------------------------------------------------------------------------
@assign_class_id("gc_1181")
@lru_cache(maxsize=None)
def is_apex(graph: nx.Graph) -> bool:
    """
    A graph G is an apex graph if it contains a vertex v such that G−v is planar.

    https://www.graphclasses.org/classes/gc_1181

    :param graph:
    :return:
    """
    if is_planar(graph):
        return True

    # a planar graph on n vertices has at most 3n - 6 edges; by definition, if our graph is apex,
    # then removing a vertex must leave a graph with at most 3(n - 1) - 6 edges; since the degree
    # of a vertex in our graph is < n, if our graph has more than 3(n-1) - 6 + n - 1 = 4n - 10
    # edges, then it cannot be apex
    n = graph.number_of_nodes()
    if graph.size() > 4 * n - 10:
        return False

    # the removal of a higher degree node has a better chance of yielding a planar graph, so let's
    # try those first
    previous_nodes = set(graph.nodes)
    return any(
        is_planar(graph.subgraph(previous_nodes.difference({v})))
        for v in sorted(graph.nodes, key=graph.degree, reverse=True)
    )


# not an actual ISGCI class
@lru_cache(maxsize=None)
def has_star_cutset(graph: nx.Graph, _complement: bool = False) -> bool:
    """Returns true if graph has a star-cutset, false otherwise. If _complement
    is True, checks the property on the complement of the graph instead.

    https://doi.org/10.1016/0095-8956(85)90049-8

    :param _complement:
    :type graph: nx.Graph
    @param graph:
    @param _complement:
    """
    # See https://doi.org/10.1016/0095-8956(85)90049-8, Theorem 1 page 192: G
    # has a star-cutset if and only if at least one of two properties hold

    if _complement:
        # testing property 1: G has a vertex w such that the set of all the
        # vertices distinct from w and not adjacent to w induces a disconnected
        # subgraph
        # since we're in the complement, neighborhoods are in fact
        # co-neighborhoods, and subgraphs are induced by non-edges; it shouldn't
        # cost too much to compute complements here, so let's try
        neighbourhoods = dict()
        previous_nodes = set(graph.nodes)
        for w in graph.nodes:
            neighbourhoods[w] = set(nx.non_neighbors(graph, w))
            closed_n_w = neighbourhoods[w].union({w})
            if not is_connected(
                complement(graph.subgraph(previous_nodes.difference(closed_n_w)))
            ):
                return True

        # testing property 2: complement has at least two nonadjacent vertices,
        # which holds iff graph has at least one edge
        if not graph.size():
            return False

        # ... and it has adjacent vertices u, v such that v dominates u (i.e., each
        # neighbor of u is either v or a neighbor of v)
        for u, v in nx.non_edges(graph):
            if (
                neighbourhoods[u].difference({v}) <= neighbourhoods[v]
                or neighbourhoods[v].difference({u}) <= neighbourhoods[u]
            ):
                return True

        return False

    # testing property 1: G has a vertex w such that the set of all the vertices distinct from w
    # and not adjacent to w induces a disconnected subgraph
    if any(not is_connected(graph.subgraph(nx.non_neighbors(graph, w))) for w in graph):
        return True

    # testing property 2: G has at least two nonadjacent vertices:
    n = graph.number_of_nodes()
    if graph.size() == (n * (n - 1)) // 2:
        return False

    # ... and it has adjacent vertices u, v such that v dominates u (i.e., each
    # neighbor of u is either v or a neighbor of v)

    # caching neighborhoods is more efficient than repeated calls to dominates
    neighbourhoods = dict()
    for u, v in graph.edges:
        if u not in neighbourhoods:
            neighbourhoods[u] = set(graph[u])

        if v not in neighbourhoods:
            neighbourhoods[v] = set(graph[v])

        if (
            neighbourhoods[u] - {v} <= neighbourhoods[v]
            or neighbourhoods[v] - {u} <= neighbourhoods[u]
        ):
            return True

    return False


@assign_class_id("gc_1188")
@lru_cache(maxsize=None)
def is_edge_regular(graph: nx.Graph) -> bool:
    """
    An edge regular graph with parameters (n, k, λ) is a k-regular graph on n vertices, in which
    any two adjacent vertices have exactly λ common neighbors.

    https://graphclasses.org/classes/gc_1188

    :type graph: nx.Graph
    :param graph:
    """
    # Complexity: O(|E|)
    # the empty graph is trivially edge-regular; this check is also required to prevent a
    # StopIteration exception below
    if not graph.size():
        return True

    if not is_regular(graph):
        return False

    k = number_of_common_neighbors(graph, *arbitrary_element(graph.edges))

    # check that each pair of adjacent vertices has exactly k common neighbors
    neighbourhoods = dict()
    for u, v in graph.edges:
        if u not in neighbourhoods:
            neighbourhoods[u] = set(graph[u])
        if v not in neighbourhoods:
            neighbourhoods[v] = set(graph[v])

        if len(neighbourhoods[u].intersection(neighbourhoods[v])) != k:
            return False

    return True


@assign_class_id("gc_277")
@lru_cache(maxsize=None)
def is_unbreakable(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    # from https://onlinelibrary.wiley.com/doi/abs/10.1002/jgt.3190150403 p.351
    # Every unbreakable graph contains a P_4; therefore, a P_4-free graph is NOT unbreakable
    if is_cograph(graph):
        return False

    return not has_star_cutset(graph) and not has_star_cutset(graph, _complement=True)


@assign_class_id("gc_195")
@lru_cache(maxsize=None)
def is_bigeodetic(graph: nx.Graph) -> bool:
    """
    A graph is bigeodetic if every pair of vertices has at most 2 paths of minimum length between
    them.

    https://www.graphclasses.org/classes/gc_195.html

    @param graph:
    @return:
    """
    # naïve algorithm
    for u, v in combinations(graph, 2):
        try:
            for i, _ in enumerate(nx.all_shortest_paths(graph, u, v), 1):
                if i > 2:
                    return False

        except nx.exception.NetworkXNoPath:  # u, v mutually unreachable: skip
            pass

    return True


@assign_class_id("gc_270")
@lru_cache(maxsize=None)
def is_minimally_imperfect(graph: nx.Graph) -> bool:
    """
    A graph is minimally imperfect if it is not perfect and every induced subgraph is perfect.
    These are precisely the odd (anti)-holes.

    https://www.graphclasses.org/classes/gc_270.html

    @type graph: nx.Graph
    @param graph:
    @return:
    """
    n = graph.size()
    if n % 2:
        if (is_connected(graph) and degree_sequence(graph) == array('b', [2] * n)) or (
            is_co_connected(graph) and degree_sequence(graph) == array('Q', [n - 3] * n)
        ):
            return True

    return False


# -------------------------------------------------------------------------------------------------
# The following recognizers call another recognizer on the complement of the input graph. Since
# building the complement can be time- and memory-consuming on large instances, and since
# recognizers are loaded in the order in which they appear in a recognizer file, those recognizers
# should stay at the end of the file in the hope that they are not actually needed until we figure
# out a way to bypass the computation of the complement.
# -------------------------------------------------------------------------------------------------
@assign_class_id("AUTO_3856")
@lru_cache(maxsize=None)
def is_co_b_perfect_and_chordal(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_3856.html

    @param graph:
    @return:
    """
    # iterate over co-connected components instead of complementing the whole graph, in the hope
    # that we can thereby stop early
    # note: complement_as_adj_mat not usable yet: a call to is_cograph is involved, which does not
    # accept anything other than a networkx.Graph
    return all(
        is_b_perfect_and_chordal(complement(graph.subgraph(cc)))
        for cc in co_connected_components(graph)
    )


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
