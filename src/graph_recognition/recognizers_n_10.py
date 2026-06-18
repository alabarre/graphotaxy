"""
Anthony Labarre © 2025-2026

O(n^10) algorithms.

"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
import os
from functools import lru_cache

import networkx as nx

# ----- My imports --------------------------------------------------------------------------------
from graph_recognition.fisc_based_recognizers_n_10 import is_b_perfect_and_chordal
from graph_recognition.misc_algo import complement, co_connected_components
from graph_recognition.recognizers_utils import (
    current_module_recognizers, assign_class_id, )


# ----- Third-party imports -----------------------------------------------------------------------

# Recognizers -------------------------------------------------------------------------------------


@assign_class_id("AUTO_3856")
@lru_cache(maxsize=None)
def is_co_b_perfect_and_chordal(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_3856.html

    @param graph:
    @return:
    """
    # iterate over co-connected components instead of complementing the whole graph, in the hope
    # that we can thereby stop early
    # note: complement_as_adj_mat not usable yet: a call to is_cograph is involved, which does not
    # accept anything other than a networkx.Graph
    return all(
        is_b_perfect_and_chordal(complement(graph.subgraph(cc)))
        for cc in co_connected_components(graph)
    )


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
