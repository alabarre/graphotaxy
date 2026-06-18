"""Anthony Labarre © 2023-2026

This file contains all naïve recognizers with complexity O(n^11) for those graph classes in ISGCI
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
from graph_recognition.profitable_hereditary_n import (
    is_chordal, is_planar, )
from graph_recognition.profitable_hereditary_n_2 import (
    is_co_chordal,
)
from graph_recognition.recognizers_utils import (
    assign_class_id,
    current_module_recognizers,
    assign_fisc, assign_inherited_fisc,
)
from graph_recognition.subgraphs import is_h_free


# Recognizers -------------------------------------------------------------------------------------

# All recognizers for patterns on at most 11 vertices ---------------------------------------------
@assign_inherited_fisc()
@assign_class_id("gc_554")
@lru_cache(maxsize=None)
def is_domination_perfect_and_planar(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_554

    @param graph:
    @return:
    """
    return is_planar(graph) and is_gc_550(graph)


@assign_inherited_fisc()
@assign_class_id("gc_562")
@lru_cache(maxsize=None)
def is_cnplus4_x_59_longhorn_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_562.html

    @param graph:
    @return:
    """
    return is_chordal(graph) and is_h_free(graph, ["longhorn", "X_{59}"])


@assign_inherited_fisc()
@assign_class_id("AUTO_2093")
@lru_cache(maxsize=None)
def is_co_cnplus4_co_x_59_co_longhorn_free(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_2093

    @param graph:
    @return:
    """
    return is_co_chordal(graph) and is_h_free(graph, ["co-longhorn", "co(X_{59})"])


@assign_fisc([
    "net",
    "X_{42}",
    "co(T_{2})",
    "co(X_{205})",
    "co(X_{207})",
    "co(X_{206})",
    "co(X_{208})",
])
@assign_class_id("gc_1330")
@lru_cache(maxsize=None)
def is_gc_1330(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (X_{42}, co(T_{2}), co(X_{205}), co(X_{206}), co(X_{207}),
    co(X_{208}), net)-free.

    See https://www.graphclasses.org/classes/gc_1330

    Complexity of naïve matching: O(n^11)

    :type graph: networkx.Graph
    """
    return is_h_free(
        graph,
        [
            "net",
            "X_{42}",
            "co(T_{2})",
            "co(X_{205})",
            "co(X_{207})",
            "co(X_{206})",
            "co(X_{208})",
        ],
    )


@assign_fisc(["S_{3}", "T_{2}", "co(X_{42})", "X_{205}", "X_{207}", "X_{206}", "X_{208}"])
@assign_class_id("AUTO_1892")
@lru_cache(maxsize=None)
def is_auto_1892(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (S_{3}, T_{2}, X_{205}, X_{206}, X_{207}, X_{208}, co(X_{42}))-free.

    See https://www.graphclasses.org/classes/AUTO_1892

    Complexity of naïve matching: O(n^11)
    :type graph: networkx.Graph
    """
    return is_h_free(
        graph,
        ["S_{3}", "T_{2}", "co(X_{42})", "X_{205}", "X_{207}", "X_{206}", "X_{208}"],
    )


@assign_fisc([
    "X_{45}",
    "K_{3,3}",
    "H",
    "A",
    "co(X_{42})",
    "X_{46}",
    "X_{52}",
    "X_{49}",
    "X_{50}",
    "X_{48}",
    "X_{51}",
    "X_{47}",
    "X_{53}",
    "X_{55}",
    "X_{56}",
    "X_{54}",
    "X_{57}",
])
@assign_class_id("gc_550")
@lru_cache(maxsize=None)
def is_gc_550(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (A, H, K_{3, 3}, X_{45}, X_{46}, X_{47}, X_{48}, X_{49}, X_{50},
    X_{51}, X_{52}, X_{53}, X_{54}, X_{55}, X_{56}, X_{57}, co(X_{42}))-free.

    See https://www.graphclasses.org/classes/gc_550

    Complexity of naïve matching: O(n^11)
    :type graph: networkx.Graph
    """
    return is_h_free(
        graph,
        [
            "X_{45}",
            "K_{3,3}",
            "H",
            "A",
            "co(X_{42})",
            "X_{46}",
            "X_{52}",
            "X_{49}",
            "X_{50}",
            "X_{48}",
            "X_{51}",
            "X_{47}",
            "X_{53}",
            "X_{55}",
            "X_{56}",
            "X_{54}",
            "X_{57}",
        ],
    )


@assign_fisc([
    "co(H)",
    "co(A)",
    "2K_{3}",
    "co(X_{45})",
    "X_{42}",
    "co(X_{46})",
    "co(X_{53})",
    "co(X_{51})",
    "co(X_{48})",
    "co(X_{52})",
    "co(X_{49})",
    "co(X_{50})",
    "co(X_{47})",
    "co(X_{55})",
    "co(X_{54})",
    "co(X_{56})",
    "co(X_{57})",
])
@assign_class_id("AUTO_2092")
@lru_cache(maxsize=None)
def is_auto_2092(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{3}, X_{42}, co(A), co(H), co(X_{45}), co(X_{46}), co(X_{47}),
    co(X_{48}), co(X_{49}), co(X_{50}), co(X_{51}), co(X_{52}), co(X_{53}), co(X_{54}), co(X_{55}),
    co(X_{56}), co(X_{57}))-free.

    See https://www.graphclasses.org/classes/AUTO_2092

    Complexity of naïve matching: O(n^11)
    :type graph: networkx.Graph
    """
    return is_h_free(
        graph,
        [
            "co(H)",
            "co(A)",
            "2K_{3}",
            "co(X_{45})",
            "X_{42}",
            "co(X_{46})",
            "co(X_{53})",
            "co(X_{51})",
            "co(X_{48})",
            "co(X_{52})",
            "co(X_{49})",
            "co(X_{50})",
            "co(X_{47})",
            "co(X_{55})",
            "co(X_{54})",
            "co(X_{56})",
            "co(X_{57})",
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
