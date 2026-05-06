"""Anthony Labarre © 2023-2025

This file contains recognizers for profitable hereditary classes, i.e. classes that admit a
forbidden induced subgraph characterization, but can be recognized with a faster-than-naïve
algorithm.

Recognizers in this file have constant running time O(1).

"""

# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
import os
from functools import lru_cache

# ----- Third-party imports -----------------------------------------------------------------------
from networkx import Graph

# ----- My imports --------------------------------------------------------------------------------
from graph_recognition.misc_algo import is_complete, number_of_nodes, number_of_edges
from graph_recognition.recognizers_utils import (
    current_module_recognizers,
    assign_class_id,
    assign_fisc,
)


# Recognizers -------------------------------------------------------------------------------------
@assign_fisc(["2K_{1}"])
@assign_class_id("gc_1227")
@lru_cache(maxsize=None)
def is_2k1_free(graph: Graph) -> bool:
    """
    Returns True iff graph is 2K_{1}-free.

    See https://www.graphclasses.org/classes/gc_1227

    Complexity: O(1) < O(n^2) (naïve)

    :type graph: networkx.Graph
    """
    # graph is 2K_1-free iff it is complete
    return is_complete(graph)


@assign_fisc(["K_{2}"])
@assign_class_id("gc_1247")
@lru_cache(maxsize=None)
def is_k2_free(graph: Graph) -> bool:
    """
    Returns True iff graph is K_{2}-free.

    See https://www.graphclasses.org/classes/gc_1247

    Complexity: O(1) < O(n^2) (naïve)

    :type graph: networkx.Graph
    """
    # graph is K_2-free iff it has no edges
    return number_of_edges(graph) == 0


@assign_fisc(["3K_{1}", "co(P_{3})", "C_{4}"])
@assign_class_id("gc_1310")
@lru_cache(maxsize=None)
def is_3k1_c4_co_p3_free(graph: Graph) -> bool:
    """
    Returns True iff graph is (3K_{1}, C_{4}, co(P_{3}))-free.

    See https://www.graphclasses.org/classes/gc_1310

    Complexity: O(1) < O(n^4) (naïve)

    :type graph: networkx.Graph
    """
    # A graph is (3K_{1}, C_{4}, co(P_{3}))-free if it has at most one non-edge
    n = number_of_nodes(graph)
    return graph.size() >= (n * (n - 1)) // 2 - 1


@assign_fisc(["P_{3}", "triangle", "2K_{2}"])
@assign_class_id("gc_1309")
@lru_cache(maxsize=None)
def is_gc_1309(graph: Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, P_{3}, triangle)-free.

    See https://www.graphclasses.org/classes/gc_1309

    Complexity: O(1)

    :type graph: networkx.Graph
    """
    # a graph is (2K_{2}, P_{3}, triangle)-free if it has at most one edge.
    return graph.size() <= 1


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
