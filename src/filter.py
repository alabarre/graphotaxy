"""
Anthony Labarre © 2025-2026

Filters all graphs in a file that belong to a specific graph class.
"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
import argparse
import functools
import os
import sys
from collections import namedtuple
from os.path import basename
from typing import Iterator, Iterable, Callable

# ----- My imports --------------------------------------------------------------------------------
from undirected_graph import UndirectedGraph
from graph_recognition.smallgraphs import all_smallgraphs_by_order
from tools.compute_fisc_basis import basis


def disable_lru_cache(maxsize: int = None, typed: bool = False) -> Callable:
    """
    Decorator for disabling lru_cache wherever it is used.

    This may have come from some StackOverflow post, but I can't find it anymore.
    """
    _CacheInfo = namedtuple("CacheInfo", ["hits", "misses", "maxsize", "currsize"])

    def decorator(_func: Callable) -> Callable:
        @functools.wraps(_func)
        def wrapper(*args, **kwargs) -> Callable:
            return _func(*args, **kwargs)

        # decorate function with same attributes as lru_cache would to guarantee compatibility
        wrapper.cache_clear = lambda: None
        wrapper.cache_info = lambda: _CacheInfo(0, 0, maxsize, 0)
        wrapper.cache_parameters = lambda: {"maxsize": maxsize, "typed": typed}
        return wrapper

    if callable(maxsize) and not isinstance(maxsize, int):
        func = maxsize
        maxsize = None
        return decorator(func)

    return decorator


# disable all lru_cache decorations: we may receive large files to filter, and the high memory
# usage isn't worth it
setattr(functools, "lru_cache", disable_lru_cache)

# ----- Third-party imports -----------------------------------------------------------------------
import networkx as nx
from tqdm import tqdm

# ----- My imports --------------------------------------------------------------------------------
from graph_analyzer import GraphAnalyzer
from readwrite import process_graphs, number_of_graphs_in_file


def get_recognizer(class_id: str) -> Callable | None:
    """
    Returns the recognizer for the class identified by class_id.

    :param class_id:
    :return:
    """
    try:
        # accessing the __wrapped__ function ensures we access the non-lru_cached version of the
        # recognizer
        return GraphAnalyzer().get_recognizer(class_id).__wrapped__

    except ValueError:
        print(f"no recognizer available for class {class_id}")


def filter_graphs(filename: str, class_id: str, invert: bool = False) -> Iterator:
    """
    Returns the list of all graphs in filename that belong to the class identified by class_id.

    :param filename:
    :param class_id:
    :param invert:
    :return:
    """
    recognizer = get_recognizer(class_id)
    if recognizer:
        if invert:
            for graph in tqdm(
                    process_graphs(filename),
                    total=number_of_graphs_in_file(filename),
                    unit=" graphs",
            ):
                if recognizer(graph):
                    yield graph
            else:
                for graph in tqdm(
                        process_graphs(filename),
                        total=number_of_graphs_in_file(filename),
                        unit=" graphs",
                ):
                    if not recognizer(graph):
                        yield graph


def write_graphs_to_file(graph_iterable: Iterable[nx.Graph], filename: str) -> int:
    """
    Writes all graphs in an iterable to a file, and returns the number of graphs that were written.

    :param graph_iterable:
    :param filename:
    :return:
    """
    # extract extension and use it to select the right writer
    extension = os.path.splitext(filename)[-1]
    if extension == ".g6":
        writer = nx.to_graph6_bytes

    elif extension == ".s6":
        writer = nx.to_sparse6_bytes

    else:
        raise ValueError(f"Unknown file extension {extension}")

    # write each graph to the output file
    with open(filename, "w") as file:
        for i, graph in enumerate(graph_iterable, 1):
            file.write(writer(graph, header=False).decode())
        return i


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Filters all graphs that belong to a specific graph class"
    )
    parser.add_argument("-i", "--input", help="the graph file to analyze")
    parser.add_argument(
        "-s", "--smallgraphs", action="store_true",
        help="filter smallgraphs rather than graphs from a file"
    )
    parser.add_argument(
        "-m", "--membership",
        help="class for which the membership should be tested; use ISGCI ids",
    )
    parser.add_argument(
        "-v", "--invert-matches", action="store_true",
        help="output graphs that are NOT members of the given class"
    )
    if len(sys.argv) == 1:
        parser.print_help()
        parser.exit()

    args = parser.parse_args()

    # sanity checks
    if not args.membership:
        print("Error: specify a class")
        sys.exit(-1)

    print(args.invert_matches)
    # filter graphs
    if args.smallgraphs:
        recognizer = get_recognizer(args.membership)
        all_smallgraphs = all_smallgraphs_by_order()
        matches = set()
        if args.invert_matches:
            for graph_set in all_smallgraphs.values():
                for name, g6 in graph_set:
                    graph = UndirectedGraph(nx.from_graph6_bytes(g6.encode()))
                    if not recognizer(graph):
                        print(name)
                        matches.add(name)
        else:
            for graph_set in all_smallgraphs.values():
                for name, g6 in graph_set:
                    graph = UndirectedGraph(nx.from_graph6_bytes(g6.encode()))
                    if recognizer(graph):
                        print(name)
                        matches.add(name)

        print("Basis:")
        print(basis(matches))

    else:
        # check input file
        if not os.path.exists(args.input):
            print("Error:", args.input, "does not exist")
            sys.exit(-1)

        print(f"Processing graphs in {args.input}")
        matches = filter_graphs(args.input, args.membership, invert=args.invert_matches)

        # output result if any
        if matches:
            output_filename = ("_and_" + args.membership).join(
                os.path.splitext(basename(args.input))
            )
            count = write_graphs_to_file(matches, output_filename)
            print(f"Wrote {count} filtered graphs to {output_filename}")

        else:
            print(
                f"None of the input graphs belong to class {args.membership}, so no output file written"
            )


if __name__ == "__main__":
    main()
