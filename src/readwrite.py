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

# ----- My imports --------------------------------------------------------------------------------
from undirected_graph import UndirectedGraph


# Functions ---------------------------------------------------------------------------------------
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
    readers = {"g6": nx.from_graph6_bytes, "s6": nx.from_sparse6_bytes}
    supported_compressed_formats = {"bz2": bz2.open, "gz": gzip.open, "xz": lzma.open}
    # retrieve extension in lower case without the .
    extension = os.path.splitext(filename)[-1][1:].lower()
    if extension in readers:
        # read graphs as the readers would, but yield them instead of storing them; binary mode is
        # required by g6 / s6
        with open(filename, "rb") as file:
            for line in file:
                yield UndirectedGraph(readers[extension](line.strip()))

    elif extension in supported_compressed_formats:
        # compute "original" extension (i.e., the EXT in foo.EXT.GZ)
        original_extension = os.path.splitext(os.path.splitext(filename)[0])[-1][1:].lower()
        if original_extension in readers:
            decompressor = supported_compressed_formats[extension]
            with decompressor(filename, 'rb') as archive:
                for line in archive:
                    yield UndirectedGraph(readers[original_extension](line.strip()))
        else:
            raise ValueError(
                f"Unknown original file extension for '{filename}' ({extension} is fine, but I "
                f"can't handle {original_extension})"
            )

    elif extension == ".dot":
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
