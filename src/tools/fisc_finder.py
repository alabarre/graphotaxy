"""
Anthony Labarre © 2024

Program intended to find a forbidden induced subgraph characterization for a
given set of graphs.


Right now, the first goal will be to report the smallest induced subgraphs that
do not appear in any of the input graphs. We'll be more ambitious later on.

NOTE: still work in progress, don't trust results yet
"""
import argparse
import os
import sys
from itertools import combinations, product

import networkx as nx
from graph_recognition.smallgraphs import all_smallgraphs_by_order, smallgraph_inclusion_graph
from graph_recognition.subgraphs import SubgraphMatcher
from tqdm import tqdm


# TODO initialise input graphs
#   no need for classifications, we'll just need one subgraphmatcher per input graph
#
def find_all_smallgraphs(graph):
    """
    Returns a SubgraphMatcher where all smallgraphs have been queried.

    @param graph:
    @return:
    """
    matcher = SubgraphMatcher(graph)

    for size, pattern in sorted(all_smallgraphs_by_order()):
        matcher.find_induced(pattern)

    return matcher


def basis(avoided_subgraphs):
    """
    Returns the largest induced subgraphs common to all input subgraphs.

    @param avoided_subgraphs:
    @return:
    """
    # reverse graph, so that the lowest common ancestor of u and v will be the
    # largest induced subgraph contained by u and v
    all_smallgraphs = smallgraph_inclusion_graph().reverse()
    print("product:", list(product(*avoided_subgraphs)))
    return
    return set(dict(
        nx.all_pairs_lowest_common_ancestor(
            all_smallgraphs, pairs=combinations(avoided_subgraphs, 2)
        )
    ).values()) & set(avoided_subgraphs)


def main():
    parser = argparse.ArgumentParser(description="graph classification")

    parser.add_argument('-i', '--input', help='the graph file to analyse')
    # parser.add_argument(
    #     '--capabilities', action="store_true",
    #     help='shows various information about what the program can do'
    # )
    # parser.add_argument(
    #     "--print-unknown-descendants", action="store_true",
    #     help='in addition to each recognized class, print its descendants, if '
    #          'any, which have not been identified'
    # )
    # parser.add_argument(
    #     '--negative', nargs="+",
    #     help='classes to which all input graphs are known not to belong; use '
    #          'ISGCI ids'
    # )
    # parser.add_argument(
    #     '--positive', nargs="+",
    #     help="classes to which all input graphs are known to belong; use "
    #          "ISGCI ids"
    # )
    # parser.add_argument(
    #     '--todo', action="store_true",
    #     help='shows the classes that have not been identified, although '
    #          'recognizable in polynomial time, due to the lack of an '
    #          'implemented recognizer'
    # )

    if len(sys.argv) == 1:
        parser.print_help()
        # parser.print_usage()  # for just the usage line
        parser.exit()

    args = parser.parse_args()

    # if args.capabilities:
    #     print_capabilities()
    #     return

    # check that the input file exists
    if not os.path.exists(args.input):
        print("Error:", args.input, "does not exist")
        exit(-1)

    # analysis mode
    # perform_basic_checks()
    if args.input.endswith("g6"):
        # GA.add_graph(my_read_graph6(args.input))
        input_graphs = nx.read_graph6(args.input)
        # input_graphs = my_read_graph6(args.input)
    elif args.input.endswith("s6"):
        input_graphs = nx.read_sparse6(args.input)

    if not isinstance(input_graphs, list):
        input_graphs = [input_graphs]

    all_avoided_subgraphs = []
    with tqdm(
        total=len(input_graphs), desc="Analyzing input graph(s)",
        unit='graphs'
    ) as pbar:
        for graph in input_graphs:
            # print("graph.edges:", graph.edges)
            all_avoided_subgraphs.append(SubgraphMatcher(graph).minimal_missed_subgraphs())
            # print("avoided subgraphs:", all_avoided_subgraphs[-1])
            pbar.update()


    # TODO now that i have those missing subgraphs, I must figure out the common features.
    # I think its simply a matter of finding the lca's of all avoided subgraphs ... or the "highest" up among those i found? dunno

    # print(all_avoided_subgraphs)
    #print("The following minimal subgraphs are avoided by all input graphs:\n")
    #print(set.intersection(*all_avoided_subgraphs))
    #print("Basis:\n")
    #print("flattened:", sum(map(tuple, all_avoided_subgraphs), ()))
    #print(basis(all_avoided_subgraphs))
    '''

    '''


if __name__ == "__main__":
    main()
