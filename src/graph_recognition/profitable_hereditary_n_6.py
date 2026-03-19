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
from functools import lru_cache

# ----- Third-party imports -----------------------------------------------------------------------
import networkx as nx

# ----- My imports --------------------------------------------------------------------------------
from graph_recognition.misc_algo import is_h_u_k2_free
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
