"""
Anthony Labarre © 2023-2025
"""
# Imports ----------------------------------------------------------------------
# ----- Standard imports -------------------------------------------------------
from collections import defaultdict
from functools import lru_cache
from itertools import combinations_with_replacement
from math import log
from time import perf_counter
from typing import Iterable

# ----- Third-party imports ---------------------------------------------------
import networkx as nx

def my_is_distance_regular(G: nx.Graph) -> bool:
    """Returns True if the graph is distance regular, False otherwise.

    A connected graph G is distance-regular if for any nodes x,y
    and any integers i,j=0,1,...,d (where d is the graph
    diameter), the number of vertices at distance i from x and
    distance j from y depends only on i,j and the graph distance
    between x and y, independently of the choice of x and y.

    Parameters
    ----------
    G: Networkx graph (undirected)

    Returns
    -------
    bool
      True if the graph is Distance Regular, False otherwise

    Examples
    --------
    >>> G = nx.hypercube_graph(6)
    >>> nx.is_distance_regular(G)
    True

    See Also
    --------
    intersection_array, global_parameters

    Notes
    -----
    For undirected and simple graphs only

    References
    ----------
    .. [1] Brouwer, A. E.; Cohen, A. M.; and Neumaier, A.
        Distance-Regular Graphs. New York: Springer-Verlag, 1989.
    .. [2] Weisstein, Eric W. "Distance-Regular Graph."
        http://mathworld.wolfram.com/Distance-RegularGraph.html

    """
    try:
        my_intersection_array(G)
        return True
    except nx.NetworkXError:
        return False


@lru_cache(maxsize=None)
def my_intersection_array(G: nx.Graph) -> Iterable:
    """Returns the intersection array of a distance-regular graph.

    Given a distance-regular graph G with integers b_i, c_i,i = 0,....,d
    such that for any 2 vertices x,y in G at a distance i=d(x,y), there
    are exactly c_i neighbors of y at a distance of i-1 from x and b_i
    neighbors of y at a distance of i+1 from x.

    A distance regular graph's intersection array is given by,
    [b_0,b_1,.....b_{d-1};c_1,c_2,.....c_d]

    Parameters
    ----------
    G: Networkx graph (undirected)

    Returns
    -------
    b,c: tuple of lists

    Examples
    --------
    >>> G = nx.icosahedral_graph()
    >>> nx.intersection_array(G)
    ([5, 2, 1], [1, 2, 5])

    References
    ----------
    .. [1] Weisstein, Eric W. "Intersection Array."
       From MathWorld--A Wolfram Web Resource.
       http://mathworld.wolfram.com/IntersectionArray.html

    See Also
    --------
    global_parameters
    """
    # the input graph is very unlikely to be distance-regular: here are the
    # number a(n) of connected simple graphs, and the number b(n) of
    # distance-regular graphs among them:
    #
    #    n  | 1 2 3 4  5   6   7     8      9       10
    #  -----+------------------------------------------------------------------
    #  a(n) | 1 1 2 6 21 112 853 11117 261080 11716571 https://oeis.org/A001349
    #  b(n) | 1 1 1 2  2   4   2     5      4        7 https://oeis.org/A241814
    #
    # in light of this, let's compute shortest path lengths as we go instead of
    # precomputing them all
    # test for regular graph (all degrees must be equal)
    if not nx.is_regular(G) or not nx.is_connected(G):
        raise nx.NetworkXError("Graph is not distance regular.")

    # path_length = dict(nx.all_pairs_shortest_path_length(G))
    path_length = defaultdict(dict)
    bint = {}  # 'b' intersection array
    cint = {}  # 'c' intersection array

    # see https://doi.org/10.1016/j.ejc.2004.07.004, Theorem 1.5 page 81: the
    # diameter of a distance-regular graph is at most (8 log_2 n) / 3, so let's
    # compute it as we go in the hope that we can stop early
    diameter = 0
    max_diameter_for_dr_graphs = (8 * log(G.number_of_nodes(), 2)) / 3
    for u, v in combinations_with_replacement(G, 2):
        if u not in path_length or v not in path_length[u]:
            path_length[u].update(nx.single_source_shortest_path_length(G, u))
            for x, distance in path_length[u].items():
                path_length[x][u] = distance

        i = path_length[u][v]
        diameter = max(diameter, i)

        # diameter too large: graph can't be distance-regular
        if diameter > max_diameter_for_dr_graphs:
            raise nx.NetworkXError("Graph is not distance regular.")

        # compute needed path lengths
        for n in G[v]:
            if n not in path_length or u not in path_length[n]:
                path_length[n].update(nx.single_source_shortest_path_length(G, n))
                for x, distance in path_length[n].items():
                    path_length[x][n] = distance

        # number of neighbors of v at a distance of i-1 from u
        # c = len([n for n in G[v] if path_length[n][u] == i - 1])
        c = sum(1 for n in G[v] if path_length[n][u] == i - 1)
        # number of neighbors of v at a distance of i+1 from u
        # b = len([n for n in G[v] if path_length[n][u] == i + 1])
        b = sum(1 for n in G[v] if path_length[n][u] == i + 1)
        # b,c are independent of u and v
        if cint.get(i, c) != c or bint.get(i, b) != b:
            raise nx.NetworkXError("Graph is not distance regular")
        bint[i] = b
        cint[i] = c

    # diameter = max(max(path_length[n].values()) for n in path_length)
    return (
        [bint.get(j, 0) for j in range(diameter)],
        [cint.get(j + 1, 0) for j in range(diameter)],
    )


# TODO don't use this, only for testing purposes, will go away when PR accepted by networkx
def my_intersection_array_2(G: nx.Graph) -> Iterable:
    """Returns the intersection array of a distance-regular graph.

    Given a distance-regular graph G with integers b_i, c_i,i = 0,....,d
    such that for any 2 vertices x,y in G at a distance i=d(x,y), there
    are exactly c_i neighbors of y at a distance of i-1 from x and b_i
    neighbors of y at a distance of i+1 from x.

    A distance regular graph's intersection array is given by,
    [b_0,b_1,.....b_{d-1};c_1,c_2,.....c_d]

    Parameters
    ----------
    G: Networkx graph (undirected)

    Returns
    -------
    b,c: tuple of lists

    Examples
    --------
    >>> G = nx.icosahedral_graph()
    >>> nx.intersection_array(G)
    ([5, 2, 1], [1, 2, 5])

    References
    ----------
    .. [1] Weisstein, Eric W. "Intersection Array."
       From MathWorld--A Wolfram Web Resource.
       http://mathworld.wolfram.com/IntersectionArray.html

    See Also
    --------
    global_parameters
    """
    # the input graph is very unlikely to be distance-regular: here are the
    # number a(n) of connected simple graphs, and the number b(n) of
    # distance-regular graphs among them:
    #
    #    n  | 1 2 3 4  5   6   7     8      9       10
    #  -----+------------------------------------------------------------------
    #  a(n) | 1 1 2 6 21 112 853 11117 261080 11716571 https://oeis.org/A001349
    #  b(n) | 1 1 1 2  2   4   2     5      4        7 https://oeis.org/A241814
    #
    # in light of this, let's compute shortest path lengths as we go instead of
    # precomputing them all
    # test for regular graph (all degrees must be equal)
    if not nx.is_regular(G) or not nx.is_connected(G):
        raise nx.NetworkXError("Graph is not distance regular.")

    # path_length = dict(nx.all_pairs_shortest_path_length(G))
    path_length = defaultdict(dict)
    bint = {}  # 'b' intersection array
    cint = {}  # 'c' intersection array

    # see https://doi.org/10.1016/j.ejc.2004.07.004, Theorem 1.5 page 81: the
    # diameter of a distance-regular graph is at most (8 log_2 n) / 3, so let's
    # compute it as we go in the hope that we can stop early
    diameter = 0
    max_diameter_for_dr_graphs = (8 * log(G.number_of_nodes(), 2)) / 3
    for u, v in combinations_with_replacement(G, 2):
        if u not in path_length or v not in path_length[u]:
            path_length[u][v] = path_length[v][u] = nx.shortest_path_length(G, u, v)

        i = path_length[u][v]
        diameter = max(diameter, i)

        # diameter too large: graph can't be distance-regular
        if diameter > max_diameter_for_dr_graphs:
            raise nx.NetworkXError("Graph is not distance regular.")

        # compute needed path lengths
        for n in G[v]:
            if n not in path_length or u not in path_length[n]:
                path_length[n][u] = path_length[u][n] = nx.shortest_path_length(G, n, u)

        # number of neighbors of v at a distance of i-1 from u
        # c = len([n for n in G[v] if path_length[n][u] == i - 1])
        c = sum(1 for n in G[v] if path_length[n][u] == i - 1)
        # number of neighbors of v at a distance of i+1 from u
        # b = len([n for n in G[v] if path_length[n][u] == i + 1])
        b = sum(1 for n in G[v] if path_length[n][u] == i + 1)
        # b,c are independent of u and v
        if cint.get(i, c) != c or bint.get(i, b) != b:
            raise nx.NetworkXError("Graph is not distance regular")
        bint[i] = b
        cint[i] = c

    # diameter = max(max(path_length[n].values()) for n in path_length)
    return (
        [bint.get(j, 0) for j in range(diameter)],
        [cint.get(j + 1, 0) for j in range(diameter)],
    )


def main() -> None:
    """

    @param graph:
    @return:
    """
    import sys

    functions = [
        nx.is_distance_regular,
        my_is_distance_regular,
        my_intersection_array_2,
    ]
    longest_function_name_length = len(max((f.__name__ for f in functions), key=len))
    print("Comparing running times for distance regularity checking")

    print()
    print("The following instances are known to be distance-regular")

    # converted the 10 graphs with the largest number of vertices from
    # https://www.distanceregular.org/ that were originally available in CSV
    instances = [  # by increasing number of vertices
        "./tests/test_data/distance-regular/coset-externarygolay.s6",
        "./tests/test_data/distance-regular/shortened-extended-ternary-golay.s6",
        "./tests/test_data/distance-regular/games.s6",
        "./tests/test_data/distance-regular/witt.s6",
        "./tests/test_data/distance-regular/iif.s6",
        "./tests/test_data/distance-regular/sksgraph.s6",
        "./tests/test_data/distance-regular/cube10.s6",
        "./tests/test_data/distance-regular/hamming4.6.s6",
        "./tests/test_data/distance-regular/grassmann263.s6",
        "./tests/test_data/distance-regular/odd7.s6",
    ]
    longest_filename_length = len(max(instances, key=len))
    longest_function_name_length = len(max((f.__name__ for f in functions), key=len))
    totals = dict({f.__name__: 0 for f in functions})
    for inst in instances:
        print(
            "now dealing with instance ", inst.ljust(longest_filename_length), end=" "
        )
        if inst.endswith("g6"):
            g = nx.read_graph6(inst)
        elif inst.endswith("s6"):
            g = nx.read_sparse6(inst)
        else:
            raise TypeError("unknown file format")

        print(f"{g.number_of_nodes()} vertices, {g.size()} edges")

        for algo in functions:
            print(
                "    now running",
                algo.__name__.ljust(longest_function_name_length),
                end=" ",
            )
            sys.stdout.flush()
            start = perf_counter()
            answer = algo(g)
            end = perf_counter()
            print(f"done in {end - start} seconds, answer is {answer}")
            totals[algo.__name__] += end - start

        print()

    print("Comparing totals:")
    for key, val in totals.items():
        print(f"    {key.ljust(longest_function_name_length)}: {val}")
    totals = dict({f.__name__: 0 for f in functions})
    num_rand_reg = 10
    n = 2048
    d = 20
    print()
    print("The following", num_rand_reg, f"instances random {d}-regular graphs")
    for i in range(num_rand_reg):
        g = nx.random_regular_graph(d, n)
        print(
            f"now dealing with instance {i} -- {g.number_of_nodes()} vertices, {g.size()} edges"
        )
        for algo in functions:
            print(
                "    now running",
                algo.__name__.ljust(longest_function_name_length),
                end=" ",
            )
            sys.stdout.flush()
            start = perf_counter()
            try:
                answer = algo(g)
            except nx.exception.NetworkXError:
                answer = False
            end = perf_counter()
            print(f"done in {end - start} seconds, answer is {answer}")
            totals[algo.__name__] += end - start

        print()

    print("Comparing totals:")
    for key, val in totals.items():
        print(f"    {key.ljust(longest_function_name_length)}: {val}")


if __name__ == "__main__":
    main()
