"""
Anthony Labarre © 2023-2026

O(n^5) algorithms.

"""

# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
import os
from functools import lru_cache
from typing import Iterable, Hashable

# ----- Third-party imports -----------------------------------------------------------------------
import networkx as nx
from pyroaring import BitMap

# ----- My imports --------------------------------------------------------------------------------
from graph_recognition.directed_graph import DirectedGraph
from graph_recognition.fisc_based_recognizers_n_4 import is_co_claw_free, is_claw_free
from graph_recognition.fisc_based_recognizers_n_5 import (
    is_p5_bull_free,
    is_gc_917,
    is_gc_574,
    is_p_free,
    is_co_p_free,
    is_p5_free,
    is_co_fork_free,
    is_house_free,
    is_gem_free,
    is_k23_free,
    is_bull_free,
    is_fork_free,
    is_gc_628,
    is_k14_free, is_xc_10_free, is_chordal_and_gem_free, is_k2_u_k3_free,
)
from graph_recognition.misc_algo import (
    empty_graph_by_removing_edges_and_incident_edges,
    is_h_u_2k1_free,
    is_h_u_k2_free,
    is_odd_co_clique_free,
    explicit_triangles,
    empty_graph_by_removing_vertices,
    common_neighbors, induced_subgraph_degrees, enumerate_all_p4_midpoints,
    neighbors, non_neighbors,
)
from graph_recognition.profitable_hereditary_n import (
    is_complete_bipartite,
    is_bipartite,
    is_chordal,
    is_planar,
    is_co_bipartite,
    is_p3_free,
    is_split_degree_sequence,
)
from graph_recognition.profitable_hereditary_n_2 import is_co_chordal, is_co_gem_free
from graph_recognition.profitable_hereditary_n_3 import (
    is_triangle_free,
    is_locally_connected,
)
from graph_recognition.profitable_hereditary_n_4 import (
    is_hole_free,
    is_anti_hole_free,
)
from graph_recognition.recognizers_n_3 import is_weakly_modular
from graph_recognition.recognizers_n_4 import is_almost_claw_free
from graph_recognition.recognizers_utils import (
    assign_class_id,
    current_module_recognizers, assign_inherited_fisc,
)
from graph_recognition.subgraphs import is_h_free
from graph_recognition.two_sat import Not, satisfiable


# Auxiliary functions -----------------------------------------------------------------------------
@lru_cache(maxsize=None)
def edge_is_bisimplicial(graph: nx.Graph, edge: Iterable) -> bool:
    """
    An edge (u, v) in a bipartite graph B is called bisimplicial if N(u) U N(v) induces a biclique
    in B.

    :param edge:
    :param graph:
    :return:
    @param graph:
    @param edge:
    """
    u, v = edge
    return is_complete_bipartite(graph.subgraph(set(graph[u]).union(graph[v])))


# Recognizers -------------------------------------------------------------------------------------
@assign_inherited_fisc()
@assign_class_id("gc_122")
@lru_cache(maxsize=None)
def is_perfect_elimination_bipartite(graph: nx.Graph) -> bool:
    """
    An edge (𝑢,𝑣) in a bipartite graph 𝐵 is called bisimplicial if 𝑁(𝑢)∪𝑁(𝑣) induces a biclique in
    𝐵. For an edge ordering 𝑒1…𝑒𝑘 let 𝑆𝑖 be the set of endpoints of 𝑒1…𝑒𝑖 and 𝑆0=∅. 𝑒1…𝑒𝑘 is a
    perfect edge elimination ordering for a bipartite graph 𝐵=(𝑉,𝐸) if 𝐵[𝑉∖𝑆𝑘] has no edges, and
    each edge 𝑒𝑖 is bisimplicial in 𝐵[𝑉∖𝑆𝑖−1]. 𝐵 is perfect elimination bipartite if it admits a
    perfect edge elimination ordering.

    https://www.graphclasses.org/classes/gc_122

    Example from https://doi.org/10.1016/0020-0190(82)90101-6:
    >>> import networkx; G = networkx.Graph()
    >>> G.add_edges_from([("x1", "y1"), ("x1", "y2"), ("x2", "y1"), ("x2", "y2"), ("x2", "y3"), \
            ("x3", "y2"), ("x3", "y3"), ("x3", "y4"), ("x4", "y3"), ("x4", "y4")])
    >>> is_perfect_elimination_bipartite(G)
    True

    :param graph:
    :return:
    """
    # naive algorithm described in https://doi.org/10.1016/0020-0190(82)90101-6: repeatedly find
    # and delete a bisimplicial edge from G; G is PEB iff the resulting graph is edgeless
    return is_bipartite(graph) and empty_graph_by_removing_edges_and_incident_edges(
        graph, edge_is_bisimplicial
    )


@assign_class_id("gc_54")
@lru_cache(maxsize=None)
def is_clique_helly(graph: nx.Graph) -> bool:
    """
    The following definitions are equivalent:

    1. An extended triangle of G is the subgraph induced by a triangle T together with all vertices
        that are adjacent to at least two vertices of T. A graph is clique-Helly iff every of its
        extended triangles contains a universal vertex.

    2. The clique hypergraph of G has V(G) as its vertices and the cliques (maximal complete
        subgraphs) of G as its hyperedges. A graph is clique-Helly iff its clique hypergraph has
        the Helly property.

    https://www.graphclasses.org/classes/gc_54.html

    @param graph:
    @return:
    """
    if is_triangle_free(graph):
        return True

    # easy algorithm from
    # https://www.combinatorics.org/ojs/index.php/eljc/article/download/DS17/pdf/ page 9
    adj = {v: neighbors(graph, v) for v in graph}

    # for each triangle, "extend" it and check whether it contains a universal vertex
    for triangle in explicit_triangles(graph):
        a, b, c = triangle
        # extend the triangle
        extended_triangle = BitMap(triangle)
        # add vertices adjacent to at least two vertices of the triangle
        extended_triangle |= adj[a] & adj[b]
        extended_triangle |= adj[a] & adj[c]
        extended_triangle |= adj[b] & adj[c]

        # look for a universal vertex in the subgraph induced by the extended triangle; i.e., a
        # vertex whose neighborhood is the entire graph. This amounts to verifying whether the
        # largest degree in the subgraph is its order - 1
        has_universal = False

        for u in extended_triangle:
            missing = extended_triangle - adj[u]
            missing.discard(u)

            if not missing:
                has_universal = True
                break

        if not has_universal:
            return False

    # the wanted property holds for every triangle, return True
    return True


@assign_inherited_fisc()
@assign_class_id("gc_653")
@lru_cache(maxsize=None)
def is_cnplus4_bull_dart_gem_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_cnplus4_dart_gem_free(graph) and is_bull_free(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_754")
@lru_cache(maxsize=None)
def is_cnplus4_claw_gem_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_chordal(graph) and is_claw_free(graph) and is_gem_free(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_755")
@lru_cache(maxsize=None)
def is_cnplus4_p5_bull_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_chordal(graph) and is_p5_bull_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_776")
@lru_cache(maxsize=None)
def is_cnplus4_p5_claw_gem_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_cnplus4_claw_gem_free(graph) and is_p5_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_1350")
@lru_cache(maxsize=None)
def is_cnplus4_dart_gem_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    # note: dart-free is not a class in ISGCI
    return is_chordal_and_gem_free(graph) and is_h_free(graph, ["dart"])


@assign_inherited_fisc()
@assign_class_id("gc_451")
@lru_cache(maxsize=None)
def is_bipartite_and_fork_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_bipartite(graph) and is_fork_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_918")
@lru_cache(maxsize=None)
def is_c4_c5_k4_diamond_free_and_planar(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_planar(graph) and is_gc_917(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_2085")
@lru_cache(maxsize=None)
def is_co_bipartite_and_co_fork_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_co_bipartite(graph) and is_co_fork_free(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_2105")
@lru_cache(maxsize=None)
def is_co_cnplus4_bull_co_dart_co_gem_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return (
            is_co_gem_free(graph)
            and is_co_chordal(graph)
            and is_bull_free(graph)
            and is_h_free(graph, ["co-dart"])
    )


@assign_inherited_fisc()
@assign_class_id("AUTO_2767")
@lru_cache(maxsize=None)
def is_co_cnplus4_bull_house_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_co_chordal(graph) and is_gc_574(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_2133")
@lru_cache(maxsize=None)
def is_co_cnplus4_co_claw_co_gem_house_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return (
            is_co_gem_free(graph)
            and is_co_chordal(graph)
            and is_co_claw_free(graph)
            and is_house_free(graph)
    )


@assign_inherited_fisc()
@assign_class_id("AUTO_2594")
@lru_cache(maxsize=None)
def is_co_cnplus4_co_dart_co_gem_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_co_gem_free(graph) and is_co_chordal(graph) and is_h_free(graph, ["co-dart"])


@assign_inherited_fisc()
@assign_class_id("AUTO_2098")
@lru_cache(maxsize=None)
def is_co_xc_10_free(graph: nx.Graph) -> bool:
    """
    Characterisation found by my xc_unpacker program

    @param graph:
    @return:
    """
    return (
            is_k2_u_k3_free(graph)
            and is_h_free(graph, ["K_{3} U 2K_{1}"])
            and is_h_u_2k1_free(graph, is_p3_free)
            and is_h_u_k2_free(graph, is_p3_free)
    )


@assign_inherited_fisc()
@assign_class_id("gc_400")
@lru_cache(maxsize=None)
def is_k_23_p_hole_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_400.html

    @param graph:
    @return:
    """
    return is_hole_free(graph) and is_p_free(graph) and is_k23_free(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_1527")
@lru_cache(maxsize=None)
def is_k2_u_k3_co_p_antihole_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_1527.html

    @param graph:
    @return:
    """
    return is_anti_hole_free(graph) and is_co_p_free(graph) and is_k2_u_k3_free(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_2380")
@lru_cache(maxsize=None)
def is_co_xc_13_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    # note: characterization found by my xc_unpacker program
    return (
            is_k2_u_k3_free(graph)
            and is_odd_co_clique_free(graph, 5)
            and is_h_u_2k1_free(graph, is_triangle_free)
            and is_h_u_2k1_free(graph, is_p3_free)
            and is_h_u_k2_free(graph, is_p3_free)
            and is_h_free(
        graph,
        [
            "co(K_{5} - e)",
            "co(W_{4})",
        ],
    )
    )


@assign_inherited_fisc()
@assign_class_id("gc_1032")
@lru_cache(maxsize=None)
def is_co_fork_hole_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_hole_free(graph) and is_co_fork_free(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_1644")
@lru_cache(maxsize=None)
def is_anti_hole_fork_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_anti_hole_free(graph) and is_fork_free(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_743")
@lru_cache(maxsize=None)
def is_p5_anti_hole_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_anti_hole_free(graph) and is_p5_free(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_1538")
@lru_cache(maxsize=None)
def is_p5_co_p_anti_hole_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_anti_hole_free(graph) and is_p5_free(graph) and is_co_p_free(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_1534")
@lru_cache(maxsize=None)
def is_p5_anti_hole_co_gem_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_co_gem_free(graph) and is_anti_hole_free(graph) and is_p5_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_216")
@lru_cache(maxsize=None)
def is_hhg_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_anti_hole_free(graph) and is_gem_free(graph) and is_house_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_113")
@lru_cache(maxsize=None)
def is_hhp_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_hole_free(graph) and is_house_free(graph) and is_p_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_228")
@lru_cache(maxsize=None)
def is_hh_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_hole_free(graph) and is_house_free(graph)


@assign_class_id("gc_154")
@lru_cache(maxsize=None)
def is_cograph_contraction(graph: nx.Graph) -> bool:
    """
    A graph G is a cograph contraction iff it has a clique Q such that every induced P4 in G has a
    midpoint in Q and every induced P5 in the complement of G has both endpoints in Q.

    https://www.graphclasses.org/classes/gc_154.html

    :param graph:
    :return:
    """
    # algorithm from https://onlinelibrary.wiley.com/doi/abs/10.1002/(SICI)1097-0118(199904)30:4%3C309::AID-JGT5%3E3.0.CO;2-5 p 312
    implication_graph = DirectedGraph()
    # for all non-edges (a, b), build a clause (not a or not b) equivalent to (a => not b)
    implication_graph.add_edges_from((a, Not(b)) for a, b in nx.non_edges(graph))

    # for each P_4 (a, b, c, d), add clause (b or c)  equivalent to (not b => c)
    # in order to go through fewer subsets, don't examine every 4-subset of vertices; instead,
    # examine all pairs of edges
    for b, c in enumerate_all_p4_midpoints(graph):
        # degrees = induced_subgraph_degrees(graph, p4)
        # b, c = [v for v, deg in degrees.items() if deg == 2]
        implication_graph.add_edge(Not(b), c)

    # co-P5 condition

    # instead of examining all 5-tuples of vertices that might induce a house (= co(P_5)), we
    # examine all edges under the assumption that they might connect the only two degree-3 vertices
    # of the house we are trying to identify, then try to complete the rest of the pattern.
    # there is no need to use bipartiteness to distinguish between house and K_{2,3} (the only
    # other graph with the same degree sequence): this is implicitly done when we look for common
    # neighbors of b and d below (in a K_{2, 3}, that number would be 0).
    for b, d in graph.edges:
        found_house = False

        for top in common_neighbors(graph, b, d):
            left = neighbors(graph, b) - neighbors(graph, d) - neighbors(graph, top)
            right = neighbors(graph, d) - neighbors(graph, b) - neighbors(graph, top)

            left.discard(d)
            left.discard(top)
            right.discard(b)
            right.discard(top)

            for x in left:
                if neighbors(graph, x) & right:
                    implication_graph.add_edge(Not(b), b)
                    implication_graph.add_edge(Not(d), d)
                    found_house = True
                    break

            if found_house:
                break

    return satisfiable(implication_graph)


@assign_inherited_fisc()
@assign_class_id("gc_263")
@lru_cache(maxsize=None)
def is_quasi_median(graph: nx.Graph) -> bool:
    """
    A graph is quasi-median if every interval in G induces a median graph and for any three
    vertices u, v, w: I(u,v) ∩ I(u,w) = {u} implies that d(v, w) >= max(d(u, v), d(u, w)).

    https://www.graphclasses.org/classes/gc_263.html

    @param graph:
    @return:
    """
    return is_gc_628(graph) and is_weakly_modular(graph)


@assign_inherited_fisc()
@assign_class_id("gc_1168")
@lru_cache(maxsize=None)
def is_xc_10_free_and_weakly_modular(graph: nx.Graph) -> bool:
    """
    A graph is weakly median if it is weakly modular and does not contain two vertices with an
    unconnected triple of common neighbors.

    https://www.graphclasses.org/classes/gc_1168

    @param graph:
    @return:
    """
    return is_weakly_modular(graph) and is_xc_10_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_1146")
@lru_cache(maxsize=None)
def is_k_1_4_free_and_almost_claw_free_and_locally_connected(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_k14_free(graph) and is_locally_connected(graph) and is_almost_claw_free(graph)


# @lru_cache(maxsize=None)  # don't: graph keeps changing
def vertex_is_soft(graph: nx.Graph, v: Hashable) -> bool:
    """
    Returns True if either v is not the endpoint of any P_4 in graph, or it is not the midpoint of
    any P_4 in graph.

    :param graph:
    :param v:
    :return:
    """
    adj = {u: neighbors(graph, u) for u in graph}

    is_endpoint = False
    is_midpoint = False

    # v as midpoint: x - v - u - y
    for u in adj[v]:
        left = adj[v] - adj[u]
        right = adj[u] - adj[v]

        left.remove(u)
        right.remove(v)

        for x in left:
            if right & BitMap(non_neighbors(graph, x)):
                is_midpoint = True
                break

        if is_midpoint:
            break

    # v as endpoint: v - a - b - c
    for a in adj[v]:
        # b must be adjacent to a but not to v
        for b in adj[a] - adj[v]:
            if b == v:
                continue

            # c must be adjacent to b, not adjacent to a, and not adjacent to v
            candidates = adj[b] - adj[a] - adj[v]
            candidates.discard(a)

            if candidates:
                is_endpoint = True
                break

        if is_endpoint:
            break

    return not (is_endpoint and is_midpoint)


@assign_class_id("gc_10")
@lru_cache(maxsize=None)
def is_brittle(graph: nx.Graph) -> bool:
    """
    A graph G is brittle iff each induced subgraph H of G contains either a vertex that is not the
    endpoint of any P4 of H, or a vertex that is not the midpoint of any P4 of H.

    https://www.graphclasses.org/classes/gc_10

    :param graph:
    :return:
    """
    # naive algorithm from https://www.sciencedirect.com/science/article/pii/0166218X9190030Z
    return empty_graph_by_removing_vertices(graph, vertex_is_soft)


# @lru_cache(maxsize=None)  # don't: graph keeps changing
def vertex_neighborhood_induces_split_graph(graph: nx.Graph, v: Hashable) -> bool:
    """
    Returns True if the neighborhood of v induces a split graph, False otherwise.

    Complexity: O(deg(v))

    :param v:
    :type graph: networkx.Graph
    :param graph:
    :return:
    """
    if len(graph[v]) <= 3:
        return True

    return is_split_degree_sequence(
        sorted(induced_subgraph_degrees(graph, frozenset(graph[v])).values(), reverse=True)
    )


@assign_class_id("gc_608")
@lru_cache(maxsize=None)
def is_split_neighbourhood(graph: nx.Graph) -> bool:
    """
    A graph is split-neighborhood if every induced subgraph has a vertex whose neighborhood
    induces a split graph.

    https://www.graphclasses.org/classes/gc_608.html

    :type graph: nx.Graph
    :param graph:
    :return:
    """
    return empty_graph_by_removing_vertices(
        graph, vertex_neighborhood_induces_split_graph, local_neighborhood_cache=True
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
