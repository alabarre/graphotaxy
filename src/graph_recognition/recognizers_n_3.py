"""
Anthony Labarre © 2023-2025

O(n^3) algorithms.

"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
import multiprocessing as mp
import os
from collections import defaultdict
from functools import lru_cache
from itertools import combinations_with_replacement, combinations, chain, product
from math import log
from typing import Any, Iterable, Iterator

# ----- Third-party imports -----------------------------------------------------------------------
import networkx as nx

# ----- My imports --------------------------------------------------------------------------------
from graph_recognition.misc_algo import (
    complement,
    dominates,
    empty_graph_by_removing_vertices,
    all_pairs_shortest_path_length,
    is_connected,
    is_complete,
    degree_sequence, co_connected_components,
)
from graph_recognition.profitable_hereditary_n import (
    is_planar,
    is_bipartite,
    is_planar_and_maximum_degree_3,
    is_split,
    is_co_bipartite,
    is_tree,
    is_chordal,
)
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
    cached_function,
)

# Cache imported functions that are not already cached -------------------------------------------
__functions_to_cache = [
    # nx.all_pairs_shortest_path_length,  # DON'T: this is a generator
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
        # TODO why not intersect common non neighbors? and remove both u and v then
        for w in set(nx.non_neighbors(graph, u)) - {v}:
            if not graph.has_edge(v, w):
                yield {u, v, w}


@lru_cache(maxsize=None)
def vertices_on_shortest_paths_between(graph: nx.Graph, u: Any, v: Any) -> set:
    """
    Returns the set of all vertices on all shortest paths between u and v in graph.

    @param graph:
    @param u:
    @param v:
    @return:
    """
    try:
        return set(chain(*(nx.all_shortest_paths(graph, u, v))))

    except nx.exception.NetworkXNoPath:
        # this exception is raised when no path exists between u and v
        return set()


@lru_cache(maxsize=None)
def vertices_on_shortest_paths(graph: nx.Graph) -> dict:
    """
    Returns a dictionary where key = edge {u, v} and value = the set of all vertices that belong to
    a shortest path between u and v. Those sets are often called "intervals" in the literature.

    @param graph:
    @return:
    """
    if is_connected(graph):
        intervals = dict()
        for u, v in combinations(graph, 2):
            intervals[frozenset([u, v])] = set(
                chain(*(nx.all_shortest_paths(graph, u, v)))
            )

        return intervals

    else:
        # graph is disconnected: launch parallel searches on each connected component; using a
        # defaultdict allows us to avoid checking whether the pair we will query exists
        result = defaultdict(set)
        for cc in nx.connected_components(graph):
            all_pairs = set(combinations(cc, 2))
            with mp.Pool() as p:
                result.update(
                    dict(
                        zip(
                            map(frozenset, all_pairs),
                            p.starmap(
                                func=vertices_on_shortest_paths_between,
                                iterable=(
                                    (graph.subgraph(cc), u, v) for u, v in all_pairs
                                ),
                            ),
                        )
                    )
                )

        return result


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
        # check that endpoints are not neighbours of x
        if y in neighbors or z in neighbors:
            continue

        # check that y and z are comparable
        if not (dominates(graph, y, z) or dominates(graph, z, y)):
            return False

    return True


# Recognizers ------------------------------------------------------------------------------------
@assign_class_id("gc_604")
@lru_cache(maxsize=None)
def is_d(graph: nx.Graph) -> bool:
    """
    A graph is a D if each induced subgraph contains a vertex x such that for any edge yz with y, z
    not neighbours of x, y dominates z or vice versa.

    https://www.graphclasses.org/classes/gc_604

    :param graph:
    :return:
    """
    # this is the naive algo from: https://doi.org/10.1016/0166-218X(95)00042-P :
    # keep removing a d-vertex from G; G is a D-graph iff we end up with an
    # empty graph
    return empty_graph_by_removing_vertices(graph, vertex_is_d)


@assign_class_id("gc_601")
@lru_cache(maxsize=None)
def is_interval_regular_of_diameter_2(graph: nx.Graph) -> bool:
    """
    A connected graph is interval regular of diameter 2 if every pair of nonadjacent vertices has
    exactly two common neighbours.

    https://www.graphclasses.org/classes/gc_601.html

    :param graph:
    :return:
    """
    if not is_connected(graph):
        return False

    return all(
        sum(1 for _ in nx.common_neighbors(graph, u, v)) == 2 for u, v in nx.non_edges(graph)
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
    #   every connected, triangulated (i.e., chordal)) graph on >= 2 vertices is dismantlable
    #   TODO every connected bridged graph is dismantlable (but I have no recognizer yet for gc_99)
    if degree_sequence(graph)[0] == n - 1 or is_tree(graph):
        return True

    if n >= 2 and is_connected(graph) and is_chordal(graph):
        return True

    nodes = set(graph.nodes)
    for z in graph:
        if any(
            dominates(graph, y, z) and is_dismantlable(graph.subgraph(nodes - {z}))
            for y in nodes - {z}
        ):
            return True

    return False


# NOTE: this is not a class in ISGCI, but this recognizer is needed to recognize the complement
# class (1, 2)-colorable
# TODO running time is O(n²m)<=O(n4), move this
@lru_cache(maxsize=None)
def is_2_1_colorable(graph: nx.Graph) -> bool:
    """
    Returns True iff graph can be partitioned into 2 cliques and 1 independent set.

    See https://www.graphclasses.org/classes/gc_500 for (p, q)-colorable

    @param graph:
    @return:
    """
    # algorithm 1 from https://nbn-resolving.org/urn:nbn:de:hbz:708-dh9961; this is a revised
    # version of  https://doi.org/10.1016/0012-365X(94)00296-U, which was wrong according to
    # https://www.sciencedirect.com/science/article/pii/S0012365X98000144
    # notation:
    #   (1, 1) is the class of split graphs
    #   (2, 0) is the class of bipartite graphs
    #   N(v) is the open neighborhood of v

    # preprocess vertices to classify them based on whether or not N(v) is (1, 1) and whether or
    # not co(N(v)) is (2, 0); each vertex will be mapped onto a tuple (a, b) expressing those
    # properties
    neighborhood_conditions = dict()
    for v in graph:
        neighborhood_conditions[v] = (
            is_split(graph.subgraph(graph[v])),
            is_bipartite(graph.subgraph(nx.non_neighbors(graph, v))),
        )
        # give up early if a vertex satisfies neither condition
        if neighborhood_conditions[v] == (False, False):
            return False

    # build set R: vertices whose neighborhood is (1, 1) and whose co-neighborhood is (2, 0)
    r_set = {v for v in graph if neighborhood_conditions[v] == (True, True)}

    # move each vertex NOT in R to a clique or the union of two independent sets if possible
    c_s = {v for v in graph if neighborhood_conditions[v] == (False, True)}
    if not is_complete(graph.subgraph(c_s)):
        return False

    i_s = {v for v in graph if neighborhood_conditions[v] == (True, False)}
    if not is_bipartite(graph.subgraph(i_s)):
        return False

    # if R is empty then we have a yes-instance
    if not r_set:
        return True

    if is_split(graph.subgraph(r_set)):
        pass  # TODO apply Lemma 2
    else:
        pass  # TODO apply Lemma 1

    # TODO finish


@assign_class_id("gc_1148")
@lru_cache(maxsize=None)
def my_is_distance_regular(graph: nx.Graph) -> bool:
    """Returns True if the graph is distance regular, False otherwise.

    A connected graph G is distance-regular if for any nodes x,y and any integers i,j=0,1,...,d
    (where d is the graph diameter), the number of vertices at distance i from x and distance j
    from y depends only on i,j and the graph distance between x and y, independently of the choice
    of x and y.

    Parameters
    ----------
    graph: Networkx graph (undirected)

    Returns
    -------
    bool
      True if the graph is Distance Regular, False otherwise

    Examples
    --------
    >>> G = nx.hypercube_graph(6)
    >>> nx.is_distance_regular(graph)
    True

    See Also
    --------
    intersection_array, global_parameters

    Notes
    -----
    For undirected and simple graphs only

    References
    ----------
    .. [1] Brouwer, A. E.; Cohen, A. M.; and Neumaier, A.
        Distance-Regular Graphs. New York: Springer-Verlag, 1989.
    .. [2] Weisstein, Eric W. "Distance-Regular Graph."
        http://mathworld.wolfram.com/Distance-RegularGraph.html

    """
    try:
        my_intersection_array(graph)
        return True
    except nx.NetworkXError:
        return False


@lru_cache(maxsize=None)
def my_intersection_array(graph: nx.Graph) -> Iterable:
    """Returns the intersection array of a distance-regular graph.

    Given a distance-regular graph G with integers b_i, c_i,i = 0,....,d such that for any 2
    vertices x,y in G at a distance i=d(x,y), there are exactly c_i neighbors of y at a distance of
    i-1 from x and b_i neighbors of y at a distance of i+1 from x.

    A distance regular graph's intersection array is given by
    [b_0,b_1,.....b_{d-1};c_1,c_2,.....c_d]

    Parameters
    ----------
    graph: Networkx graph (undirected)

    Returns
    -------
    b,c: tuple of lists

    Examples
    --------
    >>> G = nx.icosahedral_graph()
    >>> nx.intersection_array(graph)
    ([5, 2, 1], [1, 2, 5])

    References
    ----------
    .. [1] Weisstein, Eric W. "Intersection Array."
       From MathWorld--A Wolfram Web Resource.
       http://mathworld.wolfram.com/IntersectionArray.html

    See Also
    --------
    global_parameters
    """
    # the input graph is very unlikely to be distance-regular: here are the
    # number a(n) of connected simple graphs, and the number b(n) of
    # distance-regular graphs among them:
    #
    #    n  | 1 2 3 4  5   6   7     8      9       10
    #  -----+------------------------------------------------------------------
    #  a(n) | 1 1 2 6 21 112 853 11117 261080 11716571 https://oeis.org/A001349
    #  b(n) | 1 1 1 2  2   4   2     5      4        7 https://oeis.org/A241814
    #
    # in light of this, let's compute shortest path lengths as we go instead of
    # precomputing them all
    # test for regular graph (all degrees must be equal)
    if not nx.is_regular(graph) or not nx.is_connected(graph):
        raise nx.NetworkXError("Graph is not distance regular.")

    # path_length = dict(nx.all_pairs_shortest_path_length(G))
    path_length = defaultdict(dict)
    bint = {}  # 'b' intersection array
    cint = {}  # 'c' intersection array

    # see https://doi.org/10.1016/j.ejc.2004.07.004, Theorem 1.5 page 81: the
    # diameter of a distance-regular graph is at most (8 log_2 n) / 3, so let's
    # compute it as we go in the hope that we can stop early
    diameter = 0
    max_diameter_for_dr_graphs = (8 * log(graph.number_of_nodes(), 2)) / 3
    for u, v in combinations_with_replacement(graph, 2):
        if u not in path_length or v not in path_length[u]:
            path_length[u].update(nx.single_source_shortest_path_length(graph, u))
            for x, distance in path_length[u].items():
                path_length[x][u] = distance

        i = path_length[u][v]
        diameter = max(diameter, i)

        # diameter too large: graph can't be distance-regular
        if diameter > max_diameter_for_dr_graphs:
            raise nx.NetworkXError("Graph is not distance regular.")

        # compute needed path lengths
        for n in graph[v]:
            if n not in path_length or u not in path_length[n]:
                path_length[n].update(nx.single_source_shortest_path_length(graph, n))
                for x, distance in path_length[n].items():
                    path_length[x][n] = distance

        # number of neighbors of v at a distance of i-1 from u
        # c = len([n for n in G[v] if path_length[n][u] == i - 1])
        c = sum(1 for n in graph[v] if path_length[n][u] == i - 1)
        # number of neighbors of v at a distance of i+1 from u
        # b = len([n for n in G[v] if path_length[n][u] == i + 1])
        b = sum(1 for n in graph[v] if path_length[n][u] == i + 1)
        # b,c are independent of u and v
        if cint.get(i, c) != c or bint.get(i, b) != b:
            raise nx.NetworkXError("Graph is not distance regular")
        bint[i] = b
        cint[i] = c

    # diameter = max(max(path_length[n].values()) for n in path_length)
    return (
        [bint.get(j, 0) for j in range(diameter)],
        [cint.get(j + 1, 0) for j in range(diameter)],
    )


@assign_class_id("gc_50")
@lru_cache(maxsize=None)
def is_modular(graph: nx.Graph) -> bool:
    """
    G is modular if for every three vertices x,y,z there exists a vertex w that
    lies on a shortest path between every two of x, y, z; i.e. if every metric
    triangle has size 0.

    https://www.graphclasses.org/classes/gc_50.html

    From https://doi.org/10.1007/BF02122796: "all graphs considered here are
    connected."

    @param graph:
    @return:
    """
    # alternative characterisation that yields a faster recognition
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
    # equivalence from isgci: triangle-free and pseudo-median
    return is_triangle_free(graph) and is_pseudo_median(graph)


@assign_class_id("gc_1169")
@lru_cache(maxsize=None)
def is_median_and_planar(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_1169

    @param graph:
    @return:
    """
    return is_planar(graph) and is_median(graph)


def number_of_common_neighbors_at_distance(
    graph: nx.Graph, u: Any, v: Any, w: Any, k: int
) -> int:
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
            for x in nx.common_neighbors(graph, v, w)
            if nx.shortest_path_length(graph, u, x) == k - 1
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
        # skip if u not equidistant from v and w or not at distance >= 2
        k = nx.shortest_path_length(graph, u, v)
        if k < 2 or nx.shortest_path_length(graph, u, w) != k:
            continue
        if number_of_common_neighbors_at_distance(graph, u, v, w, k) != 1:
            return False

    # 2) all v, w at distance 2
    for u, (v, w) in product(
        graph,
        (
            (x, y)
            for x, y in nx.non_edges(graph)
            if nx.shortest_path_length(graph, x, y) == 2
        ),
    ):
        # skip if u not equidistant from v and w or not at distance >= 2
        k = nx.shortest_path_length(graph, u, v)
        if k < 2 or nx.shortest_path_length(graph, u, w) != k:
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

    # TODO slow; I should not gain anything by caching since calls to nx.shortest_path_length
    #   are already cached, but maybe if i use single source shortest path lengths as in my
    #   improvement to intersection_array ...
    # let's do this in two steps, should be faster than examining all triplets
    # 1) all v, w at distance 1 (= all edges)
    for v, w in graph.edges:
        # for u in graph:
        # for u in set(graph) - {v, w}:
        # u is at distance >= 2 of both v and w iff it's not adjacent to either
        # of them TODO so condition on k below can go away
        for u in set(nx.non_neighbors(graph, v)) & set(nx.non_neighbors(graph, w)):
            # skip if u not equidistant from v and w or not at distance >= 2
            k = nx.shortest_path_length(graph, u, v)
            if k < 2 or nx.shortest_path_length(graph, u, w) != k:
                continue
            # is there a common neighbor of v and w at distance k-1 from u?
            if all(
                nx.shortest_path_length(graph, u, x) != k - 1
                for x in nx.common_neighbors(graph, v, w)
            ):
                return False

    # 2) all v, w at distance 2
    for v, w in nx.non_edges(graph):
        if nx.shortest_path_length(graph, v, w) == 2:
            # for u in graph:
            # for u in set(graph) - {v, w}:
            # u is at distance >= 2 of both v and w iff it's not adjacent to either
            # of them
            # TODO so condition on k below can go away --- careful: not exactly same case as above
            for u in set(nx.non_neighbors(graph, v)) & set(nx.non_neighbors(graph, w)):
                # skip if u not equidistant from v and w or not at distance >= 2
                k = nx.shortest_path_length(graph, u, v)
                if k < 2 or nx.shortest_path_length(graph, u, w) != k:
                    continue

                # is there a common neighbor of v and w at distance k-1 from u?
                if all(
                    nx.shortest_path_length(graph, u, x) != k - 1
                    for x in nx.common_neighbors(graph, v, w)
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
    # note: this function is very slow on Cayley graphs of permutation groups,
    # so I'm hunting for anything that could make it faster.
    # From the paper introducing them:
    # https://www.sciencedirect.com/science/article/pii/0012365X82900218

    # FORMER VERSION
    # """
    if not is_connected(graph):
        return False

    # NOTE: I used to precompute all intervals, but that was way too slow, so now I'm computing
    # them as I go in the hope that we'll stop early
    # intervals = vertices_on_shortest_paths(graph)
    # TODO I should do the same for distances actually; same way as in my new intersection array
    #  function
    distances = all_pairs_shortest_path_length(graph)
    for u, v in combinations(graph.nodes, 2):
        int_u_v = vertices_on_shortest_paths_between(
            graph, u, v
        )  # intervals[frozenset([u, v])]
        # note: since combinations produces unique pairs, we must check the
        # condition both ways (i.e., for u and for v)
        if (
            len(set(graph[u]) & int_u_v) != distances[u][v]
            or len(set(graph[v]) & int_u_v) != distances[u][v]
        ):
            return False

    return True


@assign_class_id("gc_247")
@lru_cache(maxsize=None)
def is_interval_or_co_interval(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_interval(graph) or is_co_interval(graph)


@assign_class_id("gc_1226")
@lru_cache(maxsize=None)
def is_bipartite_and_girth_at_least9_and_maximum_degree3_and_planar(
    graph: nx.Graph,
) -> bool:
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
            and d(u, v) = d(u, w) = d(u, z) - 1, there is a common neighbour x of v and w such that
            d(u,x) = d(u,v) - 1.

    https://www.graphclasses.org/classes/gc_222.html

    >>> import networkx as nx; G = nx.Graph()
    >>> G.add_edges_from([(0, 4), (1, 4), (2, 5), (3, 5), (4, 5)])
    >>> is_weakly_modular(G)
    True

    @param graph:
    @return:
    """
    # Note: the second definition yields a faster algorithm, but currently fails on my test data
    # sets, so either my implementation is wrong or the paper is. Let us settle for definition 1)
    # for now
    distances = all_pairs_shortest_path_length(graph)
    intervals = vertices_on_shortest_paths(graph)
    for cc in nx.connected_components(graph):
        for u, v, w in combinations(cc, 3):
            # do u, v, w form a metric triangle?
            f_u_v, f_u_w, f_v_w = (
                frozenset({u, v}),
                frozenset({u, w}),
                frozenset({v, w}),
            )
            if (
                intervals[f_u_v] & intervals[f_u_w] == {u}
                and intervals[f_u_v] & intervals[f_v_w] == {v}
                and intervals[f_u_w] & intervals[f_v_w] == {w}
            ):
                # do all vertices in I(v, w) have the same distance to u?
                if len({distances[x][u] for x in intervals[f_v_w]}) != 1:
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
        for u, v in nx.non_edges(graph):
            graph.add_edge(u, v)
            retval = is_co_bipartite(graph)
            graph.remove_edge(u, v)
            if retval:
                return True

        return False

    # construct T(co(G)), the spanning subgraph of co(G) (or G) whose edge set contains precisely
    # the edges that are contained in some co-triangle of G
    t_co_g = nx.empty_graph(graph)
    for co_triangle in explicit_independent_triplets(graph):
        t_co_g.add_edges_from(combinations(co_triangle, 2))

    # if T(co(G)) is not a split graph, then G is not probe 2-clique
    if not is_split(t_co_g):
        return False

    # otherwise, find each maximal complete subgraph C of T(co(G))
    for maximal_clique in nx.find_cliques(t_co_g):
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
# @assign_class_id("gc_540")  # TODO debug in progress, do not use yet
@lru_cache(maxsize=None)
def is_1_2_colorable(graph: nx.Graph) -> bool:
    """
    A graph is (1, 2)-colorable iff its complement is (2, 1)-colorable.

    https://www.graphclasses.org/classes/gc_540.html

    @param graph:
    @return:
    """
    return is_2_1_colorable(complement(graph))


@assign_class_id("AUTO_2780")
@lru_cache(maxsize=None)
def is_co_paw_odd_anti_hole_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    # iterate over co-connected components instead of complementing the whole graph, in the hope
    # that we can thereby stop early
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
        is_interval(complement(graph.subgraph(cc)))
        for cc in co_connected_components(graph)
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
        for i, _ in enumerate(nx.all_shortest_paths(graph, u, v), 1):
            if i > 1:
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
