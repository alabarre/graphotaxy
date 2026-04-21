"""
Anthony Labarre © 2025-2026

O(n^9) algorithms.

"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
import os
from functools import lru_cache

# ----- Third-party imports -----------------------------------------------------------------------
import networkx as nx

# ----- My imports --------------------------------------------------------------------------------
from graph_recognition.profitable_hereditary_n import (
    is_chordal,
)
from graph_recognition.profitable_hereditary_n_2 import is_co_chordal
from graph_recognition.recognizers_utils import (
    assign_class_id,
    current_module_recognizers, assign_inherited_fisc,
)
from graph_recognition.subgraphs import is_h_free


# Recognizers -------------------------------------------------------------------------------------
@assign_inherited_fisc()
@assign_class_id("gc_663")
@lru_cache(maxsize=None)
def is3_k_3_cnplus4_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_663

    @param graph:
    @return:
    """
    return is_chordal(graph) and is_h_free(graph, ["3K_{3}"])


@assign_inherited_fisc()
@assign_class_id("AUTO_2108")
@lru_cache(maxsize=None)
def is_k333_co_cnplus4_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_2108.html

    @param graph:
    @return:
    """
    return is_co_chordal(graph) and is_h_free(graph, ["K_{3,3,3}"])


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
