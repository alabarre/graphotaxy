"""Bipartite.py

Two-color graphs and find related structures.
D. Eppstein, May 2004.
"""

import unittest

from graph_recognition.LATER import DFS


class NonBipartite(Exception):
    pass


def TwoColor(G):
    """
    Find a bipartition of G, if one exists.
    Raises NonBipartite or returns dict mapping vertices
    to two colors (True and False).
    """
    color = {}
    for v, w, edgetype in DFS.search(G):
        if edgetype is DFS.forward:
            color[w] = not color.get(v, False)
        elif edgetype is DFS.nontree and color[v] == color[w]:
            raise NonBipartite
    return color


def isBipartite(G):
    """
    Return True if G is bipartite, False otherwise.
    """
    try:
        TwoColor(G)
        return True
    except NonBipartite:
        return False


if __name__ == "__main__":
    unittest.main()
