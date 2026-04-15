"""
Anthony Labarre © 2023-2026

This module contains various functions for reading and writing graphs from / to files.

"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
import bz2
import gzip
import lzma
import os
import re
import textwrap
from typing import Iterator, Any, Callable

# ----- Third-party imports -----------------------------------------------------------------------
import networkx as nx

# ----- My imports --------------------------------------------------------------------------------
from graph_recognition.adjacency_matrix import HalfAdjacencyMatrix
from undirected_graph import UndirectedGraph

# Global variables --------------------------------------------------------------------------------
NAUTY_READERS = {"g6": nx.from_graph6_bytes, "s6": nx.from_sparse6_bytes}
SUPPORTED_COMPRESSED_FORMATS = {"bz2": bz2.open, "gz": gzip.open, "xz": lzma.open}


# Functions ---------------------------------------------------------------------------------------
def edge_list_file_to_edge_set(filename: str) -> Iterator:
    """
    Returns a set of edge sets from a given file. Loops and weights are discarded.

    :param filename: the path to the file to read
    :return: set of edge sets
    """
    # I tried pandas, but it was twice as slow, so I'm sticking with this version for now
    with open(filename) as data:
        for line in data:
            if line[0] != "%":  # skip comments
                u, v = map(int, line.split()[:2])  # skip weight if present
                if u != v:  # skip loops
                    yield u, v


def process_graphs(filename: str, output_type: Callable = UndirectedGraph) -> Iterator:
    """
    Yields all graphs from a file. Supported file formats are graph6 (.g6), sparse6 (.s6), and
    graphviz (.dot), with the caveat that only the first graph from a .dot file can be loaded even
    if it contains more of them.

    Additionally, compressed g6 and s6 files are also supported if compressed using bzip2, gzip, or
    xz. The naming scheme must reflect this (e.g., foo.g6.bz2 or bar.s6.gz).

    :param output_type:
    :param filename: the path to the file to open
    :return: undirected graphs from that file
    """
    # retrieve extension in lower case without the .
    extension = os.path.splitext(filename)[-1][1:].lower()
    if extension in NAUTY_READERS:
        # read graphs as the readers would, but yield them instead of storing them; binary mode is
        # required by g6 / s6
        with open(filename, "rb") as file:
            for line in file:
                yield output_type(NAUTY_READERS[extension](line.strip()))

    elif extension in SUPPORTED_COMPRESSED_FORMATS:
        # compute "original" extension (i.e., the EXT in foo.EXT.GZ)
        original_extension = os.path.splitext(os.path.splitext(filename)[0])[-1][1:].lower()
        if original_extension in NAUTY_READERS:
            decompressor = SUPPORTED_COMPRESSED_FORMATS[extension]
            with decompressor(filename, 'rb') as archive:
                for line in archive:
                    yield output_type(NAUTY_READERS[original_extension](line.strip()))

        else:
            raise ValueError(
                f"Unknown original file extension for '{filename}' ({extension} is fine, but I "
                f"can't handle {original_extension})"
            )

    elif extension == "dot":
        # if dot file contains several graphs, warn user that all graphs except the first one will
        # be discarded
        count = number_of_graphs_in_file(filename)
        if count > 1:
            print(
                textwrap.fill(
                    f"WARNING: {os.path.basename(filename)} is a dot file with {count} graphs; "
                    "however, nx.nx_pydot.read_dot will only read the first graph in that file, "
                    "silently ignoring any subsequent graph.",
                    width=100,
                    subsequent_indent=" " * 9,
                )
            )
        yield output_type(nx.nx_pydot.read_dot(filename))

    elif extension in {"edges", "mtx"}:
        yield output_type(edge_list_file_to_edge_set(filename))

    else:
        raise ValueError(f"Unknown file extension for '{filename}'")


def null_output(*args: Any, **kwargs: Any) -> None:  # noqa
    """
    Accepts anything, returns nothing.

    :param args:
    :param kwargs:
    :return:
    """
    return


def number_of_graphs_in_file(filename: str) -> int:
    """
    Returns the actual number of graphs in the given file.

    :param filename: the path to the file to open
    :return: the number of graphs in that file
    """
    # retrieve extension in lower case without the .
    extension = os.path.splitext(filename)[-1][1:].lower()
    if extension == "dot":
        # regex for matching "graph { ...", excluding subgraphs
        pattern = re.compile(r"^\s*(?:graph)\b[^{]*\{", re.MULTILINE)
        with open(filename) as file:
            return len(pattern.findall(file.read()))

    # otherwise result depends on the format, so process graphs and count them
    return sum(1 for _ in process_graphs(filename, output_type=null_output))
