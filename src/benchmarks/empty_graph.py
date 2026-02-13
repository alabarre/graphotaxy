"""
Anthony Labarre © 2024

Testing several ways of emptying graphs.
"""
from collections import defaultdict
from timeit import timeit
from typing import Callable

import networkx as nx

from graph_recognition.misc_algo import empty_graph_by_removing_vertices


def empty_graph_by_removing_vertices_2(graph: nx.Graph, criterion: Callable) -> bool:
    """Empties the graph by repeatedly removing vertices that satisfy the
    criterion. Returns True if all vertices are deleted, False otherwise.

    :param criterion:
    :type graph: networkx.Graph
    :param graph:
    :return:
    """
    new_graph = graph.copy()
    while new_graph:
        for v in new_graph:
            if criterion(new_graph, v):
                new_graph.remove_node(v)
                break

        else:  # no satisfying vertex was found, quit early
            return False

    # graph was successfully emptied
    return True


def always_true(*_) -> bool:
    return True


def main() -> None:
    """

    @return:
    """
    functions = [empty_graph_by_removing_vertices, empty_graph_by_removing_vertices_2]
    results = defaultdict(int)  # facultatif mais plus simple que dict
    num_instances = 1000000
    num_tries = 10000
    num_functions = len(functions)
    num_vertices = 50

    # generate random graphs on n vertices, and compare running times for emptying them
    for func in functions:
        print(f"Now testing {func.__name__} ...")
        for graph in [nx.fast_gnp_random_graph(num_vertices, .5)]:
            results[func.__name__] += timeit(
                setup="from __main__ import " + func.__name__ + ", always_true",
                stmt=func.__name__ + "(graph, always_true)",
                globals=locals(),
                number=num_tries
            )


    print("\nResults:\n")
    longest_name_len = max(len(nom) for nom in results)
    for name, time in sorted(results.items(), key=lambda pair: pair[1]):
        print(name.rjust(longest_name_len), ":", time)

    # Results: for large graphs (n >= 5000), empty_graph_by_removing_vertices is faster
    # For "small" graphs it's about the same


if __name__ == "__main__":
    main()
