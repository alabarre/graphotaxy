"""
Anthony Labarre © 2026

Online recognition algorithms. Typical use case: a recognizer for a graph G needs to build another
graph H based on G only to verify that H satisfies some property. In that case, running an online
algorithm on an edge generator for H is much faster and memory-efficient than building H then
running a recognizer.

Algorithms in this file are intended to be used as follows:

def my_recognizer(G):
    def edge_generator(...):
        # some code that yields the edges of the graph H we would normally build

    return online_is_...(edge_generator(...))

"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
from collections import defaultdict
from typing import List, Hashable, Iterable

# ----- Third-party imports -----------------------------------------------------------------------
from networkx.utils.union_find import UnionFind


def online_connected_components(edge_generator: Iterable[tuple]) -> List[set]:
    """
    Returns the connected components of the graph described by the edge generator.

    :param edge_generator:
    :return:
    """
    disjoint_sets = UnionFind()

    for u, v in edge_generator:
        if disjoint_sets[u] != disjoint_sets[v]:
            disjoint_sets.union(u, v)

    return list(disjoint_sets.to_sets())


def online_is_forest(edge_generator: Iterable[tuple]) -> bool:
    """
    Returns True if the graph described by the edge generator has no cycle, False otherwise.

    :param edge_generator:
    :return:
    """
    disjoint_sets = UnionFind()

    for u, v in edge_generator:
        if disjoint_sets[u] == disjoint_sets[v]:
            return False

        disjoint_sets.union(u, v)

    return True


# Online bipartite graph recognition --------------------------------------------------------------
class IdentityDict(dict):
    """Behaves as a defaultdict that stores and returns the key itself when the key is missing."""
    def __missing__(self, key: Hashable) -> Hashable:
        self[key] = key
        return key


class ParityUnionFind:
    """
    UnionFind structure that supports parity. Implementation derived from the explanations at
    https://cp-algorithms.com/data_structures/disjoint_set_union.html
    """

    def __init__(self) -> None:
        """Initializes the ParityUnionFind object."""
        self.parity = defaultdict(bool)
        self.parents = IdentityDict()
        self.weights = defaultdict(lambda: 1)

    def find(self, x: Hashable) -> Hashable:
        """
        Performs the classical find operation and updates parities along the way.

        :param x:
        :return:
        """
        if self.parents[x] != x:
            parent = self.parents[x]
            root = self.find(parent)
            self.parity[x] ^= self.parity[parent]
            self.parents[x] = root
        return self.parents[x]

    def union(self, u: Hashable, v: Hashable) -> bool:
        """
        Performs the union operation while updating parities, and returns True if the update
        preserved bipartiteness, False otherwise.

        :param u:
        :param v:
        :return:
        """
        ru, rv = self.find(u), self.find(v)
        pu, pv = self.parity[u], self.parity[v]
        if ru == rv:
            return (pu ^ pv) == 1

        if self.weights[ru] < self.weights[rv]:
            # swap roots and parities
            ru, rv = rv, ru
            pu, pv = pv, pu

        self.parents[rv] = ru
        self.parity[rv] = pu ^ pv ^ True
        self.weights[ru] += self.weights[rv]

        return True


def online_is_bipartite(edge_generator: Iterable[tuple]) -> bool:
    """
    Returns True if the graph described by the edge generator is bipartite, False otherwise.

    :param edge_generator:
    :return:
    """
    disjoint_sets = ParityUnionFind()

    for u, v in edge_generator:
        if not disjoint_sets.union(u, v):
            return False

    return True
