"""
Anthony Labarre © 2025-2026

O(n^11) algorithms.

"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
import os
from functools import lru_cache
from itertools import combinations

# ----- Third-party imports -----------------------------------------------------------------------
import networkx as nx

# ----- My imports --------------------------------------------------------------------------------
from graph_recognition.misc_algo import number_of_edges
from graph_recognition.recognizers_utils import (
    assign_class_id,
    current_module_recognizers, )


# Recognizers -------------------------------------------------------------------------------------
@assign_class_id("gc_749")
@lru_cache(maxsize=None)
def is_maximal_clique_irreducible(graph: nx.Graph) -> bool:
    """
    A graph G is maximal clique irreducible if every maximal clique in G contains an edge that is
    not contained in any other maximal clique.

    https://www.graphclasses.org/classes/gc_749

    :param graph:
    :return:
    """
    if not graph.edges:
        return True

    # naïve algorithm: first, compute all maximal cliques. If there are more than the number of
    # edges, then at least one edge appears in more than one clique, so we can return False
    # I don't know the complexity of nx.find_cliques; we can only claim that we will not read more
    # than m elements from its result.
    max_clique_edges = list()
    m = number_of_edges(graph)
    for k, clique in enumerate(nx.find_cliques(graph), 1):
        if k > m:
            return False
        max_clique_edges.append(set(map(frozenset, combinations(clique, 2))))

    # map every clique onto a set of edges that no other clique may contain; to achieve that, we
    # examine clique i, and discard from it all edges that appear in other cliques
    # for each clique, discard from its edge set all edges in all other cliques
    for i in range(len(max_clique_edges)):
        unique_edges = max_clique_edges[i].copy()
        for j, second in enumerate(max_clique_edges):
            if j != i:
                unique_edges.discard(second)
            # if at any point the set of unique edges is empty, then current clique has no edge
            # that appears only in it, so the property is False
            if not unique_edges:
                return False

    return True


# This code segment must always be at the END of a recognizer file --------------------------------
RECOGNIZERS = current_module_recognizers(
    ".".join(
        [
            os.path.basename(os.path.dirname(__file__)),
            os.path.basename(__file__).removesuffix(".py"),
        ]
    )
)
# -------------------------------------------------------------------------------------------------
