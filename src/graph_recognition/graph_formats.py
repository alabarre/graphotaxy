"""
Anthony Labarre © 2023-2026

This file contains everything related to reading, writing, and converting between various graph
formats. I don't aim to be exhaustive, just writing what I happen to need as I go.

"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
import argparse
from itertools import chain

# ----- Third-party imports -----------------------------------------------------------------------
import networkx as nx

# Functions ---------------------------------------------------------------------------------------
# ----- conversion to LAD -------------------------------------------------------------------------
"""
The LAD format is used by the Glasgow Subgraph Solver and is structured as follows:

        order

        degree_1 neighbour_1 neighbour_2 ...
        degree_2 neighbour_1 neighbour_2 ...
        ...

Source: https://perso.liris.cnrs.fr/christine.solnon/SIP.html
"""


def g6file_to_lad(g6file: str) -> str:
    """
    Returns the LAD encoding of a graph encoded as a graph6 file.

    :param g6file:
    :return:
    """
    return nx_graph_to_lad_string(nx.read_graph6(g6file))


def g6string_to_lad(g6string: str) -> str:
    """
    Returns the LAD encoding of a graph encoded as a graph6 string.

    :param g6string:
    :return:
    """
    return nx_graph_to_lad_string(nx.from_graph6_bytes(g6string.encode()))


def nx_graph_to_lad_string(graph: nx.Graph) -> str:
    """
    Returns the LAD encoding of a networkx.Graph.

    >>> import networkx; g = nx.complete_graph(3); print(nx_graph_to_lad_string(g))
    3
    2 1 2
    2 0 2
    2 0 1

    :param graph:
    :return:
    """
    # nodes must sometimes be relabeled, because the glasgow subgraph solver expects nodes in the
    # range [0, n-1] when n vertices are announced. This causes it to crash on subgraphs with the
    # following error:
    #
    #   "Error: Error reading graph file ... : edge index out of bounds"
    n = graph.number_of_nodes()
    mapping = dict(zip(graph.nodes, range(n)))
    result = str(n)
    for node in graph:
        result = "\n".join(
            [
                result,
                " ".join(
                    map(
                        str,
                        chain([graph.degree[node]], (mapping[v] for v in graph[node])),
                    )
                ),
            ]
        )

    return result


def nx_graph_to_lad_file(graph: nx.Graph, filename: str) -> None:
    """
    Writes the LAD encoding of a networkx.Graph to a file.

    :param graph:
    :param filename:
    :return:
    """
    with open(filename, "w") as output:
        # nodes must sometimes be relabeled, because the glasgow subgraph solver
        # expects nodes in the range [0, n-1] when n vertices are announced. This
        # causes it to crash on subgraphs with the following error:
        #
        #   "Error: Error reading graph file ... : edge index out of bounds"
        n = graph.number_of_nodes()
        mapping = dict(zip(graph.nodes, range(n)))
        output.write(str(n) + "\n")
        for node in graph:
            output.write(
                " ".join(
                    map(
                        str,
                        chain([graph.degree[node]], (mapping[v] for v in graph[node])),
                    )
                )
                + "\n"
            )


def nx_graph_to_gr_file(graph: nx.Graph, filename: str) -> None:
    """
    Writes the GR encoding of a networkx.Graph to a file. The GR format is as follows:

        mandatory first line: p tw [number of vertices] [number of edges]

    No other line may start with p. Every other line describes a single edge u -- v as:

        u v

    Comments can be inserted in the form of a line starting with c:

        c this is a comment

    Source: https://pacechallenge.wordpress.com/pace-2016/track-a-treewidth/

    :param graph:
    :param filename:
    :return:
    """
    with open(filename, "w") as output:
        # mandatory first line
        output.write(
            "p tw " + str(graph.number_of_nodes()) + " " + str(graph.size()) + "\n"
        )
        # every subsequent line is an edge u v, where indices must be in the range
        # [1, n]
        for u, v in graph.edges:
            output.write(str(u + 1) + " " + str(v + 1) + "\n")


def lad_file_to_nx_graph(filename: str) -> nx.Graph:
    """
    Returns a nx.Graph constructed from a LAD file.

    >>> sorted(lad_file_to_nx_graph("smallgraphs/triangle").edges())
    [(0, 1), (0, 2), (1, 2)]
    >>> sorted(lad_file_to_nx_graph("smallgraphs/4K_{1}").edges())
    []
    >>> sorted(lad_file_to_nx_graph("smallgraphs/4K_{1}").nodes())
    [0, 1, 2, 3]

    :param filename:
    :return:
    """
    with open(filename, "r") as data:
        graph = nx.empty_graph(int(data.readline()))
        for v, line in enumerate(data):
            # each line contains the degree of the node followed by its neighbors
            graph.add_edges_from([(v, x) for x in map(int, line.split()[1:])])

        return graph


def main() -> None:
    """
    Tests to illustrate conversions between various formats.

    @return:
    """
    available_output_formats = sorted(["lad"])
    parser = argparse.ArgumentParser(
        description=f"Converts an input graph to any other format among {available_output_formats} "
                    f"and writes the output to STDOUT"
    )

    parser.add_argument("-i", "--input", help="input file name", required=True)
    parser.add_argument(
        "-f", "--format", choices=available_output_formats, help="desired output format"
    )

    args = parser.parse_args()

    print(g6file_to_lad(args.input))


if __name__ == "__main__":
    main()
