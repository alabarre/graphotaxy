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
from typing import Iterator

# ----- Third-party imports -----------------------------------------------------------------------
import networkx as nx
import pandas as pd

# ----- My imports --------------------------------------------------------------------------------
from undirected_graph import UndirectedGraph


# Functions ---------------------------------------------------------------------------------------
def edge_list_file_to_edge_set(filename: str) -> Iterator:
    """
    Returns a set of edge sets from a given file. Loops and weights are discarded.

    >>> from time import perf_counter; import networkx as nx; start = perf_counter()
    >>> x = set(edge_list_file_to_edge_set("/home/anthony/Downloads/bio-mouse-gene/bio-mouse-gene.edges"))
    >>> end = perf_counter()
    >>> print(end - start)

    # current version takes about 12 seconds on my machine

    :param filename: the path to the file to read
    :return: set of edge sets
    """
    # I tried pandas but it was twice as slow, so I'm sticking with this version for now
    with open(filename) as data:
        for line in data:
            if line[0] != "%": # skip comments
                u, v = map(int, line.split()[:2]) # skip weight if present
                if u != v: # skip loops
                    yield u, v


def process_graphs(filename: str) -> Iterator:
    """
    Yields all graphs from a file. Supported file formats are graph6 (.g6), sparse6 (.s6), and
    graphviz (.dot), with the caveat that only the first graph from a .dot file can be loaded even
    if it contains more of them.

    Additionally, compressed g6 and s6 files are also supported if compressed using bzip2, gzip, or
    xz. The naming scheme must reflect this (e.g., foo.g6.bz2 or bar.s6.gz).

    :param filename: the path to the file to open
    :return: undirected graphs from that file
    """
    nauty_readers = {"g6": nx.from_graph6_bytes, "s6": nx.from_sparse6_bytes}
    supported_compressed_formats = {"bz2": bz2.open, "gz": gzip.open, "xz": lzma.open}
    # retrieve extension in lower case without the .
    extension = os.path.splitext(filename)[-1][1:].lower()
    if extension in nauty_readers:
        # read graphs as the readers would, but yield them instead of storing them; binary mode is
        # required by g6 / s6
        with open(filename, "rb") as file:
            for line in file:
                yield UndirectedGraph(nauty_readers[extension](line.strip()))

    elif extension in supported_compressed_formats:
        # compute "original" extension (i.e., the EXT in foo.EXT.GZ)
        original_extension = os.path.splitext(os.path.splitext(filename)[0])[-1][1:].lower()
        if original_extension in nauty_readers:
            decompressor = supported_compressed_formats[extension]
            with decompressor(filename, 'rb') as archive:
                for line in archive:
                    yield UndirectedGraph(nauty_readers[original_extension](line.strip()))

        # TODO support for compressed .edges

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
        yield UndirectedGraph(nx.nx_pydot.read_dot(filename))

    elif extension == "edges":
        yield UndirectedGraph(edge_list_file_to_edge_set(filename))

    else:
        raise ValueError(f"Unknown file extension for '{filename}'")


def number_of_graphs_in_file(filename: str) -> int:
    """
    Returns the actual number of graphs in the given file.

    :param filename: the path to the file to open
    :return: the number of graphs in that file
    """
    extension = os.path.splitext(filename)[-1]
    if extension in {".g6", ".s6"}:
        # every line except the optional header is a graph in a g6 or s6 file
        count = 0
        with open(filename) as file:
            for line in file:
                count += not line.startswith(">>>")
            return count

    elif extension == ".dot":
        # regex for matching "graph { ...", excluding subgraphs
        pattern = re.compile(r"^\s*(?:graph)\b[^{]*\{", re.MULTILINE)
        with open(filename) as file:
            return len(pattern.findall(file.read()))

    # otherwise result depends on the format, so process graphs and count them
    return sum(1 for _ in process_graphs(filename))
