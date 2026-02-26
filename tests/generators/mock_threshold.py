"""
Anthony Labarre (c) 2026

Tools for generating mock threshold graphs.
"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
from random import choice, shuffle

# ----- Third-party imports -----------------------------------------------------------------------
import networkx as nx


def random_mock_threshold_graph(n: int) -> nx.Graph:
    """
    Returns a random mock threshold graph on n vertices.

    >>> random_mock_threshold_graph(4).nodes
    >>> random_mock_threshold_graph(6).nodes
    
    """
    # in the words of Thomas Zaslavsky: "A mock threshold graph is like a threshold graph, but not 
    # quite. It is constructed from the null graph by adding vertices, one at a time, that are 
    # adjacent, or non-adjacent, to 0 or 1 existing vertices."
    # (https://people.math.binghamton.edu/zaslav/Tpapers/index.html)
    
    # from https://doi.org/10.1016/j.disc.2018.04.023 proposition 13: every graph on <= 5 vertices
    # is mock threshold except for C_5; so if n < 5 we simply return any random graph
    if n < 5:
        return nx.fast_gnp_random_graph(n, .5)

    # otherwise, we start with a random graph on 4 vertices, and keep adding vertices with random
    # valid connections 
    result = nx.fast_gnp_random_graph(4, .5)
    
    for k in range(4, n+1):
        # choose degree at random among valid values; k is the id of the vertex we are going to 
        # add, and it is also the number of vertices in the result before we add it
        d = choice([0, 1, k-1, k])
        
        # select d random neighbors by keeping only the first d entries in a shuffled list of nodes
        neighbors = list(result.nodes)
        shuffle(neighbors)
        neighbors = neighbors[:d]
        
        # add new vertex and its connections
        result.add_node(k)
        result.add_edges_from((k, v) for v in neighbors)
        
    return result


def main() -> None:
    """
    """
    from sys import argv
    
    if len(argv) != 3:
        print(f"Usage: {argv[0]} K N")
        print("\nGenerates at most K random mock threshold graphs on N vertices and writes them to a graph6 file")
        print('("at most" because I do not check for duplicates)')
        exit(-1)
    
    # TODO first version: I'm not checking for duplicates
    k, n = int(argv[1]), int(argv[2])
    set_of_g6_strings = set()
    for _ in range(k):
        G = random_mock_threshold_graph(n)
        set_of_g6_strings.add(nx.to_graph6_bytes(G, header=False).decode())

    print(f"Generated {len(set_of_g6_strings)} graphs on {n} vertices")
    with open(f"random-mock-threshold-{n}.g6", "w") as output:
        for g6 in set_of_g6_strings:
            output.write(g6)


if __name__ == "__main__":
    main()
