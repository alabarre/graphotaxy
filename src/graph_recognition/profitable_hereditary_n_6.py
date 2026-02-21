"""
Anthony Labarre © 2023-2026

This file contains recognizers for profitable hereditary classes, i.e. classes that admit a
forbidden induced subgraph characterization, but can be recognized with a faster-than-naïve
algorithm.

Recognizers in this file have running time O(n^6).

"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
import os
from array import array
from functools import lru_cache
from itertools import combinations

# ----- Third-party imports -----------------------------------------------------------------------
import networkx as nx

# ----- My imports --------------------------------------------------------------------------------
from graph_recognition.misc_algo import is_h_u_k2_free, is_connected, degree_sequence
from graph_recognition.profitable_hereditary_n import is_chordal
from graph_recognition.profitable_hereditary_n_4 import is_claw_free
from graph_recognition.recognizers_utils import (
    current_module_recognizers,
    assign_class_id,
    assign_fisc,
)


# Recognizers -------------------------------------------------------------------------------------
@assign_fisc(["K_{2} U claw"])
@assign_class_id("gc_735")
@lru_cache(maxsize=None)
def is_gc_735(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is K_{2} U claw-free.

    See https://www.graphclasses.org/classes/gc_735

    Complexity: O(mn^4) <= O(n^6) (naïve)

    :type graph: networkx.Graph
    """
    return is_h_u_k2_free(graph, is_claw_free)


@assign_fisc(["C_{6}"])
@assign_class_id("gc_436")
@lru_cache(maxsize=None)
def is_c6_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is C_{6}-free.

    See https://www.graphclasses.org/classes/gc_436

    Complexity: O(m^3) <= O(n^6) (naïve)

    :type graph: networkx.Graph
    """
    # if graph has a C_6 then it has a P_4, so if graph is a cograph it has no P_4 and therefore no
    # C_6
    if is_chordal(graph):
        return True

    # the following naive algorithm turns out to be much faster than
    # return is_h_free(graph, ["C_{6}"])
    c6_degseq = array('b', [2] * 6)
    for e, f, g in combinations(graph.edges, 3):
        vertices = set(e + f + g)
        if len(vertices) == 6:
            subgraph = graph.subgraph(vertices)
            # checking connectedness is mandatory, since 2K_{3} has the same degree sequence
            if is_connected(subgraph) and degree_sequence(subgraph) == c6_degseq:
                return False

    return True


# This code segment must always be at the END of a recognizer file ------------
RECOGNIZERS = current_module_recognizers(
    ".".join(
        [
            os.path.basename(os.path.dirname(__file__)),
            os.path.basename(__file__).removesuffix(".py"),
        ]
    )
)
# -----------------------------------------------------------------------------
