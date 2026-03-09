"""
Anthony Labarre © 2025-2026

Utilities to "expand" a given graph so that all its minors that ISGCI knows about can be obtained.
The goal is to provide the set of all subgraphs covered by each configuration forbidden minor to
obtain explicit FISCs and thereby write recognizers for the corresponding graph classes.

"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------

# ----- Third-party imports -----------------------------------------------------------------------
from networkx import (
    Graph,
    add_path,
    complete_graph,
    complete_multipartite_graph,
)
from networkx.algorithms.isomorphism import GraphMatcher

from graph_recognition.smallgraphs import all_smallgraphs_by_order
from tools.xc_unpacker import identify_smallgraph

GRAPHS_TO_NAMES = all_smallgraphs_by_order()

# @lru_cache(maxsize=None) would be fine, except we also want to cache results for graphs that are
# isomorphic to the given one; since there seems to be no easy way to do that with lru_cache, let's
# simply implement our own cache
MY_CACHE = dict()


def all_non_isomorphic_1_subdivisions(graph: Graph) -> dict[Graph, Graph]:
    """
    Returns all nonisomorphic subgraphs that can be obtained by subdividing one edge of the given
    graph.

    @param graph:
    @return:
    """
    # if we don't know the result, compute it ...
    if graph not in MY_CACHE:
        # ... unless we know it for a graph isomorphic to the input
        for other in MY_CACHE:
            if GraphMatcher(graph, other).is_isomorphic():
                MY_CACHE[graph] = MY_CACHE[other]
                break

        else:
            # otherwise, compute result from scratch, store it, then return it
            result = set()
            new_node = graph.number_of_nodes() + 1
            for u, v in graph.edges():
                # split edge (u, v): replace it with a path (u, max(V) + 1, v), and remove the edge
                new_graph = graph.copy()
                add_path(new_graph, [u, new_node, v])
                new_graph.remove_edge(u, v)

                # record new graph only if it is not  isomorphic to any of the subdivisions we've
                # already computed
                if all(not GraphMatcher(new_graph, other).is_isomorphic() for other in result):
                    result.add(new_graph)

            MY_CACHE[graph] = result

    return MY_CACHE[graph]


def known_subdivisions(graph: Graph) -> set[Graph]:
    """
    Returns all subdivisions of a graph that correspond to smallgraphs known to ISGCI, including
    the given graph.

    @param graph:
    @param subdivisions:
    @return:
    """
    result = set()

    def known_subdivisions_rec(other_graph: Graph) -> None:
        """
        Identifies the graph, adds it to the known subdivisions if need be, then splits each edge
        in turn and recurses until we have "too many nodes" (currently 13).

        @param graph:
        @return:
        """
        # if graph is "known", record its name
        graph_name = identify_smallgraph(other_graph)
        if graph_name:
            # print("[DEBUG] found:", graph_name)
            result.add(graph_name)

        # only proceed to subdividing the graph further if it contains fewer vertices than the
        # largest smallgraph in ISGCI
        if other_graph.number_of_nodes() < 13:
            # naive version
            """
            for u, v in set(graph.edges()):
                # split edge (u, v): replace it with a path (u, max(V) + 1, v), and remove the edge
                new_node = graph.number_of_nodes() + 1
                add_path(graph, [u, new_node, v])
                graph.remove_edge(u, v)

                # then subdivide further
                known_subdivisions_rec(graph)

                # undo edge splitting: delete added vertex and add edge (u, v) back
                graph.remove_node(new_node)
                graph.add_edge(u, v)
                bar.update()
            """

            # compute all non-isomorphic subdivisions of one edge first, and recurse only on those
            for subdivision in all_non_isomorphic_1_subdivisions(graph):
                known_subdivisions_rec(subdivision)

    known_subdivisions_rec(graph)
    return result


def main() -> None:
    """
    The only graphs that are involved in minor-free characterizations in ISGCI are:

    [v] K_{2, 3}:   ['K_{2,3}', 'co(X_{90})', 'twin-C_{5}']
    [v] K_{3, 3}:   ['K_{3,3}', 'co(X_{86})']
    [v] K_{3}:      ['C_{4}', 'C_{6}', 'C_{7}', 'C_{8}', 'co(C_{5})', 'triangle']
    [v] K_{4}:      ['BW_{3}', 'K_{3,3}-e', 'K_{4}', 'X_{203}', 'X_{39}', 'co(P_{2} U P_{3})', 'co(X_{37})', 'co(X_{88})', 'co(X_{89})', 'co-twin-C_{5}']
    [v] K_{5}:      ['K_{5}', 'X_{46}', 'co(K_{2} U claw)', 'co(X_{120})']
    [v] X_{126}:    ['X_{126}']
    [v] X_{174}:    ['X_{174}']
    [v] 3K_{2}:     ['3K_{2}', '3P_{3}']

    See:

    [v] https://www.graphclasses.org/classes/gc_903.html (= outerplanar)
    [v] https://www.graphclasses.org/classes/gc_898.html (= planar)
    [ ] https://www.graphclasses.org/classes/gc_896.html (= tree)
    [ ] https://www.graphclasses.org/classes/gc_309.html (= series-parallel, treewidth 2, partial 2-tree)
        no recognizer available
    [ ] https://www.graphclasses.org/classes/gc_897.html (= partial 3-tree, treewidth 3)
        no recognizer available

    @return:
    """
    from time import perf_counter

    # """
    print("All subdivisions of 3K_2")
    three_edges = Graph()
    three_edges.add_edges_from([(0, 1), (2, 3), (4, 5)])
    print(sorted(known_subdivisions(three_edges)))
    # """
    # """
    print("All subdivisions of X_{174}")
    x174 = Graph()
    x174.add_edges_from(
        [
            (0, 1),
            (0, 4),
            (0, 5),
            (1, 2),
            (1, 6),
            (2, 3),
            (2, 7),
            (3, 4),
            (3, 8),
            (4, 9),
            (5, 6),
            (5, 9),
            (6, 7),
            (7, 8),
            (8, 9),
        ]
    )
    print(sorted(known_subdivisions(x174)))
    # """
    # """
    print("All subdivisions of X_{126}")
    x126 = Graph()
    x126.add_edges_from(
        [
            (0, 2),
            (0, 3),
            (0, 6),
            (1, 4),
            (1, 6),
            (1, 7),
            (2, 4),
            (2, 7),
            (3, 5),
            (3, 7),
            (4, 5),
            (5, 6),

        ]
    )
    print(sorted(known_subdivisions(x126)))
    # """

    # """  # gave up after 20 minutes, find a way to improve speed TODO
    for num in range(3, 6):
        print(f"All subdivisions of K_{num}")
        kn = complete_graph(num)
        #
        start = perf_counter()
        print(sorted(known_subdivisions(kn)))
        print("Done in", perf_counter() - start, "seconds")
    # """

    for m, n in [(2, 3), (3, 3)]:
        print(f"All subdivisions of K_({m}, {n})")
        k33 = complete_multipartite_graph(m, n)
        #
        start = perf_counter()
        print(sorted(known_subdivisions(k33)))
        print("Done in", perf_counter() - start, "seconds")


if __name__ == "__main__":
    main()
