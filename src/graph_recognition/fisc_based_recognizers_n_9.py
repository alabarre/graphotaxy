"""Anthony Labarre © 2023-2026

This file contains all naïve recognizers with complexity O(n^9) for those graph classes in ISGCI
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
from graph_recognition.fisc_based_recognizers_n_5 import is_p5_free, is_k23_free, is_c5_free, is_gem_free, \
    is_house_free, is_k2_u_k3_free
from graph_recognition.profitable_hereditary_n import (
    is_2k2_free, is_chordal, )
from graph_recognition.profitable_hereditary_n_2 import (
    is_co_gem_free, is_co_chordal,
)
from graph_recognition.profitable_hereditary_n_3 import (
    is_3k1_free,
    is_triangle_free,
    is_p2up4_free,
)
from graph_recognition.profitable_hereditary_n_4 import (
    is_co_claw_free,
    is_claw_free,
)
from graph_recognition.fisc_based_recognizers_n_4 import is_c4_free
from graph_recognition.recognizers_utils import (
    assign_class_id,
    current_module_recognizers,
    assign_inherited_fisc,
)
from graph_recognition.subgraphs import is_h_free


# Recognizers -------------------------------------------------------------------------------------

# All recognizers for patterns on at most 9 vertices ----------------------------------------------
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


@assign_class_id("AUTO_2398")
@lru_cache(maxsize=None)
def is_auto_2398(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co(X_{91}), co-claw)-free.

    See https://www.graphclasses.org/classes/AUTO_2398

    Complexity of naïve matching: O(n^9)
    :type graph: networkx.Graph
    """
    return is_co_claw_free(graph) and is_h_free(graph, ["co(X_{91})"])


@assign_class_id("gc_811")
@lru_cache(maxsize=None)
def is_gc_811(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P, star_{1, 2, 5})-free.

    See https://www.graphclasses.org/classes/gc_811

    Complexity of naïve matching: O(n^9)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["P", "star_{1,2,5}"])


@assign_class_id("AUTO_2141")
@lru_cache(maxsize=None)
def is_auto_2141(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co(P), co-star_{1, 2, 5})-free.

    See https://www.graphclasses.org/classes/AUTO_2141

    Complexity of naïve matching: O(n^9)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["co(P)", "co-star_{1,2,5}"])


@assign_class_id("gc_1214")
@lru_cache(maxsize=None)
def is_gc_1214(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (X_{91}, claw)-free.

    See https://www.graphclasses.org/classes/gc_1214

    Complexity of naïve matching: O(n^9)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["claw", "X_{91}"])


@assign_class_id("AUTO_2113")
@lru_cache(maxsize=None)
def is_auto_2113(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, co(X_{91}), co-claw)-free.

    See https://www.graphclasses.org/classes/AUTO_2113

    Complexity of naïve matching: O(n^9)
    :type graph: networkx.Graph
    """
    return (
            is_2k2_free(graph)
            and is_co_claw_free(graph)
            and is_h_free(graph, ["co(X_{91})"])
    )


@assign_class_id("gc_692")
@lru_cache(maxsize=None)
def is_gc_692(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{4}, X_{91}, claw)-free.

    See https://www.graphclasses.org/classes/gc_692

    Complexity of naïve matching: O(n^9)
    :type graph: networkx.Graph
    """
    return is_claw_free(graph) and is_c4_free(graph) and is_h_free(graph, ["X_{91}"])


@assign_class_id("gc_698")
@lru_cache(maxsize=None)
def is_gc_698(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, K_{3, 3}-e, T_{2}, X_{18}, X_{94}, domino, triangle)-free.

    See https://www.graphclasses.org/classes/gc_698

    Complexity of naïve matching: O(n^9)
    :type graph: networkx.Graph
    """
    return is_triangle_free(graph) and is_h_free(
        graph, ["C_{5}", "X_{18}", "K_{3,3}-e", "domino", "T_{2}", "X_{94}"]
    )


@assign_class_id("AUTO_2116")
@lru_cache(maxsize=None)
def is_auto_2116(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{3} + e, 3K_{1}, C_{5}, co(T_{2}), co(X_{18}), co(X_{94}),
    co-domino)-free.

    See https://www.graphclasses.org/classes/AUTO_2116

    Complexity of naïve matching: O(n^9)
    :type graph: networkx.Graph
    """
    return is_3k1_free(graph) and is_h_free(
        graph,
        [
            "C_{5}",
            "co(X_{18})",
            "2K_{3} + e",
            "co-domino",
            "co(T_{2})",
            "co(X_{94})",
        ],
    )


@assign_class_id("AUTO_2090")
@lru_cache(maxsize=None)
def is_auto_2090(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, P_{5}, co(C_{6}), co(C_{7}), co(C_{8}),
    co(P_{8}), co(X_{19}), co(X_{20}), co(X_{21}), co(X_{22}), co-gem)-free.

    See https://www.graphclasses.org/classes/AUTO_2090

    Complexity of naïve matching: O(n^9)
    :type graph: networkx.Graph
    """
    return (
            is_p5_free(graph)
            and is_co_gem_free(graph)
            and is_h_free(
        graph,
        [
            "C_{5}",
            "co(C_{6})",
            "co(X_{20})",
            "co(C_{7})",
            "co(X_{19})",
            "co(C_{8})",
            "co(P_{8})",
            "co(X_{22})",
            "co(X_{21})",
        ],
    )
    )


@assign_class_id("gc_538")
@lru_cache(maxsize=None)
def is_gc_538(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, C_{6}, C_{7}, C_{8}, P_{8}, X_{19}, X_{20}, X_{21}, X_{22},
    gem, house)-free.

    See https://www.graphclasses.org/classes/gc_538

    Complexity of naïve matching: O(n^9)
    :type graph: networkx.Graph
    """
    return (
            is_gem_free(graph)
            and is_c5_free(graph)
            and is_house_free(graph)
            and is_h_free(
        graph,
        [
            "C_{6}",
            "C_{7}",
            "X_{20}",
            "P_{8}",
            "C_{8}",
            "X_{22}",
            "X_{19}",
            "X_{21}",
        ],
    )
    )


@assign_class_id("AUTO_2134")
@lru_cache(maxsize=None)
def is_auto_2134(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{6}, C_{8}, T_{2}, X_{3}, co(BW_{3}),
    co(W_{5}), co(W_{7}), co(X_{103}), co(X_{105}), co(X_{106}), co(X_{107}),
    co(X_{108}), co(X_{109}), co(X_{110}), co(X_{111}), co(X_{112}),
    co(X_{113}), co(X_{114}), co(X_{115}), co(X_{116}), co(X_{117}),
    co(X_{118}), co(X_{119}), co(X_{120}), co(X_{121}), co(X_{122}),
    co(X_{123}), co(X_{124}), co(X_{125}), co(X_{126}), co(X_{53}), co(X_{88}),
    co-X_{104})-free.

    See https://www.graphclasses.org/classes/AUTO_2134

    Complexity of naïve matching: O(n^9)
    :type graph: networkx.Graph
    """
    return is_h_free(
        graph,
        [
            "C_{6}",
            "co(W_{5})",
            "co(X_{103})",
            "co(BW_{3})",
            "co(X_{105})",
            "co(X_{106})",
            "co(X_{88})",
            "X_{3}",
            "co(X_{107})",
            "T_{2}",
            "co-X_{104}",
            "co(X_{116})",
            "co(X_{114})",
            "co(X_{119})",
            "co(X_{108})",
            "co(X_{118})",
            "co(X_{111})",
            "co(X_{115})",
            "C_{8}",
            "co(X_{122})",
            "co(X_{110})",
            "co(X_{120})",
            "co(X_{121})",
            "co(X_{123})",
            "co(X_{125})",
            "co(X_{112})",
            "co(X_{124})",
            "co(X_{113})",
            "co(X_{53})",
            "co(X_{126})",
            "co(X_{117})",
            "co(X_{109})",
            "co(W_{7})",
        ],
    )


@assign_class_id("gc_779")
@lru_cache(maxsize=None)
def is_gc_779(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (BW_{3}, W_{5}, W_{7}, X_{103}, X_{104}, X_{105}, X_{106}, X_{107},
    X_{108}, X_{109}, X_{110}, X_{111}, X_{112}, X_{113}, X_{114}, X_{115}, X_{116}, X_{117},
    X_{118}, X_{119}, X_{120}, X_{121}, X_{122}, X_{123}, X_{124}, X_{125}, X_{126}, X_{53},
    X_{88}, co(C_{6}), co(C_{8}), co(T_{2}), co(X_{3}))-free.

    See https://www.graphclasses.org/classes/gc_779

    Complexity of naïve matching: O(n^9)
    :type graph: networkx.Graph
    """
    return is_h_free(
        graph,
        [
            "co(C_{6})",
            "W_{5}",
            "X_{107}",
            "X_{104}",
            "co(X_{3})",
            "co(T_{2})",
            "X_{103}",
            "X_{88}",
            "BW_{3}",
            "X_{106}",
            "X_{105}",
            "X_{125}",
            "X_{113}",
            "X_{123}",
            "co(C_{8})",
            "X_{114}",
            "X_{115}",
            "X_{53}",
            "X_{116}",
            "X_{111}",
            "X_{117}",
            "X_{108}",
            "X_{126}",
            "X_{109}",
            "X_{121}",
            "X_{122}",
            "X_{110}",
            "X_{124}",
            "X_{119}",
            "X_{112}",
            "X_{120}",
            "X_{118}",
            "W_{7}",
        ],
    )


@assign_class_id("gc_1035")
@lru_cache(maxsize=None)
def is_gc_1035(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (6-fan, C_{4} U P_{2}, C_{5}, C_{6} U K_{1}, C_{7}, K_{2} U K_{3},
    K_{2, 3}, P_{2} U P_{4}, W_{4} U K_{1}, W_{6}, X_{132}, X_{169}, X_{176}, X_{18}, X_{197},
    X_{198}, X_{199}, X_{200}, X_{201}, X_{202}, X_{35}, X_{84}, co(C_{4} U P_{2}),
    co(C_{6} U K_{1}), co(C_{7}), co(P_{2} U P_{4}), co(W_{4} U K_{1}), co(W_{6}), co(X_{132}),
    co(X_{169}), co(X_{176}), co(X_{18}), co(X_{197}), co(X_{198}), co(X_{199}), co(X_{200}),
    co(X_{201}), co(X_{35}), co(X_{84}), co(butterfly U K_{1}), butterfly U K_{1}, co-6-fan,
    co-fish, fish)-free.

    See https://www.graphclasses.org/classes/gc_1035

    Complexity of naïve matching: O(n^9)
    :type graph: networkx.Graph
    """
    return (
            is_k23_free(graph)
            and is_p2up4_free(graph)
            and is_k2_u_k3_free(graph)
            and is_h_free(
        graph,
        [
            "C_{4} U P_{2}",
            "C_{5}",
            "X_{169}",
            "co-fish",
            "fish",
            "X_{198}",
            "co(W_{4} U K_{1})",
            "X_{197}",
            "X_{84}",
            "X_{18}",
            "co(X_{197})",
            "butterfly U K_{1}",
            "W_{4} U K_{1}",
            "co(X_{198})",
            "co(X_{169})",
            "co(X_{18})",
            "co(butterfly U K_{1})",
            "co(X_{84})",
            "co(P_{2} U P_{4})",
            "co(C_{4} U P_{2})",
            "co-6-fan",
            "C_{7}",
            "X_{35}",
            "co(C_{7})",
            "X_{199}",
            "X_{132}",
            "X_{176}",
            "C_{6} U K_{1}",
            "co(X_{176})",
            "W_{6}",
            "X_{200}",
            "co(X_{132})",
            "co(X_{200})",
            "co(W_{6})",
            "co(X_{35})",
            "6-fan",
            "co(X_{199})",
            "co(C_{6} U K_{1})",
            "X_{202}",
            "X_{201}",
            "co(X_{201})",
        ],
    )
    )


@assign_class_id("AUTO_2629")
@lru_cache(maxsize=None)
def is_auto_2629(graph: nx.Graph) -> bool:
    """



    @param graph:
    @return:
    """
    return is_co_gem_free(graph) and is_h_free(
        graph,
        [
            "P_{2} U P_{3}",
            "P_{3} U 2K_{1}",
            "X_{188}",
            "X_{214}",
            "co(W_{4})",
            "co(X_{102})",
            "co(X_{204})",
            "co(X_{209})",
            "co(X_{210})",
            "co(X_{212})",
            "co(X_{213})",
            "co(X_{215})",
            "co(X_{216})",
            "co(X_{217})",
            "co(X_{218})",
            "co(X_{86})",
        ],
    )


@assign_class_id("gc_1365")
@lru_cache(maxsize=None)
def is_gc_1365(graph: nx.Graph) -> bool:
    """



    @param graph:
    @return:
    """
    return is_gem_free(graph) and is_h_free(
        graph,
        [
            "co(P_{2} U P_{3})",
            "co(P_{3} U 2K_{1})",
            "co(X_{188})",
            "X_{214}",
            "W_{4}",
            "X_{102}",
            "X_{204}",
            "X_{209}",
            "X_{210}",
            "X_{212}",
            "X_{213}",
            "X_{215}",
            "X_{216}",
            "X_{217}",
            "X_{218}",
            "X_{86}",
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
