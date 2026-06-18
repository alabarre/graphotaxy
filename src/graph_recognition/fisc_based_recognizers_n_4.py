"""Anthony Labarre © 2023-2026

This file contains all naïve recognizers with complexity O(n^4) for those graph classes in ISGCI
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
from graph_recognition.misc_algo import (
    is_h_u_k1_free,
    complement_as_adj_mat, )
from graph_recognition.profitable_hereditary_n import (
    is_cograph,
    is_forest, )
from graph_recognition.profitable_hereditary_n_3 import (
    is_paw_free,
)
from graph_recognition.profitable_hereditary_n_4 import (
    is_c4_free,
)
from graph_recognition.recognizers_utils import (
    assign_class_id,
    current_module_recognizers,
    assign_fisc, assign_inherited_fisc,
)
from graph_recognition.subgraphs import is_h_free


# Recognizers -------------------------------------------------------------------------------------

# All recognizers for patterns on at most 4 vertices ----------------------------------------------
@assign_fisc(["diamond"])
@assign_class_id("gc_441")
@lru_cache(maxsize=None)
def is_diamond_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is diamond-free.

    See https://www.graphclasses.org/classes/gc_441

    Complexity of naïve matching: O(n^4)

    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["diamond"])


@assign_fisc(["diamond", "C_{4}"])
@assign_class_id("gc_473")
@lru_cache(maxsize=None)
def is_c4_diamond_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{4}, diamond)-free.

    See https://www.graphclasses.org/classes/gc_473

    Complexity: O(m^2) <= O(n^4) (naïve)

    :type graph: networkx.Graph
    """
    return is_c4_free(graph) and is_diamond_free(graph)


@assign_fisc(["diamond", "paw", "P_{4}"])
@assign_class_id("gc_1375")
@lru_cache(maxsize=None)
def is_p4_diamond_paw_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{4}, diamond, paw)-free.

    See https://www.graphclasses.org/classes/gc_1375

    Complexity of naïve matching: O(n^4)

    :type graph: networkx.Graph
    """
    return is_cograph(graph) and is_paw_free(graph) and is_diamond_free(graph)


@assign_fisc(["C_{4}", "P_{4}", "diamond", "paw"])
@assign_class_id("gc_1376")
@lru_cache(maxsize=None)
def is_gc_1376(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return (
            is_cograph(graph)
            and is_c4_free(graph)
            and is_diamond_free(graph)
            and is_paw_free(graph)
    )


@assign_inherited_fisc([
    "co-claw",  # C_{3} U K_{1}
    "co-butterfly",  # C_{4} U K_{1}
    "co(W_{5})",  # C_{5} U K_{1}
])  # partial fisc for (C_{n+3} U K_{1})-free, no larger such configuration in ISGCI yet
@assign_class_id("gc_1020")
@lru_cache(maxsize=None)
def is_cnplus3_u_k1_diamond_paw_free(graph: nx.Graph | HalfAdjacencyMatrix) -> bool:
    """

    https://www.graphclasses.org/classes/gc_1020.html


    Complexity: O(n^4).

    :param graph:
    :return:
    """
    # checking (C_{n+3} U K_{1})-freeness amounts to checking cycle-freeness of the graph obtained
    # by removing v U N(v) for every v in the graph
    return is_h_u_k1_free(graph, is_forest) and is_paw_free(graph) and is_diamond_free(graph)


@assign_inherited_fisc([
    "claw",  # co(C_{3} U K_{1})
    "butterfly",  # co(C_{4} U K_{1})
    "W_{5}",  # co(C_{5} U K_{1})
])  # partial fisc for co(C_{n+3} U K_{1})-free, no larger such configuration in ISGCI yet
@assign_class_id("AUTO_2276")
@lru_cache(maxsize=None)
def is_co_cnplus3_u_k1_co_diamond_co_paw_free(graph: nx.Graph | HalfAdjacencyMatrix) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_2276.html


    Complexity: O(n^4).

    :param graph:
    :return:
    """
    return is_cnplus3_u_k1_diamond_paw_free(complement_as_adj_mat(graph))


@assign_fisc([
    "claw",  # co(C_{3} U K_{1})
    "butterfly",  # co(C_{4} U K_{1})
    "W_{5}",  # co(C_{5} U K_{1})
    "co-diamond",
    "co-paw",
])  # partial fisc for co(C_{n+3} U K_{1})-free, no larger such configuration in ISGCI yet
@assign_class_id("AUTO_2276")
@lru_cache(maxsize=None)
def is_cnplus3_u_k1_co_diamond_co_paw_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_2276

    Complexity: O(n^4).

    :param graph:
    :return:
    """
    return is_cnplus3_u_k1_diamond_paw_free(complement_as_adj_mat(graph))


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
