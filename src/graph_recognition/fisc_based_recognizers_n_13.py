"""Anthony Labarre © 2023-2026

This file contains all naïve recognizers with complexity O(n^13) for those graph classes in ISGCI
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
from graph_recognition.fisc_based_recognizers_n_5 import is_p5_free, is_house_free
from graph_recognition.profitable_hereditary_n_4 import (
    is_k4_free,
)
from graph_recognition.fisc_based_recognizers_n_4 import is_4k1_free
from graph_recognition.recognizers_utils import (
    assign_class_id,
    current_module_recognizers,
    assign_inherited_fisc,
)
from graph_recognition.subgraphs import is_h_free


# Recognizers -------------------------------------------------------------------------------------

# All recognizers for patterns on at most 13 vertices ---------------------------------------------
@assign_inherited_fisc([
    "W_{5}",
    "co(X_{39})",
    "X_{88}",
    "co(X_{38})",
    "co(C_{7})",
    "X_{89}",
    "X_{86}",
    "X_{90}",
    "X_{194}",
    "co(X_{195})",
    "co(X_{196})",
])
@assign_class_id("gc_1031")
@lru_cache(maxsize=None)
def is_gc_1031(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{4}, P_{5}, W_{5}, X_{194}, X_{86}, X_{88}, X_{89}, X_{90},
    co(C_{7}), co(X_{195}), co(X_{196}), co(X_{38}), co(X_{39}))-free.

    See https://www.graphclasses.org/classes/gc_1031

    Complexity of naïve matching: O(n^13)
    :type graph: networkx.Graph
    """
    return (
            is_k4_free(graph)
            and is_p5_free(graph)
            and is_h_free(
        graph,
        [
            "W_{5}",
            "co(X_{39})",
            "X_{88}",
            "co(X_{38})",
            "co(C_{7})",
            "X_{89}",
            "X_{86}",
            "X_{90}",
            "X_{194}",
            "co(X_{195})",
            "co(X_{196})",
        ],
    )
    )


@assign_inherited_fisc([
    "co(W_{5})",
    "co(X_{88})",
    "X_{39}",
    "co(X_{90})",
    "C_{7}",
    "co(X_{86})",
    "co(X_{89})",
    "X_{38}",
    "co(X_{194})",
    "X_{195}",
    "X_{196}",
])
@assign_class_id("AUTO_2292")
@lru_cache(maxsize=None)
def is_auto_2292(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (4K_{1}, C_{7}, X_{195}, X_{196}, X_{38}, X_{39}, co(W_{5}),
    co(X_{194}), co(X_{86}), co(X_{88}), co(X_{89}), co(X_{90}), house)-free.

    See https://www.graphclasses.org/classes/AUTO_2292

    Complexity of naïve matching: O(n^13)

    :type graph: networkx.Graph
    """
    return (
            is_4k1_free(graph)
            and is_house_free(graph)
            and is_h_free(
        graph,
        [
            "co(W_{5})",
            "co(X_{88})",
            "X_{39}",
            "co(X_{90})",
            "C_{7}",
            "co(X_{86})",
            "co(X_{89})",
            "X_{38}",
            "co(X_{194})",
            "X_{195}",
            "X_{196}",
        ],
    )
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
