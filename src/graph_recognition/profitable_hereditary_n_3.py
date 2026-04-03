"""
Anthony Labarre © 2023-2026

This file contains recognizers for profitable hereditary classes, i.e. classes that admit a
forbidden induced subgraph characterization, but can be recognized with a faster-than-naïve
algorithm.

Recognizers in this file have running time O(n^3).

"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
import os
from functools import lru_cache
from itertools import combinations
from typing import Hashable

# ----- Third-party imports -----------------------------------------------------------------------
import networkx as nx

# ----- My imports --------------------------------------------------------------------------------
from graph_recognition.misc_algo import (
    complement,
    is_connected,
    is_h_u_k2_free,
    co_connected_components, complement_as_adj_mat,
)
from graph_recognition.profitable_hereditary_n import (
    is_gc_1312,
    is_bipartite,
    is_chordal,
    is_cograph,
    is_maximum_degree_4,
    is_maximum_degree_3,
    is_co_maximum_degree_3,
    is_planar_and_maximum_degree_3,
    is_planar,
    is_co_bipartite,
    is_maximum_degree_7,
    is_split,
)
from graph_recognition.profitable_hereditary_n_2 import is_co_paw_free
from graph_recognition.recognizers_utils import (
    current_module_recognizers,
    assign_class_id,
    assign_fisc,
)

# check whether function has already been lru_cached
if not hasattr(nx.asteroidal.create_component_structure, "cache_info"):
    setattr(
        nx.asteroidal,
        "create_component_structure",
        lru_cache(maxsize=None)(nx.asteroidal.create_component_structure),
    )


# Recognizers -------------------------------------------------------------------------------------
@assign_fisc(["paw"])
@assign_class_id("gc_357")
@lru_cache(maxsize=None)
def is_paw_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is paw-free.

    See https://www.graphclasses.org/classes/gc_357

    Complexity: O(mn) < O(n^4) (naïve)

    :type graph: networkx.Graph
    """
    # Every connected component of a paw-free graph is triangle-free or complete multipartite
    # (=co(P_3)-free)
    return all(
        is_triangle_free(cc) or is_co_p3_free(cc)
        for cc in map(graph.subgraph, nx.connected_components(graph))
    )


@assign_fisc(["2K_{2}", "3K_{1}", "P_{3}"])
@assign_class_id("gc_1308")
@lru_cache(maxsize=None)
def is_gc_1308(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, 3K_{1}, P_{3})-free.

    See https://www.graphclasses.org/classes/gc_1308

    Complexity: O(mn) < O(n^4) (naïve)

    :type graph: networkx.Graph
    """
    #      (2K_{2}, P_{3})       3K_{1}
    return is_gc_1312(graph) and is_3k1_free(graph)


@assign_fisc(["triangle", "K_{1,5}"])
@assign_class_id("gc_921")
@lru_cache(maxsize=None)
def is_gc_921(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{1, 5}, triangle)-free.

    See https://www.graphclasses.org/classes/gc_921

    Complexity: O(mn) < O(n^6) (naïve)

    :type graph: networkx.Graph
    """
    # equivalent to maximum degree 4 AND triangle-free
    return is_maximum_degree_4(graph) and is_triangle_free(graph)


@assign_fisc(["diamond", "claw"])
@assign_class_id("gc_709")
@lru_cache(maxsize=None)
def is_claw_diamond_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (claw, diamond)-free.

    See https://www.graphclasses.org/classes/gc_709

    Complexity: O(n^3) < O(n^4) (naïve)

    :type graph: networkx.Graph
    """
    # equivalent to line graphs of triangle-free graphs
    # https://www.graphclasses.org/classes/gc_708.html
    # inverting disconnected graphs does not work, we have to examine each component separately
    for cc in nx.connected_components(graph):
        try:
            is_triangle_free(nx.inverse_line_graph(graph.subgraph(cc)))

        except nx.NetworkXError:  # graph is not a line graph
            return False

    return True


@assign_fisc(["triangle"])
@assign_class_id("gc_371")
@lru_cache(maxsize=None)
def is_triangle_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is triangle-free.

    See https://www.graphclasses.org/classes/gc_371

    Complexity: O(mn) <= O(n^3) (naïve)

    :type graph: networkx.Graph
    """
    # Mantel's theorem: a triangle-free graph on n vertices cannot have more than ⌊n²/4⌋ edges
    if graph.number_of_edges() > graph.number_of_nodes() ** 2 // 4:
        return False

    # for each vertex, go through its neighbors; if any two of them are adjacent, then we have a
    # triangle
    contains_triangle = not is_bipartite(graph) and any(
        graph.has_edge(v, w) for u in graph for v, w in combinations(graph[u], 2)
    )

    return not contains_triangle


@assign_fisc(["co(P_{3})"])
@assign_class_id("gc_1271")
@lru_cache(maxsize=None)
def is_co_p3_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is co(P_{3})-free.

    See https://www.graphclasses.org/classes/gc_1271

    Complexity: O(mn) <= O(n^3) (naïve)

    :type graph: networkx.Graph
    """
    # for each vertex v, check whether G contains an edge whose endpoints are
    # independent of v
    has_co_p3 = any(
        graph.has_edge(v, w)
        for u in graph
        for v, w in combinations(nx.non_neighbors(graph, u), 2)
    )

    return not has_co_p3


@assign_fisc(["3K_{1}"])
@assign_class_id("gc_1378")
@lru_cache(maxsize=None)
def is_3k1_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is 3K_{1}-free.

    See https://www.graphclasses.org/classes/gc_1378

    Complexity: O(mn) <= O(n^3) (naïve)

    :type graph: networkx.Graph
    """
    # for each pair of independent vertices, check whether they have a common
    # non-neighbor; careful, v is also a non-neighbor of w and must be ignored
    has_3k_1 = any(
        not graph.has_edge(v, w)
        for u, v in nx.non_edges(graph)
        for w in nx.non_neighbors(graph, u)
        if w != v
    )
    return not has_3k_1


@assign_class_id("gc_234")
@lru_cache(maxsize=None)
def is_interval(graph: nx.Graph) -> bool:
    """
    Complexity is O(n^3), since:

        is_chordal: O(n + m)
        is_at_free: O(nm' + nm), where m' is the number of non-edges (= O(n^3))

    See https://www.graphclasses.org/classes/gc_234

    @param graph:
    @return:
    """
    return is_chordal(graph) and my_is_at_free(graph)


# NOTE: the FISC is partial, since we cannot account for everything covered by infinite
# configurations (e.g. C_{n+6})
@assign_fisc(
    [
        "T_{2}",
        "X_{2}",
        "X_{3}",
        "X_{30}",
        "X_{31}",
        "X_{32}",
        "X_{33}",
        "X_{34}",
        "X_{35}",
        "X_{36}",
        "X_{37}",
        "X_{38}",
        "X_{39}",
        "X_{40}",
        "X_{41}",
        # "unpacking" C_{n+6}:
        "C_{6}",
        "C_{7}",
        "C_{8}",
        # "unpacking" XF_{2n+1}: (info taken from smallgraphs page)
        "net",  # = XF_2^1
        # "unpacking" XF_{3n}: (info taken from smallgraphs page)
        "S_{3}",  # = XF_3^0
        "rising sun",  # = XF_3^1
        # "unpacking" XF_{4n}: (info taken from smallgraphs page)
        "co-antenna",  # = XF_4^0
        "co(X_{35})",  # = XF_4^1
    ]
)
@assign_class_id("gc_61")
@lru_cache(maxsize=None)
def my_is_at_free(graph: nx.Graph) -> bool:
    """
    Improved version of nx.is_at_free, see https://github.com/networkx/networkx/pull/7736 for
    details.

    See https://www.graphclasses.org/classes/gc_61

    Complexity: O(n^3).

    @param graph:
    @return:
    """
    # adapted copy paste of nx.asteroidal.find_asteroidal_triple; besides improvements as described
    # in the pull request, we return True instead of None if no asteroidal triple was found, and
    # False instead of an asteroidal triple otherwise.
    nodes = set(graph)

    if len(nodes) < 6:
        # An asteroidal triple cannot exist in a graph with less than 6 vertices.
        return True

    @lru_cache(maxsize=None)
    def my_component_structure(w: Hashable):
        """
        An attempt at writing a more efficient component_structure computation function than what
        networkx has to offer. Instead of computing the whole component structure, we just compute
        the values for each node as we go.

        :return:
        """
        closed_neighborhood = {w}.union(graph[w])
        row_dict = dict.fromkeys(closed_neighborhood, 0)
        graph_reduced = graph.subgraph(set(graph) - closed_neighborhood)
        # note: this is probably doable online, but I'm not sure whether singletons should be
        # included, and at the moment online_connected_components doesn't provide that.
        for label, cc in enumerate(nx.connected_components(graph_reduced), 1):
            for x in cc:
                row_dict[x] = label

        return row_dict


    # component_structure = nx.asteroidal.create_component_structure(graph)

    for u, v in nx.non_edges(graph):
        # Check for each pair of vertices whether they belong to the same connected component when
        # the closed neighborhood of the third is removed.
        if any(
                my_component_structure(u)[v] == my_component_structure(u)[w]
                and my_component_structure(v)[u] == my_component_structure(v)[w]
                and my_component_structure(w)[u] == my_component_structure(w)[v]
#                component_structure[u][v] == component_structure[u][w]
#                and component_structure[v][u] == component_structure[v][w]
#                and component_structure[w][u] == component_structure[w][v]
                for w in nodes - set(graph[u]).union(graph[v], [u, v])
        ):
            return False

    return True


@assign_fisc(["P_{2} U P_{4}"])
@assign_class_id("gc_930")
@lru_cache(maxsize=None)
def is_p2up4_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is P_{2} U P_{4}-free.

    See https://www.graphclasses.org/classes/gc_930

    Complexity: O(n^3) < O(n^6) (naïve)

    :type graph: networkx.Graph
    """
    # let's first check whether there is a P_{4}: if not, there won't be a P_{2} U P_{4} either
    return is_cograph(graph) or is_h_u_k2_free(graph, is_cograph)


@assign_fisc(["triangle", "P_{4}"])
@assign_class_id("gc_1270")
@lru_cache(maxsize=None)
def is_gc_1270(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{4}, triangle)-free.

    See https://www.graphclasses.org/classes/gc_1270

    Complexity: O(n(m+n)) <= O(n^3) < O(n^4) (naïve)

    :type graph: networkx.Graph
    """
    return is_cograph(graph) and is_triangle_free(graph)


@assign_fisc(["triangle", "P_{2} U P_{4}"])
@assign_class_id("gc_923")
@lru_cache(maxsize=None)
def is_gc_923(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{2} U P_{4}, triangle)-free.

    See https://www.graphclasses.org/classes/gc_923

    Complexity: O(n^3) < O(n^6) (naïve)

    :type graph: networkx.Graph
    """
    return is_triangle_free(graph) and is_p2up4_free(graph)


@assign_fisc(["triangle", "C_{4}", "C_{5}", "C_{6}", "C_{7}", "C_{8}"])
@assign_class_id("gc_1225")
@lru_cache(maxsize=None)
def is_girth_at_least_9(graph: nx.Graph) -> bool:
    """

    See https://www.graphclasses.org/classes/gc_1225

    @param graph:
    @return:
    """
    return nx.girth(graph) >= 9


@assign_fisc(
    ["W_{5}", "W_{7}"]
)  # partial fisc, since we cannot account for infinite configurations
@assign_class_id("gc_1262")
@lru_cache(maxsize=None)
def is_locally_bipartite(graph: nx.Graph) -> bool:
    """
    A graph is locally bipartite if the open neighborhood of each vertex induces a bipartite graph.

    See https://www.graphclasses.org/classes/gc_1262

    :param graph:
    :return:
    """
    return all(is_bipartite(graph.subgraph(graph[v])) for v in graph)


# the fisc will be obtained through calls to constituent class recognizers
@assign_class_id("AUTO_741")
@lru_cache(maxsize=None)
def is_xc11_claw_diamond_free(graph: nx.Graph) -> bool:
    """

    See https://www.graphclasses.org/classes/AUTO_741

    @param graph:
    @return:
    """
    return is_maximum_degree_4(graph) and is_claw_diamond_free(graph)


# profitable from constituent classes
@assign_class_id("AUTO_849")
@lru_cache(maxsize=None)
def is_xc_12_triangle_free(graph: nx.Graph) -> bool:
    """

    See https://www.graphclasses.org/classes/AUTO_849

    @param graph:
    @return:
    """
    return is_maximum_degree_3(graph) and is_triangle_free(graph)


# profitable from constituent classes
@assign_class_id("AUTO_3254")
@lru_cache(maxsize=None)
def is_3k_1_co_xc_12_free(graph: nx.Graph) -> bool:
    """

    See https://www.graphclasses.org/classes/AUTO_3254

    @param graph:
    @return:
    """
    return is_co_maximum_degree_3(graph) and is_3k1_free(graph)


# profitable from constituent classes
@assign_class_id("gc_1274")
@lru_cache(maxsize=None)
def is_maximum_degree_3_and_planar_and_triangle_free(graph: nx.Graph) -> bool:
    """

    See https://www.graphclasses.org/classes/gc_1274

    @param graph:
    @return:
    """
    return is_planar_and_maximum_degree_3(graph) and is_triangle_free(graph)


# profitable from constituent classes
@assign_class_id("gc_869")
@lru_cache(maxsize=None)
def is_planar_and_triangle_free(graph: nx.Graph) -> bool:
    """

    See https://www.graphclasses.org/classes/gc_869

    @param graph:
    @return:
    """
    return is_planar(graph) and is_triangle_free(graph)


# profitable from constituent classes
@assign_class_id("gc_885")
@lru_cache(maxsize=None)
def is_co_bipartite_and_proper_circular_arc(graph: nx.Graph) -> bool:
    """

    See https://www.graphclasses.org/classes/gc_885

    @param graph:
    @return:
    """
    return is_co_bipartite(graph) and is_co_at_free(graph)


@assign_fisc(["paw"])
@assign_class_id("gc_278")
@lru_cache(maxsize=None)
def is_paw_free_and_perfect(graph: nx.Graph) -> bool:
    """
    A graph G is paw-free ∩ perfect iff each component of G is bipartite or complete multipartite.

    See https://www.graphclasses.org/classes/gc_278

    :param graph:
    :return:
    """
    return all(
        is_bipartite(cc) or is_co_p3_free(cc)
        for cc in map(graph.subgraph, nx.connected_components(graph))
    )


@assign_fisc(["paw", "co-paw"])
@assign_class_id("gc_514")
@lru_cache(maxsize=None)
def is_gc_514(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co-paw, paw)-free.

    See https://www.graphclasses.org/classes/gc_514

    Complexity: O(mn) < O(n^4) (naïve)

    :type graph: networkx.Graph
    """
    return is_co_paw_free(graph) and is_paw_free(graph)


@assign_class_id("gc_852")
@lru_cache(maxsize=None)
def is_gc_852(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (3K_{1}, P_{4})-free.

    See https://www.graphclasses.org/classes/gc_852

    Complexity: O(mn) < O(n^4) (naïve)

    :type graph: networkx.Graph
    """
    return is_cograph(graph) and is_3k1_free(graph)


@assign_class_id("AUTO_1444")
@lru_cache(maxsize=None)
def is_auto_1444(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (3K_{1}, paw)-free.

    See https://www.graphclasses.org/classes/AUTO_1444

    Complexity: O(mn) < O(n^4) (naïve)

    :type graph: networkx.Graph
    """
    return is_paw_free(graph) and is_3k1_free(graph)


@assign_fisc(
    [
        "3K_{1}",
        "P_{3}",
        "co(P_{3})",
    ]
)  # fisc obtained by computing the basis of all non locally connected smallgraphs
@assign_class_id("gc_932")
@lru_cache(maxsize=None)
def is_locally_connected(graph: nx.Graph) -> bool:
    """
    A graph G is locally connected iff for every vertex v, the open neighborhood N(v) of v induces
    a connected graph in G.

    Note that disconnected graphs can be locally connected (e.g. disjoint union of cliques).

    https://www.graphclasses.org/classes/gc_932

    :param graph:
    :return:
    """
    return all(is_connected(graph.subgraph(graph[v])) for v in graph)


@assign_class_id("gc_1094")
@lru_cache(maxsize=None)
def is_locally_connected_and_maximum_degree_4(graph: nx.Graph) -> bool:
    """

    See https://www.graphclasses.org/classes/gc_1094

    @param graph:
    @return:
    """
    return is_maximum_degree_4(graph) and is_locally_connected(graph)


@assign_class_id("gc_1091")
@lru_cache(maxsize=None)
def is_locally_connected_and_maximum_degree_7(graph: nx.Graph) -> bool:
    """

    See https://www.graphclasses.org/classes/gc_1091

    @param graph:
    @return:
    """
    return is_maximum_degree_7(graph) and is_locally_connected(graph)


@assign_class_id("gc_926")
@lru_cache(maxsize=None)
def is_gc_926(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co-paw, triangle)-free.

    See https://www.graphclasses.org/classes/gc_926

    Complexity: O(n^3) < O(n^4) (naïve)

    :type graph: networkx.Graph
    """
    return is_co_paw_free(graph) and is_triangle_free(graph)


@assign_class_id("gc_1305")
@lru_cache(maxsize=None)
def is_gc_1305(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, C_{4}, C_{5}, claw, diamond)-free.

    See https://www.graphclasses.org/classes/gc_1305

    Complexity: O(n^3) < O(n^5) (naïve)

    :type graph: networkx.Graph
    """
    return is_split(graph) and is_claw_diamond_free(graph)


# -------------------------------------------------------------------------------------------------
# The following recognizers call another recognizer on the complement of the input graph. Since
# building the complement can be time- and memory-consuming on large instances, and since
# recognizers are loaded in the order in which they appear in a recognizer file, those recognizers
# should stay at the end of the file in the hope that they are not actually needed until we figure
# out a way to bypass the computation of the complement.
# -------------------------------------------------------------------------------------------------
@assign_fisc(
    [
        "co(C_{6})",
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
        "co(X_{37})",
        "co(X_{38})",
        "co(X_{39})",
        "co(X_{40})",
        "co(X_{41})",
    ]
)  # partial fisc, since we cannot account for all infinite configurations
@assign_class_id("AUTO_2127")
@lru_cache(maxsize=None)
def is_co_at_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_2127.html

    @param graph:
    @return:
    """
    # iterate over co-connected components instead of complementing the whole graph, in the hope
    # that we can thereby stop early
    return all(
        my_is_at_free(complement_as_adj_mat(graph.subgraph(cc))) for cc in co_connected_components(graph)
    )


@assign_fisc(
    ["co(W_{5})", "co(W_{7})"]
)  # partial fisc, since we cannot account for infinite configurations
@assign_class_id("AUTO_2467")
@lru_cache(maxsize=None)
def is_co_locally_bipartite(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_2467.html

    @param graph:
    @return:
    """
    # iterate over co-connected components instead of complementing the whole graph, in the hope
    # that we can thereby stop early
    return all(
        is_locally_bipartite(complement(graph.subgraph(cc)))
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
