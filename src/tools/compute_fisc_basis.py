"""
Anthony Labarre © 2025

Given a set of forbidden induced subgraphs, returns a basis for these subgraphs, i.e. a minimal set
of subgraphs that all these subgraphs contain.
"""
import argparse

# Imports -----------------------------------------------------------------------------------------
# Standard imports --------------------------------------------------------------------------------
from typing import Iterable

# Third-party imports -----------------------------------------------------------------------------
import networkx as nx

# My imports --------------------------------------------------------------------------------------
from graph_recognition.smallgraphs import smallgraph_inclusion_graph


# Functions ---------------------------------------------------------------------------------------
def basis(smallgraphs: set[str]) -> set[str]:
    """
    Given a bunch of smallgraph names, returns a basis for that set, i.e. a minimal subset of that
    set such that all input subgraphs contain one of these as induced subgraph.

    >>> basis({"K_{2}", "K_{3}"})
    {'K_{2}'}

    @param smallgraphs:
    @return:
    """
    sig = smallgraph_inclusion_graph()
    retval = set()

    # an input smallgraph should belong to the basis if none of its induced subgraphs is in the
    # input set; this amounts to verifying that none of its descendants in the inclusion graph
    # appear in the input set
    for graph in smallgraphs:
        if not set(nx.descendants(sig, graph)) & smallgraphs:
            retval.add(graph)

    return retval


def main():
    # TODO argparse
    parser = argparse.ArgumentParser(description="graph classification")
    parser.add_argument("-s", "--smallgraphs", nargs="+", default=[])
    args = parser.parse_args()
    if args.smallgraphs:
        result = basis(set(args.smallgraphs))
        print(
            "Reduced",
            len(args.smallgraphs),
            "smallgraphs to the following",
            len(result),
            "smallgraphs:",
        )
        print(result)

    pass


if __name__ == "__main__":
    main()
