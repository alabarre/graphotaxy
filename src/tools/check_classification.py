"""
Anthony Labarre © 2023



"""
import pickle
# Imports ----------------------------------------------------------------------
import sys
from itertools import product

import networkx as nx

import isgci


# Functions --------------------------------------------------------------------
def inconsistencies(classification: nx.DiGraph) -> None:
    """
    Reports any inconsistencies in classification, in the form of pairs of
    incompatible nodes (example: a graph recognised as bipartite, but not as
    triangle-free).


    # TODO see if a compact way of reporting inconsistencies can be found; eg
    #   "a contradicts b, c, d" instead of "a and b", "a and c", "a and d", ...
    :param classification: networkx.DiGraph
    :type classification: networkx.DiGraph
    :return:
    """
    tc_isgci = nx.transitive_closure_dag(
        isgci.isgci_whole_inclusion_graph()
    )
    results = []
    # TODO for each positive node in the classification: check that none of the negative nodes are ancestors of that node
    positive_nodes = {
        class_id for class_id, data in classification.nodes(data=True)
        if data["category"] == "+"
    }
    negative_nodes = {
        class_id for class_id, data in classification.nodes(data=True)
        if data["category"] == "-"
    }
    open_nodes = {
        class_id for class_id, data in classification.nodes(data=True)
        if data["category"] == "-"
    }

    # a positive node cannot have a negative ancestor
    for plus, minus in product(positive_nodes, negative_nodes):
        if minus in tc_isgci.predecessors(plus):
            print(
                "ISSUE:", plus, "is a positive node, but its ancestor", minus,
                "is negative"
            )

    # a positive node cannot have an open ancestor
    for plus, unknown in product(positive_nodes, open_nodes):
        if unknown in tc_isgci.predecessors(plus):
            print(
                "ISSUE:", plus, "is a positive node, but its ancestor", unknown,
                "is open"
            )


def main() -> None:
    # TODO take classification as input, and check it (be more precise)
    with open(sys.argv[1], "rb") as file:
        classification = pickle.load(file)

    # classification = networkx.read_gpickle(sys.argv[1])
    inconsistencies(classification)
    pass


if __name__ == "__main__":
    main()
