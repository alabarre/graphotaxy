"""
Anthony Labarre (c) 2026

Tools for generating mock threshold graphs.
"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
import subprocess
from random import choice, shuffle
from time import perf_counter

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
    
    for k in range(4, n):
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


def nauty_canonical_labeling(nauty_string: str) -> str:
    """
    
    """
    result = subprocess.run(['nauty-labelg'], input=nauty_string, stdout=subprocess.PIPE, text=True, stderr=subprocess.DEVNULL)
    return result.stdout
    

def main() -> None:
    """
    """
    from sys import argv
    # here's the number of undirected graphs on n vertices (https://oeis.org/A000088)
    number_of_graphs = (1, 1, 2, 4, 11, 34, 156, 1044, 12346, 274668, 12005168, 1018997864, 165091172592, 50502031367952, 29054155657235488, 31426485969804308768, 64001015704527557894928, 245935864153532932683719776, 1787577725145611700547878190848, 24637809253125004524383007491432768)
    
    if len(argv) != 3:
        print(f"Usage: {argv[0]} K N")
        print("\nGenerates K random mock threshold graphs on N vertices and writes them to a graph6 file")
        exit(-1)
    
    k, n = int(argv[1]), int(argv[2])
    
    if k > number_of_graphs[n]:
        print(f"Note: changing K from {k} to {number_of_graphs[n]}, which is the number of nonisomorphic graphs on {n} vertices")
        k = number_of_graphs[n]
        

    set_of_g6_strings = set()
    timeout = 10
    start = perf_counter()
    gave_up = False
    while len(set_of_g6_strings) < k:
        nx_g6_string = nx.to_graph6_bytes(random_mock_threshold_graph(n), header=False).decode()
        canon_g6 = nauty_canonical_labeling(nx_g6_string)
        if canon_g6 not in set_of_g6_strings:
            set_of_g6_strings.add(canon_g6)
            start = perf_counter()
        if perf_counter() - start > timeout:
            gave_up = True
            break

    print(f"Generated {len(set_of_g6_strings)} graphs on {n} vertices")
    with open(f"random-mock-threshold-{n}.g6", "w") as output:
        for g6 in set_of_g6_strings:
            output.write(g6)

    if gave_up:
        print(f"Note: interrupted generation because no new graph was generated in the last {timeout} seconds")

if __name__ == "__main__":
    main()
