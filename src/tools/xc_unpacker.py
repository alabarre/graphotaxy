"""
Anthony Labarre © 2023-2026

Lists the graphs that are covered by each XC or XZ configuration. Those configurations are defined
here: https://www.graphclasses.org/smallgraphs.html#forbidden_configurations_XC and there:
https://www.graphclasses.org/smallgraphs.html#forbidden_configurations_XZ, and summarize many
smallgraphs as follows:

- each configuration XC represents a family of graphs by specifying edges that must be present
    (solid lines), edges that must not be present (dotted lines), and edges that may or may not be
    present (not drawn).
- each configuration XZ represents a family of graphs by specifying edges that must be present
    (solid lines), edges that must not be present (not drawn), and edges that may or may not be
    present (red dotted lines).

The goal of this unpacking program is to provide the set of all subgraphs covered by each
configuration so as to obtain explicit FISCs and thereby write recognizers for the corresponding
graph classes.

"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
from copy import deepcopy
from functools import lru_cache
from itertools import chain, combinations
from typing import Iterable, Generator, List

# ----- Third-party imports -----------------------------------------------------------------------
import networkx as nx

# ----- My imports --------------------------------------------------------------------------------
from graph_recognition.smallgraphs import all_smallgraphs_by_order

# Global variables --------------------------------------------------------------------------------
ALL_SMALLGRAPHS = all_smallgraphs_by_order()


# Functions ---------------------------------------------------------------------------------------
def powerset(iterable: Iterable) -> Generator:
    """
    Generates all subsets of elements of a given iterable.

    Example: powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)

    Source: https://docs.python.org/3/library/itertools.html#recipes

    :param iterable:
    :return:
    """
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


def unpack_xc(present: Iterable, forbidden: Iterable) -> List[nx.Graph]:
    """
    Returns all graphs that can be obtained from an XC configuration. Those graphs must contain all
    present edges, and may additionally contain any missing edge **not** in the forbidden set.

    :param present:
    :param forbidden:
    :return:
    """
    base_graph = nx.Graph(present)
    results = []

    # try all subsets of nonedges \ forbidden (including the empty set)
    for new_edges in powerset(set(nx.non_edges(base_graph)).difference(forbidden)):
        new_graph = deepcopy(base_graph)
        new_graph.add_edges_from(new_edges)
        results.append(new_graph)

    return results


def unpack_xz(present: Iterable, allowed: Iterable) -> List[nx.Graph]:
    """
    Returns all graphs that can be obtained from an XZ configuration. Those graphs must contain all
    present edges, and may additionally contain any edge in the allowed set.

    :param allowed:
    :param present:
    :return:
    """
    base_graph = nx.Graph(present)
    results = []

    # try all subsets of nonedges \ forbidden (including the empty set)
    for new_edges in powerset(allowed):
        new_graph = deepcopy(base_graph)
        new_graph.add_edges_from(new_edges)
        results.append(new_graph)

    return results


@lru_cache(maxsize=None)
def identify_smallgraph(graph: nx.Graph) -> str | None:
    """
    Returns the name of the smallgraph that corresponds to the given graph, or None if no match
    exists.

    """
    n = graph.number_of_nodes()
    if n in ALL_SMALLGRAPHS:
        # return the name of the only smallgraph isomorphic to graph
        for data in ALL_SMALLGRAPHS[n]:
            if nx.is_isomorphic(graph, nx.from_graph6_bytes(data[1].encode())):
                return data[0]


def main() -> None:
    """

    @return:
    """
    # I number vertices from left to right and top to bottom
    xc_configurations = {
        "XC_1": (
            [(0, 1), (0, 3), (1, 2), (1, 3), (1, 4), (2, 4), (3, 4)],
            [(0, 4), (2, 3)],
        ),
        "XC_2": (
            [(0, 1), (0, 3), (0, 4), (1, 2), (1, 4), (1, 5), (2, 5), (3, 4), (4, 5)],
            [(0, 2), (3, 5)],
        ),
        "XC_3": (
            [(0, 3), (1, 3), (1, 4), (1, 5), (2, 5), (3, 4), (4, 5)],
            [(0, 1), (0, 2), (1, 2), (3, 5)],
        ),
        "XC_4": (
            [(0, 1), (0, 2), (1, 2), (1, 3), (1, 5), (2, 4), (2, 6), (3, 5), (4, 6)],
            [(0, 3), (0, 4), (1, 6), (2, 5)],
        ),
        "XC_5": (
            [(0, 1), (2, 4), (3, 5)],
            [(0, 2), (0, 5), (1, 3), (1, 4), (2, 3), (4, 5)],
        ),
        "XC_6": (
            [(0, 3), (1, 4), (2, 5)],
            [(0, 1), (0, 2), (1, 2), (3, 4), (3, 5), (4, 5)],
        ),
        "XC_7": (
            [(0, 1), (0, 2), (1, 3), (2, 4), (3, 4)],
            [(0, 3), (0, 4), (1, 2), (1, 4), (2, 3)],
        ),
        "XC_8": (
            [(0, 1), (1, 2), (1, 3), (1, 4), (1, 5), (2, 4), (3, 5), (4, 6), (5, 6)],
            [(0, 4), (0, 5), (1, 6), (2, 3), (2, 6), (3, 6), (4, 5)],
        ),
        "XC_9": ([(0, 1), (1, 4), (2, 3)], [(0, 3), (1, 2), (3, 4)]),
        "XC_10": ([(0, 1), (0, 3), (1, 2), (1, 4), (2, 3), (3, 4)], [(0, 2), (2, 4)]),
        "XC_11": ([(0, 3), (1, 3), (2, 3), (3, 4), (3, 5)], []),
        "XC_12": ([(0, 2), (1, 2), (2, 3), (2, 4)], []),
        "XC_13": ([(0, 1), (0, 3), (1, 2), (1, 4), (2, 3), (3, 4)], []),
    }

    # findings: XC_1, XC_5, XC_6, XC_7, XC_9, XC_10, XC_12, XC_13 generate only known smallgraphs
    print("Here are all unpacked XC configurations:\n")

    for name, xc_config in xc_configurations.items():
        unpacked_names = {identify_smallgraph(graph) for graph in unpack_xc(*xc_config)}
        print(
            ["[ v ]", "[ x ]"][None in unpacked_names],
            name,
            "yields the following smallgraphs:",
            unpacked_names,
        )

    print("\nHere are all unpacked XZ configurations:\n")
    # I number vertices from left to right and top to bottom
    xz_configurations = {
        "XZ_1": (
            [(0, 1), (0, 2), (1, 2), (1, 3), (2, 4), (3, 5), (3, 6), (4, 6), (5, 6)],
            [(3, 4), (4, 5)],
        ),
        # note: XZ_2 and XZ_3 are not yet useful
        "XZ_4": (
            [(0, 1), (0, 2), (1, 2), (1, 3), (2, 4), (3, 6), (3, 7), (4, 5), (4, 8),
             (5, 7), (6, 8), (7, 8)],
            [(3, 4), (3, 5), (4, 6), (5, 6)],
        ),
        "XZ_5": (
            [(0, 1), (0, 2), (0, 5), (1, 2), (1, 5), (2, 5), (3, 6), (4, 6), (5, 6)],
            [(0, 3), (0, 4), (1, 3), (1, 4), (2, 3), (2, 4)],
        ),
        "XZ_6": ([(0, 1), (1, 2), (1, 4), (1, 5), (2, 3)], [(0, 4), (0, 5), (4, 5)]),
        "XZ_7": (
            [(0, 1), (0, 5), (1, 2), (1, 4), (2, 3), (2, 5)],
            [(0, 4), (1, 5), (4, 5)],
        ),
        "XZ_8": ([(0, 1), (1, 2), (1, 4), (2, 3), (3, 5)], [(0, 4), (0, 5), (4, 5)]),
        "XZ_9": ([(0, 1), (1, 2), (1, 4), (2, 3), (2, 5)], [(0, 4), (3, 5), (4, 5)]),
        "XZ_10": (
            [(0, 1), (0, 4), (1, 2), (2, 3), (2, 4), (3, 5)],
            [(0, 5), (1, 4), (4, 5)],
        ),
        "XZ_11": (
            [(0, 1), (1, 2), (1, 4), (2, 3), (3, 4), (3, 5)],
            [(0, 5), (2, 4), (4, 5)],
        ),
        "XZ_12": ([(0, 1), (1, 2), (2, 3), (2, 4), (3, 5)], [(0, 5), (3, 4), (4, 5)]),
        "XZ_13": ([(0, 1), (0, 4), (1, 2), (2, 3), (3, 5)], [(0, 5), (3, 4), (4, 5)]),
        "XZ_14": (
            [(0, 1), (0, 4), (0, 5), (1, 2), (2, 3), (3, 5)],
            [(1, 5), (3, 4), (4, 5)],
        ),
        # output for XZ_15 is {'co(3K_{2})', 'co(P_{2} U P_{4})', 'co(E)', 'S_{3}'}, which confirms
        # the known equivalence with https://www.graphclasses.org/classes/gc_748.html
        "XZ_15": (
            [(0, 1), (0, 2), (1, 2), (1, 3), (1, 4), (2, 4), (2, 5), (3, 4), (4, 5)],
            [(0, 3), (0, 5), (3, 5)],
        ),
    }

    for name, xz_config in xz_configurations.items():
        unpacked_names = {identify_smallgraph(graph) for graph in unpack_xz(*xz_config)}
        print(
            ["[ v ]", "[ x ]"][None in unpacked_names],
            name.rjust(5),
            "yields the following smallgraphs:",
            unpacked_names,
        )


if __name__ == "__main__":
    main()
