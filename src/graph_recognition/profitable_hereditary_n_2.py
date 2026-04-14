"""
Anthony Labarre © 2023-2026

This file contains recognizers for profitable hereditary classes, i.e. classes that admit a
forbidden induced subgraph characterization, but can be recognized with a faster-than-naïve
algorithm.

Recognizers in this file have running time O(n^2).

"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
import os
from array import array
from collections import defaultdict
from functools import lru_cache
from itertools import combinations, takewhile

# ----- Third-party imports -----------------------------------------------------------------------
import networkx as nx
from networkx import is_empty
from pyroaring import BitMap

# ----- My imports --------------------------------------------------------------------------------
from graph_recognition.adjacency_matrix import HalfAdjacencyMatrix
from graph_recognition.misc_algo import (
    degree_sequence,
    complement,
    number_of_common_neighbors,
    is_connected,
    is_h_u_k1_free,
    co_connected_components, complement_as_adj_mat, connected_components,
)
from graph_recognition.online_algo import online_is_bipartite
from graph_recognition.profitable_hereditary_n import (
    is_chordal,
    is_split,
    is_p3_free,
    is_cograph,
    is_bipartite,
    is_planar,
    is_cubic,
    is_2k2_free, is_mock_threshold,
)
from graph_recognition.recognizers_utils import (
    current_module_recognizers,
    assign_class_id,
    assign_fisc, undecorated_function, )
from graph_recognition.subgraphs import is_h_free


# Recognizers -------------------------------------------------------------------------------------
@assign_fisc(["P_{4}", "2K_{2}", "C_{4}"])
@assign_class_id("gc_329")
@lru_cache(maxsize=None)
def is_threshold(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, C_{4}, P_{4})-free.

    See https://www.graphclasses.org/classes/gc_329

    Complexity: O(n^2) < O(n^4) (naïve)

    :type graph: networkx.Graph
    """
    # simple, profitable check
    if not is_cograph(graph):
        return False

    # equivalent to threshold: https://www.graphclasses.org/classes/gc_329
    # adapting networkx's code until they release the version that contains function is_threshold:
    """
    Uses the property that a threshold graph must be constructed by adding either dominating or 
    isolated nodes. Thus, it can be deconstructed iteratively by removing a node of degree zero or 
    a node that connects to the remaining nodes.  If this deconstruction fails then the sequence is
    not a threshold sequence.
    """
    ds = degree_sequence(graph)
    ds.reverse()
    while ds:
        # instead of popping leading zeroes separately, remove them all at once
        length_of_longest_zero_prefix = sum(1 for _ in takewhile(lambda val: not val, ds))
        if not ds[length_of_longest_zero_prefix - 1]:
            ds = ds[length_of_longest_zero_prefix:]
            continue

        if ds[-1] != len(ds) - 1:  # is the largest degree node dominating?
            return False

        ds.pop()  # yes, largest is the dominating node
        ds = array(ds.typecode, [d - 1 for d in ds])  # remove it and decrement all degrees

    return True


# not an actual ISGCI class
@lru_cache(maxsize=None)
def is_dilworth_k(graph: nx.Graph, k: int) -> bool:
    """
    Two vertices x and y are said to be comparable if either N(y) <= N[x] or N(x) <= N[y]. The
    Dilworth number of a graph is the largest number of pairwise incomparable vertices of the
    graph. A graph is Dilworth k if it has Dilworth number k.

    :type graph: nx.Graph
    :param k:
    :return:
    """
    count = 0

    # for each pair of vertices, test whether they are incomparable;
    for u, v in combinations(graph, 2):
        n_u, n_v = set(graph[u]), set(graph[v])
        # check whether u and v are incomparable
        count += not (n_u <= n_v.difference({u}) or n_v <= n_u.difference({v}))

        # if the count exceeds k at some point, then graph is NOT Dilworth k
        if count > k:
            return False

    return count == k


@assign_fisc(["W_{4}", "butterfly", "W_{5}"])
@assign_class_id("gc_1219")
@lru_cache(maxsize=None)
def is_locally_split(graph: nx.Graph) -> bool:
    """
    A graph is locally split if the open neighborhood of each vertex induces a split graph.

    Complexity: O(n^2) < O(n^6) (naïve)

    https://www.graphclasses.org/classes/gc_1219.html

    :param graph:
    :return:
    """
    return all(is_split(graph.subgraph(graph[v])) for v in graph)


@assign_fisc(
    [
        "house",
        "P_{5}",
        "C_{5}",
        "co-fish",
        "fish",
        "3K_{2}",
        "S_{3}",
        "net",
        "C_{4} U P_{2}",
        "P_{2} U P_{4}",
        "co(3K_{2})",
        "co(P_{2} U P_{4})",
        "co(C_{4} U P_{2})",
        "co(X_{70})",
        "X_{1}",
        "X_{70}",
        "co(X_{46})",
        "rising sun",
        "co-rising sun",
        "co(X_{1})",
        "X_{46}",
    ]
)
@assign_class_id("gc_578")
@lru_cache(maxsize=None)
def is_gc_578(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (3K_{2}, C_{4} U P_{2}, C_{5}, P_{2} U P_{4}, P_{5}, S_{3}, X_{1},
    X_{46}, X_{70}, co(3K_{2}), co(C_{4} U P_{2}), co(P_{2} U P_{4}), co(X_{1}), co(X_{46}),
    co(X_{70}), co-fish, co-rising sun, fish, house, net, rising sun)-free.

    See https://www.graphclasses.org/classes/gc_578

    Complexity: O(n^2) < O(n^7) (naïve)

    :type graph: networkx.Graph
    """
    # equivalent to Dilworth 2 https://www.graphclasses.org/classes/gc_335.html
    return is_dilworth_k(graph, 2)


@assign_fisc(["co-paw"])
@assign_class_id("gc_915")
@lru_cache(maxsize=None)
def is_co_paw_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is co-paw-free.

    See https://www.graphclasses.org/classes/gc_915

    Complexity: O(n^2) < O(n^4) (naïve)

    :type graph: networkx.Graph
    """
    # co-paw = K_1 U P_3, so graph is co-paw-free iff graph - v U N(v) is P_3-free for all choices of v
    return is_h_u_k1_free(graph, is_p3_free)


@assign_fisc(["co-diamond"])
@assign_class_id("AUTO_77")
@lru_cache(maxsize=None)
def is_co_diamond_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is co-diamond-free.

    See https://www.graphclasses.org/classes/AUTO_77

    Complexity: O(n^2) < O(n^4) (naïve)

    :type graph: networkx.Graph
    """
    # note: cannot move yet to fisc_based_recognizers because of circular import issues
    return is_h_free(graph, ["co-diamond"])
    # note: tried this, but it's much slower:
    # improved algorithm: G is co-diamond-free iff G - ({u, v} U N(u) U N(v)) is 2K_{1}-free for
    # every edge {u, v}
    # nodes = set(graph)
    # return all(
    #     undecorated_function(is_2k1_free)(graph.subgraph(nodes - set.union({u, v}, graph[u], graph[v])))
    #     for u, v in graph.edges
    # )


@assign_fisc(["co-gem"])
@assign_class_id("gc_423")
@lru_cache(maxsize=None)
def is_co_gem_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is co-gem-free.

    See https://www.graphclasses.org/classes/gc_423

    Complexity: O(n^2) < O(n^5) (naïve)
    :type graph: networkx.Graph
    """
    # if graph has no P_{4}, then it has no P_{4} U K_{1}
    if is_cograph(graph):
        return True

    # improved algorithm: G is co-gem-free iff G - ({u} U N(u)) is P_4-free for every vertex v
    return is_h_u_k1_free(graph, is_cograph)


@assign_fisc(
    [
        "co-gem",
        "co(C_{4})",
        "co(C_{5})",
        "co(C_{6})",
        "co(C_{7})",
        "co(C_{8})",
    ]
)
@assign_class_id("AUTO_2778")
@lru_cache(maxsize=None)
def is_co_chordal_and_co_gem_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_co_gem_free(graph) and is_co_chordal(graph)


# the fisc will be obtained through calls to constituent class recognizers
@assign_class_id("gc_248")
@lru_cache(maxsize=None)
def is_chordal_or_co_chordal(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    # split graphs are both chordal and co-chordal
    if is_split(graph):
        return True

    return is_chordal(graph) or is_co_chordal(graph)


# the fisc will be obtained through calls to constituent class recognizers
@assign_class_id("gc_1290")
@lru_cache(maxsize=None)
def is_bipartite_and_mock_threshold(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_bipartite(graph) and is_mock_threshold(graph)


# not profitable, but needed by a profitable class so included here to avoid circular import issues
@assign_class_id("gc_1195")
@lru_cache(maxsize=None)
def is_2_strongly_regular(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return len(set(degree_sequence(graph))) <= 2 and is_deza(graph)


# profitable because of planarity
@assign_class_id("gc_1196")
@lru_cache(maxsize=None)
def is_2_strongly_regular_and_planar(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_2_strongly_regular(graph) and is_planar(graph)


# not profitable, but needed by a profitable class so included here to avoid circular import issues
@assign_class_id("gc_1189")
@lru_cache(maxsize=None)
def is_deza(graph: nx.Graph) -> bool:
    """
    A Deza graph with parameters (𝜆,𝜇) is a graph such that any two adjacent vertices have exactly
    𝜆 common neighbors and any two nonadjacent vertices have exactly 𝜇 common neighbors.

    https://www.graphclasses.org/classes/gc_1189.html

    :param graph:
    :return:
    """
    # algo complexity: should be about O(|V|^4)
    # the following check would be more elegant; however, if the graph is
    # edge-regular, we need to recompute all neighborhoods again below; so let
    # us rather duplicate code for the sake of efficiency
    # if not is_edge_regular(graph):  # <- complexity: O(|E|)
    #     return False
    # necessary check to avoid StopIteration failure with call to non_edges
    n = graph.number_of_nodes()
    if graph.size() == (n * (n - 1)) // 2:
        return True

    if not graph.size():
        return True

    k = number_of_common_neighbors(graph, *next(iter(graph.edges)))

    # check that each pair of adjacent vertices has exactly k common neighbors
    # we cache the neighborhoods because we need sets and want to avoid a
    # number of calls to set proportional to the degree of each vertex
    neighbourhoods = dict()
    for u, v in graph.edges:
        if u not in neighbourhoods:
            neighbourhoods[u] = set(graph[u])
        if v not in neighbourhoods:
            neighbourhoods[v] = set(graph[v])

        if len(neighbourhoods[u] & neighbourhoods[v]) != k:
            return False

    p = number_of_common_neighbors(graph, *next(iter(nx.non_edges(graph))))

    # check that each pair of nonadjacent vertices has exactly p common
    # neighbors
    for u, v in nx.non_edges(graph):
        if u not in neighbourhoods:
            neighbourhoods[u] = set(graph.neighbors(u))
        if v not in neighbourhoods:
            neighbourhoods[v] = set(graph.neighbors(v))
        if len(neighbourhoods[u] & neighbourhoods[v]) != p:
            return False

    return True


# not profitable, but needed by a profitable class so included here to avoid circular import issues
@assign_class_id("gc_1185")
@lru_cache(maxsize=None)
def is_strongly_regular(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_1185.html

    @param graph:
    @return:
    """
    return nx.is_regular(graph) and is_deza(graph)


# not profitable, but needed by a profitable class so included here to avoid circular import issues
@assign_class_id("gc_1186")
@lru_cache(maxsize=None)
def is_distance_regular_of_diameter_2(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_1186.html

    @param graph:
    @return:
    """
    # first characterisation: O(n^4)
    # return nx.diameter(graph) == 2 and nx.is_distance_regular(graph)
    # second characterisation: O(n^2)
    return is_connected(graph) and is_strongly_regular(graph)


@assign_fisc(
    ["claw", "diamond", "C_{5}", "C_{7}"]
)  # partial fisc (odd hole = odd cycles of length >= 5)
@assign_class_id("gc_251")
@lru_cache(maxsize=None)
def is_line_graph_of_bipartite_graph(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_251.html

    @param graph:
    @return:
    """
    for cc in connected_components(graph):
        try:
            inverse = nx.inverse_line_graph(graph.subgraph(cc))
            if not is_bipartite(inverse):
                return False
        except nx.NetworkXError:
            return False
    return True


@assign_class_id("gc_1335")
@lru_cache(maxsize=None)
def is_line_graph_of_planar_cubic_bipartite_graph(graph: nx.Graph) -> bool:
    """
    https://www.graphclasses.org/classes/gc_1335.html

    @param graph:
    @return:
    """
    for cc in connected_components(graph):
        try:
            inverse = nx.inverse_line_graph(graph.subgraph(cc))
            if not (is_cubic(inverse) and is_bipartite(inverse) and is_planar(inverse)):
                return False
        except nx.NetworkXError:
            return False
    return True


@assign_fisc(
    ["W_{4}", "W_{5}", "W_{6}", "W_{7}"]
)  # class is equivalent to W_{n+4}-free graphs
@assign_class_id("gc_1251")
@lru_cache(maxsize=None)
def is_locally_chordal(graph: nx.Graph | HalfAdjacencyMatrix) -> bool:
    """
    A graph is locally chordal if the open neighborhood of each vertex induces a chordal graph.

    https://www.graphclasses.org/classes/gc_1251.html

    :param graph:
    :return:
    """
    for v in graph:
        subgraph = graph.subgraph(graph[v])
        # checking size is mandatory: is_chordal crashes on edgeless graphs
        if subgraph.size() and not is_chordal(subgraph):
            return False

    return True


@assign_fisc(
    [
        "co-claw",  # = C_{3} U K_{1}
        "co(W_{5})",  # = C_{5} U K_{1}
        "co(X_{108})",  # = C_{7} U K_{1}
    ]
)  # partial fisc based on equivalence with odd-cycle ∪ K1-free
@assign_class_id("gc_640")
@lru_cache(maxsize=None)
def is_nearly_bipartite(graph: nx.Graph | HalfAdjacencyMatrix) -> bool:
    """
    A graph G is nearly bipartite if for every node v, G-N[v] is bipartite.

    https://www.graphclasses.org/classes/gc_640.html

    Nearly bipartite graphs are equivalent to (odd-cycle U K_1)-free graphs. Since bipartite graphs
    are odd-cycle-free, bipartite graphs are also nearly bipartite, however strange this may read.

    :param graph:
    :return:
    """
    if is_bipartite(graph):
        return True

    if isinstance(graph, HalfAdjacencyMatrix):
        return all(is_bipartite(graph.subgraph(graph.non_neighbors(v))) for v in graph)

    return all(
        is_bipartite(graph.subgraph(nx.non_neighbors(graph, v))) for v in graph
    )  # note: why does replacing all(...) with is_h_u_k1_free(graph, is_bipartite) fail?


# the fisc will be obtained through calls to constituent class recognizers
@assign_class_id("gc_1293")
@lru_cache(maxsize=None)
def is_mock_threshold_and_split(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_split(graph) and is_mock_threshold(graph)


@assign_fisc(
    [
        # note: I don't know yet how tu "unpack" XF configurations, dropping them for now
        "co(C_{6})",
        "co(C_{7})",
        "co(C_{8})",
        "co(T_{2})",
        "co(X_{2})",
        "co(X_{3})",
        "co(X_{30})",
        "co(X_{31})",
        "co(X_{32})",
        "co(X_{33})",
        "co(X_{34})",
        "co(X_{35})",
        "co(X_{36})",
        "C_{5}",
        "C_{7}",
    ]
)  # partial fisc based on the equivalence with https://www.graphclasses.org/classes/gc_767.html
@assign_class_id("gc_72")
@lru_cache(maxsize=None)
def is_comparability(graph: nx.Graph | HalfAdjacencyMatrix) -> bool:
    """
    The following definitions are equivalent:

        1. G is a comparability if it transitively orientable, i.e. its edges can be directed such
            that if a->b and b->c are directed edges, then a->c is a directed edge.
        2. The comparability graph of a partial order (V,<=) has node set V and edge xy whenever
            x<=y or y<=x. G is a comparability if it is the comparability graph of some poset.

    https://www.graphclasses.org/classes/gc_72.html

    Note: adapted from SageMath's greedy_is_comparability ; (version from 2024-07-13)

    https://github.com/sagemath/sage/blob/develop/src/sage/graphs/comparability.pyx
    """
    # this is a lazy online implementation of sage's algorithm; the original implementation
    # consists of 3 steps:
    #
    #   1) build equivalence classes;
    #   2) use equivalence classes to build a graph H
    #   3) return True if H is bipartite, False otherwise.
    #
    # on large graphs, we don't even get past step 1; so we improve the algorithm as follows:
    #
    # - check H's bipartiteness online (i.e., as we examine its edge set), instead of actually
    #       building it and waiting for it to be complete to only then start checking whether it is
    #       bipartite
    # - only build the required equivalence classes as we go, i.e., only for the vertices for which
    #       this information is needed to obtain H's next edge, instead of waiting for the whole
    #       dictionary to be available
    classes = dict()
    non_twins = defaultdict(BitMap)

    def equiv_class_gen(v):
        """
        Returns the equivalence class of vertex v, which are the co-connected components of the
        subgraph induced by its neighbors.

        :param v:
        :return:
        """
        if v in classes:
            return classes[v]

        # computing classes[v] is expensive, so let's first check if v has a twin u for which we
        # have the answer already
        for u in set(classes).difference(non_twins[v]):
            if graph[v] == graph[u]:
                return classes[u]
            else:
                non_twins[v].add(u)
                non_twins[u].add(v)

        # using the non-cached co_connected_components function since we will likely have many
        # subgraphs and the answers will not be reused
        classes[v] = list(undecorated_function(co_connected_components)(graph.subgraph(graph[v])))
        return classes[v]

    def edge_generator():
        """
        Yields the edges of the graph that must be checked for bipartiteness in the original
        algorithm. This allows us to check bipartiteness as we go without building the whole graph.

        :return:
        """
        # instead of examining all edges once, we go through all vertices and examine all their
        # neighbors; in the worst case we examine each edge twice, but we hope to stop processing
        # the graph earlier that way and compute fewer classes
        # for u, v in graph.edges():
        for u in graph:
            for v in graph.neighbors(u):
                for i, s in enumerate(equiv_class_gen(v)):
                    if u in s:
                        break

                for j, s in enumerate(equiv_class_gen(u)):
                    if v in s:
                        break

                yield (v, i), (u, j)

    return online_is_bipartite(edge_generator())


# profitable because of constituent classes
@assign_class_id("gc_123")
@lru_cache(maxsize=None)
def is_chordal_and_comparability(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_chordal(graph) and is_comparability(graph)


@assign_class_id("AUTO_2774")
@lru_cache(maxsize=None)
def is_co_chordal_and_co_diamond_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_co_diamond_free(graph) and is_co_chordal(graph)


# equivalence with https://www.graphclasses.org/classes/gc_615.html yields this partial fisc:
@assign_fisc(
    [
        "3K_{2}",
        "4-fan",
        "5-pan",
        "A",
        "C_{4} U P_{2}",
        "C_{6}",
        "E",
        "K_{3,3}",
        "K_{3,3}-e",
        "P_{2} U P_{4}",
        "P_{6}",
        "W_{4}",
        "X_{106}",
        "X_{14}",
        "X_{15}",
        "X_{18}",
        "X_{1}",
        "X_{200}",
        "X_{34}",
        "X_{42}",
        "X_{45}",
        "X_{58}",
        "X_{89}",
        "X_{90}",
        "X_{97}",
        "antenna",
        "co(2P_{3})",
        "co(A)",
        "co(C_{4} U 2K_{1})",
        "co(C_{5})",
        "co(C_{6})",
        "co(C_{7})",
        "co(H)",
        "co(P_{3} U P_{4})",
        "co(P_{6})",
        "co(P_{7})",
        "co(T_{2})",
        "co(X_{127})",
        "co(X_{134})",
        "co(X_{166})",
        "co(X_{169})",
        "co(X_{170})",
        "co(X_{173})",
        "co(X_{176})",
        "co(X_{197})",
        "co(X_{198})",
        "co(X_{27})",
        "co(X_{2})",
        "co(X_{30})",
        "co(X_{32})",
        "co(X_{33})",
        "co(X_{36})",
        "co(X_{37})",
        "co(X_{38})",
        "co(X_{39})",
        "co(X_{41})",
        "co(X_{46})",
        "co(X_{70})",
        "co(star_{1,2,3})",
        "co-eiffeltower",
        "co-longhorn",
        "co-twin-house",
        "domino",
        "gem",
        "net",
        "rising sun",
        "twin-C_{5}",
    ]
)
@assign_class_id("gc_316")
@lru_cache(maxsize=None)
def is_strict_2_threshold(graph: nx.Graph) -> bool:
    """
    A graph is a strict 2-threshold graph if its edge-set can be partitioned into two threshold
    graphs A and B such that every triangle of G is a triangle of A or a triangle of B.

    https://www.graphclasses.org/classes/gc_316.html

    Complexity: O(m) < O(n^7) (naive)

    :param graph:
    :return:
    """

    # algorithm from https://twiki.di.uniroma1.it/pub/Users/AndreaSterbini/Ricerca/11-IPL-1995.pdf
    # page 196 (see also https://doi.org/10.1016/0020-0190(95)00030-G)
    def c_and_t2_subgraphs(t1: nx.Graph) -> tuple[nx.Graph, nx.Graph]:
        """
        Returns subgraphs C and T_2 as defined in the paper.

        :param t1:
        :return:
        """
        # extract subgraph C from t1_subgraph, induced by vertices with degree in t1_subgraph
        # different from degree in graph
        c = t1.subgraph(w for w, deg in t1.degree if deg != graph.degree[w])

        # t2 is induced by vertices not in t1_subgraph and vertices in c
        t2 = graph.subgraph((set(graph.nodes) - set(t1.nodes)).union(c.nodes))

        return c, t2

    # Phase 1:
    # extract subgraph t1_subgraph induced by a vertex of max degree and its neighbors
    if not graph.nodes:  # avoid crash if graph is empty
        return True

    max_degree = degree_sequence(graph)[0]
    for x, d in graph.degree:
        if d == max_degree:
            break

    t1_subgraph = graph.subgraph({x}.union(graph[x]))
    c_subgraph, t2_subgraph = c_and_t2_subgraphs(t1_subgraph)

    if is_threshold(t1_subgraph) and is_threshold(t2_subgraph) and is_empty(c_subgraph):
        return True

    # Phase 2
    # select a neighbor y of x of maximum degree in original graph, and build t1_subgraph as before
    # based on y: i.e., t1_subgraph is induced by y and its neighbors
    max_deg = 0
    y = None
    for v in graph[x]:
        if graph.degree[v] > max_deg:
            max_deg = graph.degree[v]
            y = v

    # add to t1_subgraph the neighbors of x of degree 1 in original graph
    t1_subgraph = graph.subgraph(
        {y}.union(graph[y]).union(leaf for leaf in graph[x] if graph.degree[leaf] == 1)
    )

    # compute c_subgraph and t2_subgraph as before, and return True iff the same tests on all three
    # subgraphs succeed
    c_subgraph, t2_subgraph = c_and_t2_subgraphs(t1_subgraph)
    return is_threshold(t1_subgraph) and is_threshold(t2_subgraph) and is_empty(c_subgraph)


# I'll specify a partial fisc here because is_co_forest is not a recognizer so its attached fisc
# is not taken advantage of.


# -------------------------------------------------------------------------------------------------
# The following recognizers call another recognizer on the complement of the input graph. Since
# building the complement can be time- and memory-consuming on large instances, and since
# recognizers are loaded in the order in which they appear in a recognizer file, those recognizers
# should stay at the end of the file in the hope that they are not actually needed until we figure
# out a way to bypass the computation of the complement.
# -------------------------------------------------------------------------------------------------
# NOTE: the FISC is partial, since we cannot account for everything covered by infinite
# configurations (here: co(C_{n+4}))
@assign_fisc(
    [
        "co(C_{4})",  # = 2K_{2}
        "C_{5}",
        "co(C_{5})",
        "co(C_{6})",
        "co(C_{7})",
        "co(C_{8})",
    ]
)
@assign_class_id("gc_145")
@lru_cache(maxsize=None)
def is_co_chordal(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is co-chordal.

    https://www.graphclasses.org/classes/gc_145.html

    Complexity: O(n^2) (computing the complement).

    @param graph:
    @return:
    """
    # iterate over co-connected components instead of complementing the whole graph, in the hope
    # that we can thereby stop early
    # if graph is co-chordal, its complement contains no C_4, C_5, C_6, C_7, C_8, and therefore
    # the original graph cannot contain the complements of these configurations
    if not is_2k2_free(graph):
        return False

    # note: we can still check 'or not is_h_free(graph, ["C_{5}", "co(C_{6})", "co(C_{7})", "co(C_{8})"])'
    # but that is much slower

    # split graphs are both chordal and co-chordal, so let's try that first if it allows us to
    # avoid examining co-connected components
    return is_split(graph) or all(
        is_chordal(complement_as_adj_mat(graph, cc)) for cc in co_connected_components(graph)
    )


# FISC derived from the complements of is_planar's FISC
@assign_fisc(
    [
        "2K_{3}",  # complement of "K_{3,3}",
        "X_{86}",  # complement of "co(X_{86})",
        "5K_{1}",  # complement of "K_{5}",
        "co(X_{46})",  # complement of "X_{46}",
        "K_{2} U claw",  # complement of "co(K_{2} U claw)",
        "X_{120}",  # complement of "co(X_{120})"
    ]
)
@assign_class_id("gc_953")
@lru_cache(maxsize=None)
def is_co_planar(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_953.html

    @param graph:
    @return:
    """
    # if complement has too many edges, then it cannot be planar
    n = graph.number_of_nodes()
    if n >= 3 and (n * (n - 1)) // 2 - graph.size() > 3 * n - 6:
        return False

    # https://pjm.ppu.edu/sites/default/files/papers/PJM_May_2022_575_to_581.pdf
    # the complement of C_k with k >= 7 odd is not planar, so if graph has such
    # a cycle we can return False immediately
    # of course we should check all odd cycle lengths ...
    # NOTE: this check would be useful, but right now it creates a circular import issue
    # moreover, this would yield a running time of O(n^7)
    # if not is_h_free(graph, ["C_{7}"]):
    #    return False

    # iterate over co-connected components instead of complementing the whole graph, in the hope
    # that we can thereby stop early
    return all(is_planar(complement(graph.subgraph(cc))) for cc in co_connected_components(graph))


@assign_fisc(
    ["co(W_{4})", "co(W_{5})", "co(W_{6})", "co(W_{7})"]
)  # fisc derived from complement class
@assign_class_id("AUTO_2465")
@lru_cache(maxsize=None)
def is_co_locally_chordal(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    # iterate over co-connected components instead of complementing the whole graph, in the hope
    # that we can thereby stop early
    return all(
        is_locally_chordal(complement_as_adj_mat(graph, cc)) for cc in co_connected_components(graph)
    )


@assign_fisc(
    [
        "co-claw",
        "P_{2} U P_{3}",
        "co(K_{5} - e)",
        "co(W_{5})",
        "twin-C_{5}",
        "R",
        "twin-house",
        "A",
        "C_{4} U 2K_{1}",
    ]
)
@assign_class_id("gc_970")
@lru_cache(maxsize=None)
def is_co_line(graph: nx.Graph) -> bool:
    """
    A graph whose complement is a line graph.

    https://www.graphclasses.org/classes/gc_970.html

    :param graph:
    :return:
    """
    # iterate over co-connected components instead of complementing the whole graph, in the hope
    # that we can thereby stop early
    # note: complement_as_adj_mat not usable here yet
    for cc in co_connected_components(graph):
        try:
            nx.inverse_line_graph(complement(graph.subgraph(cc)))
        except nx.NetworkXError:
            return False

    return True


@assign_fisc(["co-claw", "co-diamond", "C_{5}", "co(C_{7})"])  # fisc derived from complement class
@assign_class_id("gc_744")
@lru_cache(maxsize=None)
def is_co_line_graph_of_bipartite_graph(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_744.html

    @param graph:
    @return:
    """
    # iterate over co-connected components instead of complementing the whole graph, in the hope
    # that we can thereby stop early
    # note: complement_as_adj_mat not yet usable here
    return all(
        is_line_graph_of_bipartite_graph(complement(graph.subgraph(cc)))
        for cc in co_connected_components(graph)
    )


@assign_fisc(
    [
        "claw",  # = complement of "co-claw",
        "W_{5}",  # = complement of C_{5} U K_{1}
        "X_{108}",  # = complement of C_{7} U K_{1}
    ]
)  # partial fisc based on equivalence with odd-cycle ∪ K1-free
@assign_class_id("gc_879")
@lru_cache(maxsize=None)
def is_quasi_line(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    # iterate over co-connected components instead of complementing the whole graph, in the hope
    # that we can thereby stop early
    return all(
        is_nearly_bipartite(complement_as_adj_mat(graph, cc))
        for cc in co_connected_components(graph)
    )


# partial fisc derived from the complement:


@assign_fisc(
    [
        "co-butterfly",  # C_4 U K_1
        "co(W_{5})",  # C_5 U K_1
        "co(X_{108})",  # C_7 U K_1
    ]
)  # partial fisc, ISGCI doesn't know all (C_{n+4} U K_{1})-free graphs
@lru_cache(maxsize=None)
def is_c_n_plus_4_u_k_1_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (Cn+4 ∪ K1)-free. Not a class in itself, but used to define several
    other classes.

    Complexity: O(n^2).

    @param graph:
    @return:
    """
    # if graph is chordal, then it has no C_{n+4}, and therefore no C_{n+4} U K1
    if is_chordal(graph):
        return True

    # very naive algo: graph is (C_{n+4} ∪ K1)-free if removing a vertex and its neighborhood always
    # yields a C_{n+4}-free (i.e., chordal) graph
    nodes = set(graph)
    return all(is_chordal(graph.subgraph(nodes - {v}.union(graph[v]))) for v in graph)


@assign_fisc(["co-diamond", "co-paw", "P_{4}"])
@assign_class_id("AUTO_1939")
@lru_cache(maxsize=None)
def is_p4_co_diamond_co_paw_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{4}, co-diamond, co-paw)-free.

    See https://www.graphclasses.org/classes/AUTO_1939

    Complexity: O(n^2) < O(n^4) (naïve)

    :type graph: networkx.Graph
    """
    return is_cograph(graph) and is_co_paw_free(graph) and is_co_diamond_free(graph)


@assign_fisc(["2K_{2}", "P_{4}", "co-diamond", "co-paw"])
@assign_class_id("AUTO_1940")
@lru_cache(maxsize=None)
def is_auto_1940(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, P_{4}, co-diamond, co-paw)-free.

    See https://www.graphclasses.org/classes/AUTO_1940

    Complexity: O(n^2) < O(n^4) (naïve)

    @param graph:
    @return:
    """
    return (
            is_cograph(graph)
            and is_2k2_free(graph)
            and is_co_diamond_free(graph)
            and is_co_paw_free(graph)
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
