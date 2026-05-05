"""
Anthony Labarre © 2023-2026

O(n^3) algorithms.

"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
import os
from functools import lru_cache
from itertools import combinations, chain, product
from typing import Any, Iterator

# ----- Third-party imports -----------------------------------------------------------------------
import networkx as nx
from pyroaring import BitMap

# ----- My imports --------------------------------------------------------------------------------
from graph_recognition.adjacency_matrix import HalfAdjacencyMatrix
from graph_recognition.domination import dominates
from graph_recognition.misc_algo import (
    complement,
    empty_graph_by_removing_vertices,
    is_connected,
    degree_sequence, co_connected_components, complement_as_adj_mat, number_of_common_neighbors, common_neighbors,
    connected_components,
)
from graph_recognition.profitable_hereditary_n import (
    is_planar,
    is_bipartite,
    is_planar_and_maximum_degree_3,
    is_split,
    is_co_bipartite,
    is_tree,
    is_chordal, )
from graph_recognition.profitable_hereditary_n_2 import is_dilworth_k
from graph_recognition.profitable_hereditary_n_3 import is_girth_at_least_9, is_3k1_free
from graph_recognition.profitable_hereditary_n_3 import (
    is_interval,
    is_triangle_free,
    is_paw_free_and_perfect,
)
from graph_recognition.recognizers_utils import (
    assign_class_id,
    current_module_recognizers,
    cached_function, assign_inherited_fisc,
)

# Cache imported functions that are not already cached -------------------------------------------
__functions_to_cache = [
    # nx.all_shortest_paths, # DON'T: this calls a generator
    # nx.common_neighbors, # DON'T: this returns a generator expression
    # nx.connected_components,  # DON'T: this is a generator
    nx.diameter,
    nx.girth,
    nx.is_chordal,
    nx.is_distance_regular,
    # nx.non_edges,  # DON'T: this is a generator
    nx.shortest_path_length,
    nx.single_source_shortest_path_length,
]
for i, function in enumerate(__functions_to_cache):
    __functions_to_cache[i] = cached_function(function)


# Auxiliary functions ----------------------------------------------------------------------------
def explicit_independent_triplets(graph: nx.Graph) -> Iterator:
    """
    Generates all triplets of pairwise independent vertices in a graph.

    >>> test = nx.path_graph(5)
    >>> list(explicit_independent_triplets(test))
    [{0, 2, 4}, {0, 2, 4}]

    @param graph:
    @return:
    """
    # we iterate over non-edges {u, v}, and for each non-neighbor w of u, check whether w is also
    # not connected to v
    for u, v in nx.non_edges(graph):
        # careful: we may have w == v, since they are both non-neighbors of u, so we need to
        # explicitly exclude v
        for w in BitMap(nx.non_neighbors(graph, u)) - BitMap({v}):
            if not graph.has_edge(v, w):
                yield {u, v, w}


@lru_cache(maxsize=None)
def vertices_on_shortest_paths_between(graph: nx.Graph, pair: frozenset) -> BitMap:
    """
    Returns the set of all vertices on all shortest paths between u and v in graph.

    I use a pair of vertices as a frozenset so I can lru_cache the function and have the same
    answer available for (u, v) and (v, u).

    :param graph:
    :param pair: the two vertices to query
    """
    try:
        return BitMap(chain(*(nx.all_shortest_paths(graph, *pair))))

    except nx.exception.NetworkXNoPath:
        # this exception is raised when no path exists between u and v
        return BitMap()


@lru_cache(maxsize=None)
def vertex_is_d(graph: nx.Graph, x: Any) -> bool:
    """

    :param graph:
    :param x:
    :return:
    """
    """
    some definitions first
        x dominates y if N(y) - x <= N(x)
        x and y are comparable if x doms y or y doms x
        x is a d-vertex if for any edge yz whose endpoints are not in N(x),
        y and z are comparable
    note: i'm assuming "for any" means "every"
    """
    neighbors = set(graph[x])
    # check that every edge disjoint from N(x) consists of comparable endpoints
    for y, z in graph.edges:
        # check that endpoints are not neighbors of x
        if y in neighbors or z in neighbors:
            continue

        # check that y and z are comparable
        if not (dominates(graph, y, z) or dominates(graph, z, y)):
            return False

    return True


# Recognizers -------------------------------------------------------------------------------------
@assign_class_id("gc_604")
@lru_cache(maxsize=None)
def is_d(graph: nx.Graph) -> bool:
    """
    A graph is a D if each induced subgraph contains a vertex x such that for any edge yz with y, z
    not neighbors of x, y dominates z or vice versa.

    https://www.graphclasses.org/classes/gc_604

    :param graph:
    :return:
    """
    # this is the naive algo from: https://doi.org/10.1016/0166-218X(95)00042-P :
    # keep removing a d-vertex from G; G is a D-graph iff we end up with an empty graph
    return empty_graph_by_removing_vertices(graph, vertex_is_d)


@assign_class_id("gc_601")
@lru_cache(maxsize=None)
def is_interval_regular_of_diameter_2(graph: nx.Graph) -> bool:
    """
    A connected graph is interval regular of diameter 2 if every pair of nonadjacent vertices has
    exactly two common neighbors.

    https://www.graphclasses.org/classes/gc_601.html

    :param graph:
    :return:
    """
    if not is_connected(graph):
        return False

    return all(
        number_of_common_neighbors(graph, u, v) == 2 for u, v in nx.non_edges(graph)
    )


@assign_class_id("gc_173")
@lru_cache(maxsize=None)
def is_dilworth_3(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_173.html

    @param graph:
    @return:
    """
    return is_dilworth_k(graph, 3)


@assign_class_id("gc_49")
@lru_cache(maxsize=None)
def is_dismantlable(graph: nx.Graph) -> bool:
    """
    Recursive definition: K_{1} is dismantlable, and a graph G with >= 2 vertices is dismantlable
    iff it contains a dominated vertex z such that G - z is dismantlable.

    https://www.graphclasses.org/classes/gc_49

    @param graph:
    @return:
    """
    n = graph.order()
    if n == 1:
        return True

    # special cases, see bottom of page 478 in  https://doi.org/10.4153/CMB-1994-069-6
    #   trees are dismantlable
    #   graphs with a dominating vertex are dismantlable
    #   every connected, triangulated (i.e., chordal) graph on >= 2 vertices is dismantlable
    if degree_sequence(graph)[0] == n - 1 or is_tree(graph):
        return True

    if n >= 2 and is_connected(graph) and is_chordal(graph):
        return True

    # nonrecursive version; to avoid creating a lot of new subgraphs, copy graph into a disposable
    # version
    new_graph = graph.copy()
    while new_graph.number_of_nodes() > 1:
        for u, v in combinations(new_graph, 2):
            if dominates(new_graph, u, v):
                new_graph.remove_node(v)
                break
        else:
            return False

    return True


@assign_inherited_fisc()
@assign_class_id("gc_50")
@lru_cache(maxsize=None)
def is_modular(graph: nx.Graph) -> bool:
    """
    G is modular if for every three vertices x,y,z there exists a vertex w that lies on a shortest
    path between every two of x, y, z; i.e. if every metric triangle has size 0.

    https://www.graphclasses.org/classes/gc_50.html

    From https://doi.org/10.1007/BF02122796: "all graphs considered here are connected."

    @param graph:
    @return:
    """
    # alternative characterization that yields a faster recognition
    # algorithm: connected, triangle free, and pseudo-modular
    return is_connected(graph) and is_triangle_free(graph) and is_pseudo_modular(graph)


@assign_class_id("gc_211")
@lru_cache(maxsize=None)
def is_median(graph: nx.Graph) -> bool:
    """
    Let I(x, y) be the set of all vertices on all shortest paths between x and y. G is median if
    for all vertices x, y, z: |I(x,y) ∩ I(x,z) ∩ I(y,z)| = 1.

    https://www.graphclasses.org/classes/gc_211.html

    @param graph:
    @return:
    """
    for cc in connected_components(graph):
        for x, y, z in combinations(cc, 3):
            int_x_y = vertices_on_shortest_paths_between(graph, frozenset([x, y]))
            int_x_z = vertices_on_shortest_paths_between(graph, frozenset([x, z]))
            int_y_z = vertices_on_shortest_paths_between(graph, frozenset([y, z]))
            if len(int_x_y & int_x_z & int_y_z) != 1:
                return False

    return True


@assign_inherited_fisc()
@assign_class_id("gc_1169")
@lru_cache(maxsize=None)
def is_median_and_planar(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_1169

    @param graph:
    @return:
    """
    return is_planar(graph) and is_median(graph)


@lru_cache(maxsize=None)
def number_of_common_neighbors_at_distance(graph: nx.Graph, u: Any, v: Any, w: Any, k: int) -> int:
    """
    Returns the number of common neighbors of v and w at distance k - 1 from u.

    @param graph:
    @param u:
    @param v:
    @param w:
    @param k:
    @return:
    """
    return sum(
        1
        for _ in (
            x
            for x in common_neighbors(graph, v, w)
            if distance(graph, frozenset([u, x])) == k - 1
        )
    )


@assign_class_id("gc_262")
@lru_cache(maxsize=None)
def is_pseudo_median(graph: nx.Graph) -> bool:
    """
    A graph is pseudo-median if the following condition holds for all triples of vertices u, v, w:
    if 1 <= d(v, w) <= 2 and d(u, v) = d(u,w) = k >= 2, then there is a unique common neighbor x
    of v and w with d(u, x) = k-1.

    https://www.graphclasses.org/classes/gc_262.html

    From https://doi.org/10.1016/0012-365X(91)90022-T : G must be connected.

    @type graph: nx.Graph
    @param graph:
    @return:
    """
    if not is_connected(graph):
        return False

    # let's do this in two steps, should be faster than examining all triplets
    # 1) all v, w at distance 1 (= all edges)
    for u, (v, w) in product(graph, graph.edges):
        # skip if u not equidistant from v and w or not at distance >= 2; if u is either v or w,
        # then we skip it since v != w implies that u cannot be equidistant from v and w
        if u not in (v, w):
            k = distance(graph, frozenset([u, v]))
            if k < 2 or distance(graph, frozenset([u, w])) != k:
                continue
            if number_of_common_neighbors_at_distance(graph, u, v, w, k) != 1:
                return False

    # 2) all v, w at distance 2
    for u, (v, w) in product(
            graph,
            (
                    (x, y)
                    for x, y in nx.non_edges(graph)
                    if distance(graph, frozenset([x, y])) == 2
            ),
    ):
        # skip if u not equidistant from v and w or not at distance >= 2; if u is either v or w,
        # then we skip it since v != w implies that u cannot be equidistant from v and w
        if u not in (v, w):
            k = distance(graph, frozenset([u, v]))
            if k < 2 or distance(graph, frozenset([u, w])) != k:
                continue
            if number_of_common_neighbors_at_distance(graph, u, v, w, k) != 1:
                return False

    return True


@assign_class_id("gc_203")
@lru_cache(maxsize=None)
def is_pseudo_modular(graph: nx.Graph) -> bool:
    """
    A connected graph G is pseudo-modular if and only if, for any three vertices u, v, w of G with
    1 <= d(v, w) <= 2 and d(u, v)=d(u, w) = k >= 2, there exists a vertex x adjacent to both v and
    w with d(u, x) = k - 1.

    https://www.graphclasses.org/classes/gc_203.html

    The above characterization is from H.-J. Bandelt and H.M. Mulder, Pseudo-modular graphs,
    Discrete Math. 62 (1986) 245-260.

    @param graph:
    @return:
    """
    if not is_connected(graph):
        return False

    # let's do this in two steps, should be faster than examining all triplets
    # 1) all v, w at distance 1 (= all edges)
    for v, w in graph.edges:
        # for u in graph:
        # for u in set(graph) - {v, w}:
        # u is at distance >= 2 of both v and w iff it's not adjacent to either
        # of them
        for u in set(nx.non_neighbors(graph, v)) & set(nx.non_neighbors(graph, w)):
            # skip if u not equidistant from v and w or not at distance >= 2
            k = distance(graph, frozenset([u, v]))
            if k < 2 or distance(graph, frozenset([u, w])) != k:
                continue
            # is there a common neighbor of v and w at distance k-1 from u?
            if all(
                    distance(graph, frozenset([u, x])) != k - 1
                    for x in common_neighbors(graph, v, w)
            ):
                return False

    # 2) all v, w at distance 2
    for v, w in nx.non_edges(graph):
        if distance(graph, frozenset([v, w])) == 2:
            # for u in graph:
            # for u in set(graph) - {v, w}:
            # u is at distance >= 2 of both v and w iff it's not adjacent to either
            # of them
            for u in set(nx.non_neighbors(graph, v)) & set(nx.non_neighbors(graph, w)):
                # skip if u not equidistant from v and w or not at distance >= 2
                k = distance(graph, frozenset([u, v]))
                if k < 2 or distance(graph, frozenset([u, w])) != k:
                    continue

                # is there a common neighbor of v and w at distance k-1 from u?
                if all(
                        distance(graph, frozenset([u, x])) != k - 1
                        for x in common_neighbors(graph, v, w)
                ):
                    return False

    return True


@assign_class_id("gc_600")
@lru_cache(maxsize=None)
def is_interval_regular(graph: nx.Graph) -> bool:
    """
    A connected graph is interval regular if for any two vertices u, v the number of neighbors of u
    on all shortest (u, v)-paths equals d(u, v).

    https://www.graphclasses.org/classes/gc_600

    @type graph: nx.Graph
    @param graph:
    @return:
    """
    # note: this function is very slow on Cayley graphs of permutation groups, so I'm looking for
    # anything that could make it faster.
    # From the paper introducing them:
    # https://www.sciencedirect.com/science/article/pii/0012365X82900218
    # """
    if not is_connected(graph):
        return False

    @lru_cache(maxsize=None)
    def _neighbors(x: Any) -> BitMap:
        return BitMap(graph[x])

    # NOTE: I used to precompute all intervals, but that was way too slow, so now I'm computing
    # them as I go in the hope that we'll stop early
    for u, v in combinations(graph.nodes, 2):
        int_u_v = vertices_on_shortest_paths_between(graph, frozenset([u, v]))
        # note: since combinations produces unique pairs, we must check the condition both ways
        # (i.e., for u and for v)
        if (
                len(_neighbors(u) & int_u_v) != distance(graph, frozenset([u, v])) or
                len(_neighbors(v) & int_u_v) != distance(graph, frozenset([u, v]))
        ):
            _neighbors.cache_clear()
            return False

    _neighbors.cache_clear()
    return True


# @assign_inherited_fisc()  # DON'T: condition below is a "or", not an "and"
@assign_class_id("gc_247")
@lru_cache(maxsize=None)
def is_interval_or_co_interval(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_interval(graph) or is_co_interval(graph)


@assign_inherited_fisc()
@assign_class_id("gc_1226")
@lru_cache(maxsize=None)
def is_bipartite_and_girth_at_least9_and_maximum_degree3_and_planar(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_1226.html

    @param graph:
    @return:
    """
    return (
            is_bipartite(graph)
            and is_planar_and_maximum_degree_3(graph)
            and is_girth_at_least_9(graph)
    )


@lru_cache(maxsize=None)
def distance(graph: nx.Graph, pair: frozenset) -> int:
    """
    Returns the distance between two vertices in a graph.

    I use a pair of vertices as a frozenset so I can lru_cache the function and have the same
    answer available for (u, v) and (v, u).

    :param pair: the two vertices to query
    :param graph:
    :return:
    """
    u, v = pair
    return int(nx.shortest_path_length(graph, u)[v])


@assign_class_id("gc_222")
@lru_cache(maxsize=None)
def is_weakly_modular(graph: nx.Graph) -> bool:
    """
    ISGCI gives two different characterizations of weakly modular graphs:

    1) The interval I(u,v) contains all vertices that lie on a shortest path from u to v. Three
    vertices u, v, w form a metric triangle if the interval I(u, v), I(v, w) and I(w, u) pairwise
    intersect only in the common end vertices. A graph is weakly modular if for every metric
    triangle u, v, w all vertices of I(v,w) are at the same distance k = d(u, v) from u.

    2) A graph is weakly modular if its distance metric fulfills the triangle and quadrangle
    conditions:

        The triangle condition: For every three vertices u, v, w with 1 = d(v,w) < d(u,v) = d(u,w),
            there is a common neighbor x of v and w such that d(u,x) = d(u,v) + 1.

        The quadrangle condition: For every four vertices, u, v, w, z with d(v, z) = d(w, z) = 1
            and d(u, v) = d(u, w) = d(u, z) - 1, there is a common neighbor x of v and w such that
            d(u,x) = d(u,v) - 1.

    https://www.graphclasses.org/classes/gc_222.html

    >>> from networkx import Graph; G = Graph()
    >>> G.add_edges_from([(0, 4), (1, 4), (2, 5), (3, 5), (4, 5)])
    >>> is_weakly_modular(G)
    True

    @param graph:
    @return:
    """
    # Note: the second definition yields a faster algorithm, but currently fails on my test data
    # sets, so either my implementation is wrong or the paper is. Let us settle for definition 1)
    # for now
    for cc in connected_components(graph):
        for u, v, w in combinations(cc, 3):
            # do u, v, w form a metric triangle?
            int_u_v = vertices_on_shortest_paths_between(graph, frozenset([u, v]))
            int_u_w = vertices_on_shortest_paths_between(graph, frozenset([u, w]))
            int_v_w = vertices_on_shortest_paths_between(graph, frozenset([v, w]))

            if int_u_v & int_u_w == {u} and int_u_v & int_v_w == {v} and int_u_w & int_v_w == {w}:
                # do all vertices in I(v, w) have the same distance to u?
                k = distance(graph, frozenset([next(iter(int_u_v)), u]))
                if any(distance(graph, frozenset([x, u])) != k for x in int_v_w):
                    return False

    return True


@assign_class_id("gc_1267")
@lru_cache(maxsize=None)
def is_probe_co_bipartite(graph: nx.Graph) -> bool:
    """
    A graph is a probe co-bipartite graph if its vertex set can be partitioned into two sets,
    probes (P) and non-probes (N), such that N is independent and new edges can be added between
    non-probes in such a way that the resulting graph is a co-bipartite graph.

    https://www.graphclasses.org/classes/gc_1267

    @param graph:
    @return:
    """
    if not graph.edges:
        return True

    # according to ISGCI co-bipartite graphs are probe co-bipartite; this check needs to be
    # performed, because some special cases will otherwise fail (case in point: a graph made of a
    # single edge)
    if is_co_bipartite(graph):
        return True

    # The algorithm comes from https://dmtcs.episciences.org/2122/pdf, page 190 and runs in O(n^3)
    # time if G is co-triangle-free (i.e. 3K_1-free)
    if is_3k1_free(graph):
        # then check if for some non-edge e of G whether co(G) − e is bipartite (i.e., whether
        # G U e is co-bipartite); G is probe 2-clique iff there is such an edge (Lemma 1 p 189)
        graph_copy = graph.copy()
        for u, v in nx.non_edges(graph):
            graph_copy.add_edge(u, v)
            retval = is_co_bipartite(graph_copy)
            graph_copy.remove_edge(u, v)
            if retval:
                return True

        return False

    # construct T(co(G)), the spanning subgraph of co(G) (or G) whose edge set contains precisely
    # the edges that are contained in some co-triangle of G
    t_co_g = HalfAdjacencyMatrix()
    for co_triangle in explicit_independent_triplets(graph):
        t_co_g.add_edges_from(combinations(co_triangle, 2))

    # if T(co(G)) is not a split graph, then G is not probe 2-clique
    if not is_split(t_co_g):
        return False

    # otherwise, find each maximal complete subgraph C of T(co(G))
    for maximal_clique in nx.find_cliques(t_co_g):  # noqa (unexpected type HalfAdjacencyMatrix)
        # cliques in co(G) are independent sets in G; let's build the corresponding edge set
        edge_set = list(combinations(maximal_clique, 2))
        # verify if co(G) − E(C) is bipartite [if so, return True according to their Lemma 2 page
        # 189] as above, verifying whether co(G) − E(C) is bipartite is equivalent to checking
        # whether G U E(C) is co-bipartite
        graph.add_edges_from(edge_set)
        retval = is_co_bipartite(graph)
        graph.remove_edges_from(edge_set)
        if retval:
            return True

    return False


# -------------------------------------------------------------------------------------------------
# The following recognizers call another recognizer on the complement of the input graph. Since
# building the complement can be time- and memory-consuming on large instances, and since
# recognizers are loaded in the order in which they appear in a recognizer file, those recognizers
# should stay at the end of the file in the hope that they are not actually needed until we figure
# out a way to bypass the computation of the complement.
# -------------------------------------------------------------------------------------------------
@assign_class_id("AUTO_2780")
@lru_cache(maxsize=None)
def is_co_paw_odd_anti_hole_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_2780

    @param graph:
    @return:
    """
    # iterate over co-connected components instead of complementing the whole graph, in the hope
    # that we can thereby stop early
    # note: complement_as_adj_mat not usable yet because nx._plain_bfs wants an _adj attribute
    return all(
        is_paw_free_and_perfect(complement(graph.subgraph(cc)))
        for cc in co_connected_components(graph)
    )


@assign_class_id("gc_157")
@lru_cache(maxsize=None)
def is_co_interval(graph: nx.Graph) -> bool:
    """
    A co-interval graph is a graph whose complement is an interval graph.

    https://www.graphclasses.org/classes/gc_157

    @param graph:
    @return:
    """
    # iterate over co-connected components instead of complementing the whole graph, in the hope
    # that we can thereby stop early
    return all(
        is_interval(complement_as_adj_mat(graph, cc)) for cc in co_connected_components(graph)
    )


@assign_class_id("gc_96")
@lru_cache(maxsize=None)
def is_geodetic(graph: nx.Graph) -> bool:
    """
    A graph is geodetic if for every pair of vertices the shortest path between them is unique.

    https://www.graphclasses.org/classes/gc_96

    Complexity: O(n^3), since at most two BFS are launched for every pair of vertices.

    @param graph:
    @return:
    """
    # if graph is disconnected, then some pairs of vertices are mutually unreachable
    if not is_connected(graph):
        return False

    # naïve algorithm
    for u, v in combinations(graph, 2):
        for k, _ in enumerate(nx.all_shortest_paths(graph, u, v), 1):
            if k > 1:
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
RECOGNIZERS.update(
    {
        "gc_1148": cached_function(nx.is_distance_regular),
    }
)
# -------------------------------------------------------------------------------------------------
