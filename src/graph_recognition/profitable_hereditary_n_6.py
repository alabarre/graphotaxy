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
from graph_recognition.fisc_based_recognizers import is_house_free, is_p6_free
from graph_recognition.profitable_hereditary_n_4 import is_hole_free
from graph_recognition.recognizers_utils import (
    current_module_recognizers, assign_inherited_fisc, assign_class_id,
)


# Recognizers -------------------------------------------------------------------------------------
@assign_inherited_fisc()
@assign_class_id("AUTO_3450")
@lru_cache(maxsize=None)
def is_p6_hole_house_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_3450.html

    :param graph:
    :return:
    """
    return is_hole_free(graph) and is_house_free(graph) and is_p6_free(graph)


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
