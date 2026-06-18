"""Anthony Labarre © 2023-2026

This file contains all naïve recognizers with complexity O(n^10) for those graph classes in ISGCI
that admit a FISC (forbidden induced subgraph characterisation).

Recognizers are sorted first on the basis of the order of their largest pattern, then by number of
patterns. Additionally, every pattern in a given set will be examined by increasing size.

For now, only "fixed" subgraphs are taken into account. This excludes general configurations like
C_{n+4}, XC, XZ, ...

Unless you have a much better recognition algorithm than exhaustive search, calling is_h_free is
usually much faster.

"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
import os
from functools import lru_cache

# ----- Third-party imports -----------------------------------------------------------------------
import networkx as nx

# ----- My imports --------------------------------------------------------------------------------
from graph_recognition.adjacency_matrix import HalfAdjacencyMatrix
from graph_recognition.fisc_based_recognizers_n_5 import is_p5_free
from graph_recognition.fisc_based_recognizers_n_6 import is_p6_free
from graph_recognition.profitable_hereditary_n import (
    is_chordal, is_tree, )
from graph_recognition.profitable_hereditary_n_2 import (
    is_co_t3_co_cycle_free, )
from graph_recognition.recognizers_utils import (
    assign_class_id,
    current_module_recognizers,
    assign_inherited_fisc,
)
from graph_recognition.subgraphs import is_h_free


# Recognizers -------------------------------------------------------------------------------------

# All recognizers for patterns on at most 10 vertices ---------------------------------------------
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
@assign_class_id("AUTO_2101")
@lru_cache(maxsize=None)
def is_co_t3_co_x_81_co_cycle_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_2101.html

    @param graph:
    @return:
    """
    return is_co_t3_co_cycle_free(graph) and is_h_free(graph, ["co(X_{81})"])


@assign_class_id("gc_1002")
@lru_cache(maxsize=None)
def is_gc_1002(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (3P_{3}, P_{3} U P_{4}, P_{5}, X_{102}, X_{180}, X_{181}, X_{182},
    X_{183}, X_{184}, X_{185}, X_{186}, X_{187}, X_{188}, X_{189}, X_{190}, X_{191}, X_{192},
    X_{193}, co(5-pan), co(A), co(P_{6}), co-twin-C_{5})-free.

    See https://www.graphclasses.org/classes/gc_1002

    Complexity of naïve matching: O(n^10)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_h_free(
        graph,
        [
            "co(P_{6})",
            "co(A)",
            "co-twin-C_{5}",
            "co(5-pan)",
            "P_{3} U P_{4}",
            "X_{184}",
            "X_{102}",
            "X_{188}",
            "X_{186}",
            "X_{182}",
            "X_{185}",
            "X_{187}",
            "X_{189}",
            "X_{190}",
            "X_{192}",
            "X_{193}",
            "X_{180}",
            "X_{181}",
            "X_{191}",
            "3P_{3}",
            "X_{183}",
        ],
    )


@assign_class_id("AUTO_2248")
@lru_cache(maxsize=None)
def is_auto_2248(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (5-pan, A, P_{6}, X_{186}, co(3P_{3}), co(P_{3} U P_{4}),
    co(X_{102}), co(X_{180}), co(X_{181}), co(X_{182}), co(X_{183}), co(X_{184}), co(X_{185}),
    co(X_{187}), co(X_{188}), co(X_{189}), co(X_{190}), co(X_{191}), co(X_{192}), co(X_{193}),
    house, twin-C_{5})-free.

    See https://www.graphclasses.org/classes/AUTO_2248

    Complexity of naïve matching: O(n^10)
    :type graph: networkx.Graph
    """
    return is_p6_free(graph) and is_h_free(
        graph,
        [
            "house",
            "twin-C_{5}",
            "A",
            "5-pan",
            "co(P_{3} U P_{4})",
            "co(X_{102})",
            "co(X_{184})",
            "X_{186}",
            "co(X_{191})",
            "co(X_{187})",
            "co(X_{192})",
            "co(X_{193})",
            "co(X_{185})",
            "co(X_{182})",
            "co(X_{189})",
            "co(X_{181})",
            "co(X_{188})",
            "co(X_{190})",
            "co(X_{180})",
            "co(3P_{3})",
            "co(X_{183})",
        ],
    )


# This code segment must always be at the END of a recognizer file --------------------------------
RECOGNIZERS = current_module_recognizers(
    ".".join(
        [
            os.path.basename(os.path.dirname(__file__)),
            os.path.basename(__file__).strip(".py"),
        ]
    )
)
# -------------------------------------------------------------------------------------------------
