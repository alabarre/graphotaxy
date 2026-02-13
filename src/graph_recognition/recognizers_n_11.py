"""
Anthony Labarre © 2025

O(n^11) algorithms.

"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
import os
from functools import lru_cache

# ----- Third-party imports -----------------------------------------------------------------------
import networkx as nx

# ----- My imports --------------------------------------------------------------------------------
from graph_recognition.fisc_based_recognizers import is_gc_550
from graph_recognition.profitable_hereditary_n import (
    is_chordal,
    is_planar,
)
from graph_recognition.profitable_hereditary_n_2 import is_co_chordal
from graph_recognition.recognizers_utils import (
    assign_class_id,
    current_module_recognizers,
)
from graph_recognition.subgraphs import is_h_free


# Recognizers -------------------------------------------------------------------------------------
@assign_class_id("gc_562")
@lru_cache(maxsize=None)
def is_cnplus4_x_59_longhorn_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_562.html

    @param graph:
    @return:
    """
    return is_chordal(graph) and is_h_free(graph, ["longhorn", "X_{59}"])


@assign_class_id("gc_554")
@lru_cache(maxsize=None)
def is_domination_perfect_and_planar(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_554

    @param graph:
    @return:
    """
    return is_planar(graph) and is_gc_550(graph)


@assign_class_id("AUTO_2093")
@lru_cache(maxsize=None)
def is_co_cnplus4_co_x_59_co_longhorn_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_2093

    @param graph:
    @return:
    """
    return is_co_chordal(graph) and is_h_free(graph, ["co-longhorn", "co(X_{59})"])


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
