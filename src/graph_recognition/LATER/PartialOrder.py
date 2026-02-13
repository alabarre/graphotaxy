"""PartialOrder.py

Various operations on partial orders and directed acyclic graphs.

D. Eppstein, July 2006.
"""

import unittest
from graph_recognition.LATER.DFS import postorder


def isTopologicalOrder(G, L):
    """Check that L is a topological ordering of directed graph G."""
    vnum = {}
    for i in range(len(L)):
        if L[i] not in G:
            return False
        vnum[L[i]] = i
    for v in G:
        if v not in vnum:
            return False
        for w in G[v]:
            if w not in vnum or vnum[w] <= vnum[v]:
                return False
    return True


def TopologicalOrder(G):
    """Find a topological ordering of directed graph G."""
    L = list(postorder(G))
    L.reverse()
    if not isTopologicalOrder(G, L):
        raise ValueError("TopologicalOrder: graph is not acyclic.")
    return L



if __name__ == "__main__":
    unittest.main()
