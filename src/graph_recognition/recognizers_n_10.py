"""
Anthony Labarre © 2025

O(n^10) algorithms.

"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
import os
from functools import lru_cache

# ----- Third-party imports -----------------------------------------------------------------------
import networkx as nx

# ----- My imports --------------------------------------------------------------------------------
from graph_recognition.adjacency_matrix import HalfAdjacencyMatrix
from graph_recognition.fisc_based_recognizers import is_p5_free
from graph_recognition.profitable_hereditary_n import (
    is_chordal,
    is_tree,
    is_co_tree,
)
from graph_recognition.recognizers_utils import (
    assign_class_id,
    current_module_recognizers, assign_inherited_fisc,
)
from graph_recognition.subgraphs import is_h_free


# Recognizers -------------------------------------------------------------------------------------
@assign_inherited_fisc()
@assign_class_id("gc_620")
@lru_cache(maxsize=None)
def is_probe_interval_and_tree(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_620

    @param graph:
    @return:
    """
    # NOTE: nothing constrains the graph to be connected, so we should test whether it's a forest,
    # but ISGCI seems to implicitly assume connectedness
    return is_tree(graph) and is_h_free(graph, ["T_{3}", "X_{81}"])


@assign_inherited_fisc()
@assign_class_id("AUTO_2101")
@lru_cache(maxsize=None)
def is_co_t3_co_x_81_co_cycle_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_2101.html

    @param graph:
    @return:
    """
    return is_co_tree(graph) and is_h_free(graph, ["co(T_{3})", "co(X_{81})"])


@assign_inherited_fisc()
@assign_class_id("gc_1004")
@lru_cache(maxsize=None)
def is_b_perfect_and_chordal(graph: nx.Graph | HalfAdjacencyMatrix) -> bool:
    """

    https://www.graphclasses.org/classes/gc_1004

    @param graph:
    @return:
    """
    return is_chordal(graph) and is_p5_free(graph) and is_h_free(
        graph,
        [
            "3P_{3}",
            "P_{3} U P_{4}",
            "X_{102}",
            "X_{180}",
            "X_{181}",
            "X_{182}",
            "X_{183}",
            "co(A)",
        ],
    )


@assign_inherited_fisc()
@assign_class_id("AUTO_2255")
@lru_cache(maxsize=None)
def is_co_t3_co_cycle_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_2255

    @param graph:
    @return:
    """
    return is_co_tree(graph) and is_h_free(graph, ["co(T_{3})"])


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
