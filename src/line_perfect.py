"""
Anthony Labarre © 2025

Generate all graphs whose line graph is perfect. Not to be confused with the line graphs that are perfect.
"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
import os
from collections import defaultdict

# ----- Third-party imports -----------------------------------------------------------------------
import networkx as nx
from tqdm import tqdm

# ----- My imports --------------------------------------------------------------------------------
from filter import write_graphs_to_file
from graph_analyzer import process_graphs, number_of_graphs_in_file


def known_perfect_graphs():
    """
    Returns a dictionary of known perfect graphs (read from data files) indexed by number of
    vertices.

    :return:
    """
    print("Initializing known perfect graphs...")
    known_perfect_graphs_by_order = defaultdict(set)
    path_to_perfect_graph_files = "../tests/test_data/perfect=gc_56/"
    for filename in tqdm(os.listdir(path_to_perfect_graph_files)[1:], unit=" file"):
        order = int(os.path.splitext(filename)[0].split("-")[-1])
        fullpath = os.path.join(path_to_perfect_graph_files, filename)
        for graph in tqdm(
            process_graphs(fullpath),
            total=number_of_graphs_in_file(fullpath),
            unit=" graphs",
            desc=filename,
        ):
            known_perfect_graphs_by_order[order].add(graph)
    return known_perfect_graphs_by_order


def known_line_perfect_graphs_by_order(perfect_graphs):
    print("Computing connected graphs whose line graphs are perfect...")
    result = defaultdict(list)
    # go through all connected graphs
    path_to_connected_graph_files = "../tests/test_data/connected/"
    pbar = tqdm(sorted(os.listdir(path_to_connected_graph_files))[:-1], unit=" file")
    for filename in pbar:
        fullpath = os.path.join(path_to_connected_graph_files, filename)
        for graph in tqdm(
            process_graphs(fullpath),
            total=number_of_graphs_in_file(fullpath),
            unit=" graphs",
            desc=filename,
        ):
            # compute the line graph, and find out if it is perfect by looking for it in our
            # "database" of perfect graphs
            line_graph = nx.line_graph(graph)
            line_graph_order = line_graph.order()
            if line_graph_order in perfect_graphs:
                # try and find a graph isomorphic to the one we have
                for candidate in perfect_graphs[line_graph_order]:
                    if nx.is_isomorphic(line_graph, candidate):
                        result[graph.order()].append(graph)
            else:
                pbar.update()

    return result


def main():
    results_dictionary = known_line_perfect_graphs_by_order(known_perfect_graphs())
    for key, val in results_dictionary.items():
        filename = f"connected_line_perfect_{key}.g6"
        print(f"Writing {filename}")
        write_graphs_to_file(val, filename)


if __name__ == "__main__":
    main()
