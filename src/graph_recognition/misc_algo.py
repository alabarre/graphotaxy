"""
Anthony Labarre © 2023-2026

Miscellaneous useful algorithms.

"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
from array import array, typecodes
from collections import defaultdict
from collections.abc import Hashable
from functools import lru_cache
from itertools import combinations, product
from math import inf
from typing import Any, Callable, Iterator, Generator, Dict, Iterable

# ----- Third-party imports -----------------------------------------------------------------------
import networkx as nx
from networkx.utils import arbitrary_element
from pyroaring import BitMap
from typing_extensions import DefaultDict

# ----- My imports --------------------------------------------------------------------------------
from graph_recognition.adjacency_matrix import HalfAdjacencyMatrix
from graph_recognition.recognizers_utils import cached_function
from graph_recognition.undirected_graph import UndirectedGraph

# Cache imported functions that are not already cached --------------------------------------------
__functions_to_cache = [
    nx.bfs_tree,
    # nx.common_neighbors,         # DON'T: this returns a generator expression
    nx.is_chordal,
    nx.is_connected,
    nx.non_neighbors,
    # nx.non_edges,          # DON'T: this is a generator
]
for i, function in enumerate(__functions_to_cache):
    __functions_to_cache[i] = cached_function(function)

# Global variables --------------------------------------------------------------------------------
NUMERIC_TYPECODES = typecodes.replace("uw", "")


# Functions ---------------------------------------------------------------------------------------
@lru_cache(maxsize=None)
def all_pairs_shortest_path_length(graph: nx.Graph, cutoff: int | None = None) -> Dict[tuple, int]:
    """
    Computes the shortest path lengths between all nodes in `G`. This is exactly what networkx
    offers, except we return a dictionary instead of an iterator so we can cache the results.

    :param graph:
    :param cutoff:
    :return:
    """
    return dict(nx.all_pairs_shortest_path_length(graph, cutoff))


@lru_cache(maxsize=None)
def degree_sequence(graph: nx.Graph | HalfAdjacencyMatrix) -> array:
    """
    Returns the degree sequence of a graph, i.e. the list of all degrees sorted decreasingly.

    >>> import networkx; degree_sequence(networkx.empty_graph(5))
    array('b', [0, 0, 0, 0, 0])
    >>> import networkx; degree_sequence(networkx.complete_graph(5))
    array('b', [4, 4, 4, 4, 4])

    :type graph: networkx.Graph
    :param graph:
    :return:
    """
    # if graph is edgeless, then graph.degree is empty, so I need to build the sequence of zeroes
    # myself
    if not number_of_edges(graph):
        return array('b', [0] * number_of_nodes(graph))

    degseq = sorted((d for _, d in graph.degree), reverse=True)

    # return convertex array with smallest typecode
    for tc in NUMERIC_TYPECODES:
        try:
            return array(tc, degseq)
        except OverflowError:
            pass

    raise OverflowError  # no type was big enough for the elements of the degree sequence


@lru_cache(maxsize=None)
def graph_density(graph: nx.Graph | HalfAdjacencyMatrix) -> float:
    """
    Returns the ratio "number of edges" / "number of possible edges".

    :param graph:
    :return:
    """
    n = number_of_nodes(graph)
    return 2 * number_of_edges(graph) / (n * (n - 1))


# ----- Helpers for recognizers -------------------------------------------------------------------
# The following functions behave exactly as recognizers, except they do not correspond to classes
# in ISGCI (hence the lack of @assign_class_id or @assign_fisc).
@lru_cache(maxsize=None)
def is_complete(graph: nx.Graph) -> bool:
    """
    Returns True if graph is complete, False otherwise.

    :type graph: networkx.Graph
    :param graph:
    :return:
    """
    n = number_of_nodes(graph)
    return number_of_edges(graph) == (n * (n - 1)) // 2


@lru_cache(maxsize=None)
def is_h_u_k1_free(graph: nx.Graph | HalfAdjacencyMatrix, recognizer_for_h: Callable) -> bool:
    """
    Returns True if graph is (H U K_{1})-free, and False otherwise. Requires a recognizer for
    H-free graphs.

    Use this function with caution: unless recognizer_for_h is much faster than the naïve approach,
    a direct call to GSS is usually much faster for large graphs.

    @param graph:
    @param recognizer_for_h:
    @return:
    """
    # G is (H U K_{1})-free iff G - ({u} U N(u)) is H-free for every vertex v; this is equivalent
    # to verifying whether the subgraph of G induced by the non-neighbors of v is H-free for all v
    return all(recognizer_for_h(graph.subgraph(non_neighbors(graph, v))) for v in graph)


@lru_cache(maxsize=None)
def is_h_u_k2_free(graph: nx.Graph, recognizer_for_h: Callable) -> bool:
    """
    Returns True if graph is (H U K_{2})-free, and False otherwise. Requires a recognizer for
    H-free graphs.

    @param graph:
    @param recognizer_for_h:
    @return:
    """
    # G is (H U K_{2})-free iff G - ({u, v} U N(u) U N(v)) is H-free for every edge {u, v};
    # this is equivalent to verifying whether the subgraph of G induced by the vertices that are
    # adjacent neither to u nor to v is H-free for every edge {u, v}
    return all(
        recognizer_for_h(graph.subgraph(non_neighbors(graph, u) & non_neighbors(graph, v)))
        for u, v in graph.edges
    )


@lru_cache(maxsize=None)
def is_h_u_2k1_free(graph: nx.Graph, recognizer_for_h: Callable) -> bool:
    """
    Returns True if graph is (H U 2K_{1})-free, and False otherwise. Requires a recognizer for
    H-free graphs.

    @param graph:
    @param recognizer_for_h:
    @return:
    """
    # G is (H U 2K_{1})-free iff G - ({u, v} U N(u) U N(v)) is H-free for every non-edge {u, v}
    # this is equivalent to verifying whether the subgraph of G induced by the vertices that are
    # adjacent neither to u nor to v is H-free for every non-edge {u, v}
    return all(
        recognizer_for_h(graph.subgraph(non_neighbors(graph, u) & non_neighbors(graph, v)))
        for u, v in nx.non_edges(graph)
    )


@lru_cache(maxsize=None)
def complement(graph: nx.Graph) -> nx.Graph:
    """
    Returns the complement of the graph. Only exists so the result can be cached.

    :param graph:
    :type graph: networkx.Graph
    :return:
    """
    compl = graph.__class__()
    compl.add_nodes_from(graph)
    compl.add_edges_from(nx.non_edges(graph))
    return compl


@lru_cache(maxsize=None)
def complement_as_adj_mat(graph: nx.Graph, nodes=None) -> HalfAdjacencyMatrix:
    """
    Returns the complement of the graph as an adjacency matrix. If nodes is not None, then
    complementation is restricted to the subgraph induced by nodes.

    :param nodes:
    :param graph:
    :type graph: networkx.Graph
    :return:
    """
    compl = HalfAdjacencyMatrix()
    if nodes is None:
        compl.add_nodes_from(graph)
        compl.add_edges_from(nx.non_edges(graph))
    else:
        compl.add_nodes_from(nodes)
        compl.add_edges_from((u, v) for u, v in combinations(nodes, 2) if not graph.has_edge(u, v))
    return compl


@lru_cache(maxsize=None)
def common_neighbors(graph: nx.Graph | HalfAdjacencyMatrix, u: Any, v: Any):
    """
    Returns the common neighbors of u and v in graph.

    :param graph:
    :param u:
    :param v:
    :return:
    """
    return nx.common_neighbors(graph, u, v)


@lru_cache(maxsize=None)
def number_of_common_neighbors(graph: nx.Graph, u: Any, v: Any) -> int:
    """
    Returns the number of common neighbors of u and v in graph.

    :param graph:
    :param u:
    :param v:
    :return:
    """
    return sum(1 for _ in common_neighbors(graph, u, v))


@lru_cache(maxsize=None)
def is_regular(graph: nx.Graph) -> bool:
    """
    Returns True if graph is regular.

    Networkx have their own function, but this one is cached and expected to be faster. Since we
    most likely need to compute the degree sequence of our graph, chances are we can often answer
    the question in O(1) time.

    :param graph:
    :return:
    """
    # we follow networkx's convention to be consistent
    if len(graph) == 0:
        raise nx.NetworkXPointlessConcept("Graph has no nodes.")

    ds = degree_sequence(graph)
    return ds[0] == ds[-1]


# Functions for recognizing a graph by repeatedly removing edges ----------------------------------
@lru_cache(maxsize=None)
def empty_graph_by_removing_edges_and_incident_edges(graph: nx.Graph, criterion: Callable) -> bool:
    """
    Empties the graph by repeatedly removing edges that satisfy the criterion. Removing an edge
    {u, v} entails removing {u, v} as well as all other edges incident to u or v. Returns True if
    all edges are deleted, False otherwise.

    :param criterion:
    :type graph: networkx.Graph
    :param graph:
    :return:
    """
    nodes = set(graph)
    while graph.edges:
        # find an edge that matches the criterion
        for edge in graph.edges:
            if criterion(graph, edge):
                nodes -= set(edge)
                graph = graph.subgraph(nodes)
                break

        else:  # no satisfying edge was found, quit early
            return False

    # property is satisfied to the end, undo removals and return True
    return True


# Functions for recognizing a graph by repeatedly removing vertices -------------------------------
@lru_cache(maxsize=None)
def empty_graph_by_removing_vertices(graph: nx.Graph, criterion: Callable) -> bool:
    """
    Empties the graph by repeatedly removing vertices that satisfy the criterion. Returns True if
    all vertices are deleted, False otherwise.

    :param criterion:
    :type graph: networkx.Graph
    :param graph:
    :return:
    """
    nodes = set(graph)
    new_graph = graph.subgraph(nodes)
    while nodes:
        for v in new_graph:
            if criterion(new_graph, v):
                nodes.remove(v)
                new_graph = new_graph.subgraph(nodes)
                break

        else:  # no satisfying vertex was found, quit early
            return False

    # graph was successfully emptied
    return True


# Recognizers -------------------------------------------------------------------------------------
# The following recognizers were moved here solely to avoid circular import issues.
# --------------------------------------------------------------------------------------------- end
@lru_cache(maxsize=None)
def is_connected(graph: nx.Graph | HalfAdjacencyMatrix) -> bool:
    """
    Returns True iff graph is connected. I need my own version, because it will be called on
    subgraphs that might be null (no vertices and no edges) and networkx's version crashes on
    those. I'm deciding that a null graph is NOT connected.

    :type graph: nx.Graph
    :param graph:
    :return:
    """
    n = len(graph)
    return n and len(next(connected_components(graph))) == n


@lru_cache(maxsize=None)
def plain_co_bfs(graph: nx.Graph, n: int, source: Hashable) -> set:
    """
    A fast BFS node generator on the complement of the graph. Simple adaptation of networkx's
    _plain_bfs function to work on non-edges rather than edges.
    """
    # other changes:
    # - replaced lists with sets since we only care about accessibility, not order
    # - comprehension for building the next level, so we can use updates instead of many adds
    # - slight modification to make it compatible with my HalfAdjacencyMatrix class
    seen = {source}
    nextlevel = {source}

    while nextlevel:
        thislevel = nextlevel
        nextlevel = set()
        for v in thislevel:
            new_non_neighbors = {w for w in non_neighbors(graph, v) if w not in seen}
            seen.update(new_non_neighbors)
            nextlevel.update(new_non_neighbors)
            if len(seen) == n:
                return seen

    return seen


@lru_cache(maxsize=None)
def is_co_connected(graph: nx.Graph) -> bool:
    """
    Returns True iff the complement of the graph is connected.

    :type graph: nx.Graph
    :param graph:
    :return:
    """
    n = len(graph)
    if n == 0:
        return False

    return sum(1 for _ in plain_co_bfs(graph, n, arbitrary_element(graph))) == n


# @lru_cache(maxsize=None)  # don't: it's a generator
def co_connected_components(graph: nx.Graph) -> Generator:
    """
    Generate the connected components of the complement of the graph. Simple adaptation of
    networkx's connected_components function.

    :param graph:
    :return:
    """
    seen = set()
    n = len(graph)
    for v in graph:
        if v not in seen:
            c = plain_co_bfs(graph, n - len(seen), v)
            seen.update(c)
            # return result as frozenset so functions that rely on co-connected components can
            # cache what they compute
            yield frozenset(c)


@lru_cache(maxsize=None)
def is_even_clique_free(graph: nx.Graph, k: int) -> bool:
    """
    Returns True iff graph has no clique of size k, for k even.

    @param graph:
    @param k:
    @return:
    """
    assert not k % 2, "k must be even"

    if must_contain_a_clique_of_size(graph, k):
        return False

    # since vertices in a k-clique have degree k-1, restrict our search to vertices of degree at
    # least k-1; don't create a useless copy if all vertices already have degree > k, however
    ds = degree_sequence(graph)
    if ds and ds[-1] <= k:
        graph = graph.subgraph(v for v, d in graph.degree if d >= k - 1)
        # check criterion again, since graph has changed (we can afford it, it takes time O(1))
        if must_contain_a_clique_of_size(graph, k):
            return False

    # if k is even, then selecting any combination of k/2 edges gives us a set of k vertices, and
    # we then check that they induce the right amount of edges; we might then gain a little bit of
    # time as opposed to blindly trying every k-subset of vertices, since we only select pairs of
    # vertices that are connected
    clique_num_edges = (k ** 2 - k) // 2
    return all(
        number_of_edges(graph.subgraph(sum(edges, ()))) != clique_num_edges
        for edges in combinations(graph.edges, k // 2)
    )


@lru_cache(maxsize=None)
def is_odd_clique_free(graph: nx.Graph, k: int) -> bool:
    """
    Returns True iff graph has no clique of size k, for k even.

    @param graph:
    @param k:
    @return:
    """
    assert k % 2, "k must be odd"

    if must_contain_a_clique_of_size(graph, k):
        return False

    # since vertices in a k-clique have degree k-1, restrict our search to vertices of degree at
    # least k-1; don't create a useless copy if all vertices already have degree > k, however
    ds = degree_sequence(graph)
    if ds and ds[-1] <= k:
        graph = graph.subgraph(v for v, d in graph.degree if d > k)
        # check criterion again, since graph has changed (we can afford it, it takes time O(1))
        if must_contain_a_clique_of_size(graph, k):
            return False

    # graph is k-clique-free iff the neighborhood of each vertex of degree >= k-1 is
    # (k-1)-clique-free
    return all(
        is_even_clique_free(graph.subgraph(graph[v]), k - 1)
        for v, d in graph.degree
        if d >= k - 1
    )


@lru_cache(maxsize=None)
def is_even_co_clique_free(graph: nx.Graph, k: int) -> bool:
    """
    Returns True iff graph has no independent set of size k, for k even.

    @param graph:
    @param k:
    @return:
    """
    assert not k % 2, "k must be even"

    if must_contain_an_independent_set_of_size(graph, k):
        return False

    # if k is even, then selecting any combination of k/2 non-edges gives us a set of k vertices,
    # and we then check that they induce 0 edges; we might then gain a little bit of time as
    # opposed to blindly trying every k-subset of vertices, since we only select pairs of
    # vertices that are independent (but not necessarily all pairwise)
    return k > number_of_nodes(graph) or all(
        number_of_nodes(subgraph) != k or number_of_edges(subgraph) != 0
        for subgraph in map(
            # we can't use graph.edge_subgraph here, since nonedges always induce an empty graph,
            # so we must use graph.subgraph with the endpoints of all nonedges
            lambda nonedges: graph.subgraph(sum(nonedges, ())),
            combinations(nx.non_edges(graph), k // 2),
        )
    )


@lru_cache(maxsize=None)
def must_contain_a_clique_of_size(graph: nx.Graph, k: int) -> bool:
    """
    Returns True if graph contains a clique of size k, False if unsure.

    Complexity: O(1)

    @param graph:
    @param k:
    @return:
    """
    # Turan's theorem: a K_{r+1}-free graph cannot have more than (1 - 1/r)n²/2 edges
    if number_of_edges(graph) > ((1 - 1 / (k - 1)) * number_of_nodes(graph) ** 2) / 2:
        return True

    return False


@lru_cache(maxsize=None)
def must_contain_an_independent_set_of_size(graph: nx.Graph, k: int) -> bool:
    """
    Returns True if graph contains an independent set of size k, False if unsure.

    @param graph:
    @param k:
    @return:
    """
    # if graph is bipartite, then either class is an independent set; return True if either set has
    # size at least k
    try:
        # note: calling is_bipartite would raise a circular import error, and we need the sets
        # anyway, so better call bipartite.sets directly
        # to avoid raising a networkx.exception.AmbiguousSolution, let's work on the graph's
        # components
        if any(
                len(part) >= k
                for subgraph in map(graph.subgraph, nx.connected_components(graph))
                for part in nx.bipartite.sets(subgraph)
        ):
            return True

    except nx.NetworkXError:  # raised if the input graph is not bipartite
        pass

    return False


@lru_cache(maxsize=None)
def is_odd_co_clique_free(graph: nx.Graph, k: int) -> bool:
    """
    Returns True iff graph has no independent set of size k, for k odd.

    @param graph:
    @param k:
    @return:
    """
    assert k % 2, "k must be odd"

    if must_contain_an_independent_set_of_size(graph, k):
        return False

    # graph is k-K_{1}-free iff the non-neighborhood of each vertex contains k-1 independent
    # vertices; we only examine vertices with at least k-1 non-neighbors, or equivalently, vertices
    # of degree at most n-1-(k-1) = n-k
    n = number_of_nodes(graph)
    return all(
        is_even_co_clique_free(graph.subgraph(non_neighbors(graph, v)), k - 1)
        for v, d in graph.degree
        if d <= n - k
    )


def explicit_triangles(graph: nx.Graph) -> Iterator[set]:
    """
    Generates all triangles in a graph as triplets of vertices.

    Complexity: O(n^3).

    @param graph:
    @return:
    """
    for u, v in graph.edges:
        for w in nx.common_neighbors(graph, u, v):
            yield {u, v, w}


def enumerate_all_p4s(graph: nx.Graph) -> Generator:
    """
    Generates all induced paths of length 4 in a graph as sets of 4 vertices.

    :param graph:
    :return:
    """
    # iterate over every edge {u, v}, and examine all combinations of neighbors of u and v
    for u, v in graph.edges():
        # keep only neighbors of u that are not neighbors of v (and conversely) to reduce the
        # number of elements in the product below
        n_u = neighbors(graph, u) - neighbors(graph, v)
        n_v = neighbors(graph, v) - neighbors(graph, u)
        n_u.remove(v)
        n_v.remove(u)
        for x, y in product(n_u, n_v):
            # by construction, all vertices in p4_candidates are distinct, so no need to check
            # its length
            p4_candidates = {x, u, y, v}
            if sum(graph.has_edge(a, b) for a, b in combinations(p4_candidates, 2)) == 3:
                yield p4_candidates


def twins(graph: nx.Graph) -> DefaultDict[Any, set]:
    """
    Returns a partition of the vertices into twins. Twins are vertices whose neighborhoods
    coincide.

    >>> import networkx as nx  # noqa
    >>> G = nx.cycle_graph(4)
    >>> sorted(((v, sorted(equivs)) for v, equivs in twins(G).items()))  # noqa
    [(0, [2]), (1, [3]), (2, [0]), (3, [1])]

    :param graph:
    :return:
    """
    neighborhoods = defaultdict(set)
    twin_partition = defaultdict(set)
    for v in graph:
        if v not in neighborhoods:
            neighborhoods[v] = set(graph[v])
        for w in set(neighborhoods) - {v}:
            if neighborhoods[v] == neighborhoods[w]:
                twin_partition[v].add(w)
                twin_partition[w].add(v)

    return twin_partition


def find_twin_in(nbunch: Iterable, graph: nx.Graph, v: Hashable) -> Hashable | None:
    """
    Returns a twin of v in graph, i.e., a vertex w != v with the same neighborhood as v, or None if
    none exists.

    :param nbunch:
    :param graph:
    :param v:
    :return:
    """
    for w in nbunch:  # noqa
        if v != w and graph[w] == graph[v]:
            return w


@lru_cache(maxsize=None)
def all_vertices_are_int(graph: nx.Graph) -> bool:
    """
    Returns True if all vertices are integer, False otherwise.

    :param graph:
    :return:
    """
    return all(isinstance(v, int) for v in graph)


@lru_cache(maxsize=None)
def maximal_independent_set(graph: nx.Graph, cutoff: int = inf) -> set:
    """
    Returns a maximal (not maximum) independent set for the given graph. If cutoff is specified,
    stops as soon as the size of the set reaches it.

    Networkx has its own function for doing that, but I didn't want randomness. Moreover, for my
    purposes, a cutoff at 7 will usually be enough, and their function doesn't provide that
    capability.

    :param graph:
    :param cutoff:
    :return:
    """
    retval = set()
    graph_copy = UndirectedGraph()
    graph_copy.add_nodes_from(graph)
    graph_copy.add_edges_from(graph.edges())
    while graph_copy and len(retval) < cutoff:
        # select a vertex with minimum degree
        v = min(graph_copy, key=graph_copy.degree)
        retval.add(v)
        # remove the closed neighborhood of v from the graph
        graph_copy.remove_nodes_from({v}.union(graph_copy[v]))

    return retval


# Algorithms that needed to be reimplemented in order to be compatible with HalfAdjacencyMatrix ---

@lru_cache(maxsize=None)
def plain_bfs(graph: nx.Graph | HalfAdjacencyMatrix, n: int, source: Hashable) -> set:
    """
    A fast BFS node generator. Simple adaptation of networkx's _plain_bfs function that avoids
    graph._adj, on non-edges rather than edges.
    """
    # other changes:
    # - replaced lists with sets since we only care about accessibility, not order
    # - comprehension for building the next level, so we can use updates instead of many adds
    # - slight modification to make it compatible with my HalfAdjacencyMatrix class
    seen = {source}
    nextlevel = {source}

    while nextlevel:
        thislevel = nextlevel
        nextlevel = set()
        for v in thislevel:
            new_neighbors = {w for w in neighbors(graph, v) if w not in seen}
            seen.update(new_neighbors)
            nextlevel.update(new_neighbors)
            if len(seen) == n:
                return seen

    return seen


def connected_components(graph: nx.Graph | HalfAdjacencyMatrix):
    """
    Reimplementation of nx.connected_components to ensure compatibility with HalfAdjacencyMatrix.

    :param graph:
    :return:
    """
    # simple adaptation of nx.connected_components
    seen = set()
    n = len(graph)
    for v in graph:
        if v not in seen:
            c = plain_bfs(graph, n - len(seen), v)
            seen.update(c)
            yield c


@lru_cache(maxsize=None)
def neighbors(graph: nx.Graph | HalfAdjacencyMatrix, x: Any) -> BitMap:
    """
    Returns the neighbors of x in graph as a BitMap.

    :param graph:
    :param x:
    :return:
    """
    return BitMap(graph[x])


@lru_cache(maxsize=None)
def non_neighbors(graph: nx.Graph | HalfAdjacencyMatrix, x: Any) -> set | BitMap:
    """
    Returns the non-neighbors of x in graph as a BitMap.

    :param graph:
    :param x:
    :return:
    """
    if isinstance(graph, nx.Graph):
        retval = set(nx.non_neighbors(graph, x))
    else:
        retval = set(graph.non_neighbors(x))

    if all(isinstance(x, int) for x in retval):
        retval = BitMap(retval)

    return retval


@lru_cache(maxsize=None)
def number_of_edges(graph: nx.Graph | HalfAdjacencyMatrix) -> int:
    """
    Returns the number of edges in the graph. This function only exists to be able to cache
    results and is a much more convenient alternative to reimplementing the corresponding
    methods in nx.Graph, which unfortunately run in linear time.

    :param graph:
    :return:
    """
    return graph.number_of_edges()


@lru_cache(maxsize=None)
def number_of_nodes(graph: nx.Graph | HalfAdjacencyMatrix) -> int:
    """
    Returns the number of nodes in the graph. This function only exists to be able to cache
    results and is a much more convenient alternative to reimplementing the corresponding
    methods in nx.Graph, which unfortunately run in linear time.

    :param graph:
    :return:
    """
    return graph.number_of_nodes()


def induces_cycle(graph: nx.Graph, subset: BitMap) -> bool:
    """
    Returns True iff subset induces a cycle in graph.

    :param graph:
    :param subset:
    :return:
    """
    # subset induces a cycle iff every vertex it contains has degree 2 in the corresponding
    # subgraph and the subgraph is connected; to avoid building the subgraph, we check instead that
    # each vertex in the subset has two neighbors in the subset, and only after that do we try to
    # check connectedness
    if not all(len(neighbors(graph, v) & subset) == 2 for v in subset):
        return False

    return is_connected(graph.subgraph(subset))
