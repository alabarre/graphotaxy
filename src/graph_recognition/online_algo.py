"""
Anthony Labarre © 2026

This file contains online algorithms, mostly online recognizers; i.e., algorithms that can
recognize a graph using an "edge generator" without the need to actually build the whole graph.

Usually, you will rely on "offline" recognizers, which take as input a graph. Online recognizers
are worth using when we only build graphs to verify some property (e.g., G is a member of class X
iff some complicated construction that yields a graph H based on X is, say, bipartite), or when we
don't expect G to fit in memory.

Recognition algorithms in this file are intended to be used as follows:

def my_recognizer(G):
    def edge_generator(...):
        # some code that yields the edges of the graph H we would normally build

    return online_is_...(edge_generator(...))

"""
from array import array
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
from collections import defaultdict
from typing import List, Hashable, Iterable

# ----- Third-party imports -----------------------------------------------------------------------
from networkx.utils.union_find import UnionFind

from graph_recognition.misc_algo import NUMERIC_TYPECODES


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


# Basic statistitics or parameters ----------------------------------------------------------------
def online_degree_sequence(edge_generator: Iterable[tuple]) -> array:
    """
    Returns the degree sequence of a graph, i.e. the list of all degrees sorted decreasingly. Note
    that the degree sequence will not contain zeroes, since we are only given an edge_generator.

    This function implicitly assumes that no parallel edges are provided.

    :param edge_generator:
    :return:
    """
    degrees = defaultdict(int)

    # increase the degree of both endpoints of each edge by 1; we'll divide everything by 2 later
    for u, v in edge_generator:
        degrees[u] += 1
        degrees[v] += 1

    degrees = sorted((d // 2 for d in degrees), reverse=True)

    # return array with smallest typecode
    for tc in NUMERIC_TYPECODES:
        try:
            return array(tc, degrees)
        except OverflowError:
            pass

    raise OverflowError  # no type was big enough for the elements of the degree sequence


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
