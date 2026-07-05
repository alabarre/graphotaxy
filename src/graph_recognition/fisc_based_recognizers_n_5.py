"""Anthony Labarre © 2023-2026

This file contains all naïve recognizers with complexity O(n^5) for those graph classes in ISGCI
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
from pyroaring import BitMap

# ----- My imports --------------------------------------------------------------------------------
from graph_recognition.fisc_based_recognizers_n_4 import is_diamond_free, is_c4_diamond_free, is_c4_free, is_4k1_free, \
    is_co_claw_free, is_claw_free, is_co_diamond_free, is_k4_free
from graph_recognition.misc_algo import (
    is_h_u_k1_free,
    is_h_u_2k1_free, must_contain_a_clique_of_size, enumerate_all_p4s, neighbors, number_of_nodes,
)
from graph_recognition.profitable_hereditary_n import (
    is_cograph,
    is_2k2_free, is_chordal, )
from graph_recognition.profitable_hereditary_n_2 import (
    is_co_gem_free, )
from graph_recognition.profitable_hereditary_n_3 import (
    is_3k1_free,
    is_triangle_free,
    is_paw_free,
    is_co_p3_free, is_co_paw_free, )
from graph_recognition.recognizers_utils import (
    assign_class_id,
    current_module_recognizers,
    assign_fisc, assign_inherited_fisc,
)
from graph_recognition.subgraphs import is_h_free


# Auxiliary functions -----------------------------------------------------------------------------
@lru_cache(maxsize=None)
def is_k_clique_free(graph: nx.Graph, k: int) -> bool:
    """
    Returns True iff graph has no clique of size k.

    @param graph:
    @param k:
    @return:
    """
    # trivial checks
    if number_of_nodes(graph) < k:
        return True

    if must_contain_a_clique_of_size(graph, k):
        return False

    # more computationally expensive, but still worthwile
    if is_triangle_free(graph):
        return True

    core = nx.core_number(graph)
    if max(core.values(), default=0) < k - 1:
        return True

    # naïve search
    candidates = BitMap(v for v in graph if core[v] >= k - 1)
    adj = {v: neighbors(graph, v) & candidates for v in candidates}

    def contains_k_clique(cands: BitMap, depth: int) -> bool:
        """
        Recursive search for a k-clique.

        :param cands:
        :param depth:
        :return:
        """
        if depth == k:
            return True

        if len(cands) < k - depth:
            return False

        while cands:
            v = next(iter(cands))
            cands.remove(v)

            if contains_k_clique(cands & adj[v], depth + 1):
                return True

        return False

    return not contains_k_clique(candidates, 0)

    # tried alternatives:
    # return is_h_free(graph, ["K_{" + str(k) + "}"]) # slower than the above
    # return len(max_weight_clique(graph, weight=None)) < k  # much slower than GSS


# Recognizers -------------------------------------------------------------------------------------

# All recognizers for patterns on at most 5 vertices ----------------------------------------------
@assign_inherited_fisc()
@assign_class_id("AUTO_1482")
@lru_cache(maxsize=None)
def is_auto_1482(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{2} U K_{3}, co-diamond)-free.

    See https://www.graphclasses.org/classes/AUTO_1482

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_co_diamond_free(graph) and is_k2_u_k3_free(graph)


@assign_fisc(["P"])
@assign_class_id("gc_814")
@lru_cache(maxsize=None)
def is_p_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is P-free.

    See https://www.graphclasses.org/classes/gc_814

    Complexity of naïve matching: O(n^5)

    :type graph: networkx.Graph
    """
    # P contains a P_4 as an induced subgraph
    if is_cograph(graph):
        return True

    return is_h_free(graph, ["P"])


@assign_fisc(["co(P)"])
@assign_class_id("AUTO_2")
@lru_cache(maxsize=None)
def is_co_p_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is co(P)-free.

    See https://www.graphclasses.org/classes/AUTO_2

    Complexity of naïve matching: O(n^5)

    :type graph: networkx.Graph
    """
    # co(P) contains a P_4 as an induced subgraph
    if is_cograph(graph):
        return True

    return is_h_free(graph, ["co(P)"])


@assign_fisc(["C_{5}"])
@assign_class_id("gc_359")
@lru_cache(maxsize=None)
def is_c5_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is C_{5}-free.

    See https://www.graphclasses.org/classes/gc_359

    Complexity of naïve matching: O(n^5)

    :type graph: networkx.Graph
    """
    # if graph has a C_5 then it has a P_4, so if graph is a cograph it has no P_4 and therefore no
    # C_5
    if is_cograph(graph):
        return True

    return is_h_free(graph, ["C_{5}"])


@assign_fisc(["P_{5}"])
@assign_class_id("gc_396")
@lru_cache(maxsize=None)
def is_p5_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is P_{5}-free.

    See https://www.graphclasses.org/classes/gc_396

    Complexity of naïve matching: O(n^5)

    :type graph: networkx.Graph
    """
    # if graph has no P_{4}, then it has no P_{5}
    if is_cograph(graph):
        return True

    """
    # note: this slows down things a lot for large graphs, removing
    # every connected P_{5}-free graph has a dominating clique of size <= 3 or a dominating P_{3}
    # see https://doi.org/10.4230/LIPIcs.ISAAC.2017.16 page 16:4
    if is_connected(graph) and (
            not has_dominating_set_of_size_at_most_2(graph) or
            not has_dominating_triangle_or_p3(graph)
    ):
        return False
    """
    return is_h_free(graph, ["P_{5}"])


@assign_fisc(["co(K_{1,4})"])
@assign_class_id("gc_673")
@lru_cache(maxsize=None)
def is_co_k14_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is co(K_{1, 4})-free.

    See https://www.graphclasses.org/classes/gc_673

    Complexity of naïve matching: O(n^5)

    :type graph: networkx.Graph
    """
    # co(K_{1,4}) = K_4 U K_1
    if is_k4_free(graph):
        return True

    return is_h_free(graph, ["co(K_{1,4})"])


@assign_fisc(["K_{2} U K_{3}"])
@assign_class_id("gc_456")
@lru_cache(maxsize=None)
def is_k2_u_k3_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is K_{2} U K_{3}-free.

    See https://www.graphclasses.org/classes/gc_456

    Complexity of naïve matching: O(n^5)

    :type graph: networkx.Graph
    """
    if is_triangle_free(graph):
        return True

    return is_h_free(graph, ["K_{2} U K_{3}"])


@assign_fisc(["co-fork"])
@assign_class_id("AUTO_3")
@lru_cache(maxsize=None)
def is_co_fork_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is co-fork-free.

    See https://www.graphclasses.org/classes/AUTO_3

    Complexity of naïve matching: O(n^5)

    :type graph: networkx.Graph
    """
    if is_diamond_free(graph):
        return True

    return is_h_free(graph, ["co-fork"])


@assign_fisc(["house"])
@assign_class_id("gc_361")
@lru_cache(maxsize=None)
def is_house_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is house-free.

    See https://www.graphclasses.org/classes/gc_361

    Complexity of naïve matching: O(n^5)

    :type graph: networkx.Graph
    """
    if is_cograph(graph) or is_triangle_free(graph):
        return True

    return is_h_free(graph, ["house"])


@assign_fisc(["gem"])
@assign_class_id("gc_354")
@lru_cache(maxsize=None)
def is_gem_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is gem-free.

    See https://www.graphclasses.org/classes/gc_354

    Complexity of naïve matching: O(n^5)

    :type graph: networkx.Graph
    """
    if is_cograph(graph):
        return True

    for a, b, c, d in enumerate_all_p4s(graph):
        if neighbors(graph, a) & neighbors(graph, b) & neighbors(graph, c) & neighbors(graph, d):
            return False

    return True
    # faster than
    # return is_h_free(graph, ["gem"])


@assign_inherited_fisc()
@assign_class_id("gc_307")
@lru_cache(maxsize=None)
def is_chordal_and_gem_free(graph: nx.Graph) -> bool:
    """

    @param graph:
    @return:
    """
    return is_chordal(graph) and is_gem_free(graph)


@assign_fisc(["K_{2,3}"])
@assign_class_id("gc_362")
@lru_cache(maxsize=None)
def is_k23_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is K_{2, 3}-free.

    See https://www.graphclasses.org/classes/gc_362

    Complexity of naïve matching: O(n^5)

    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["K_{2,3}"])


@assign_fisc(["bull"])
@assign_class_id("gc_372")
@lru_cache(maxsize=None)
def is_bull_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is bull-free.

    See https://www.graphclasses.org/classes/gc_372

    Complexity of naïve matching: O(n^5)

    :type graph: networkx.Graph
    """
    if is_cograph(graph) or is_triangle_free(graph):
        return True

    return is_h_free(graph, ["bull"])


@assign_fisc(["fork"])
@assign_class_id("gc_391")
@lru_cache(maxsize=None)
def is_fork_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is fork-free.

    See https://www.graphclasses.org/classes/gc_391

    Complexity of naïve matching: O(n^5)

    :type graph: networkx.Graph
    """
    if is_cograph(graph):
        return True

    return is_h_free(graph, ["fork"])


@assign_fisc(["K_{1,4}"])
@assign_class_id("gc_388")
@lru_cache(maxsize=None)
def is_k14_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is K_{1, 4}-free.

    See https://www.graphclasses.org/classes/gc_388

    Complexity of naïve matching: O(n^5)

    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["K_{1,4}"])


@assign_fisc(["co-cricket", "house"])
@assign_class_id("AUTO_1515")
@lru_cache(maxsize=None)
def is_auto_1515(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co-cricket, house)-free.

    See https://www.graphclasses.org/classes/AUTO_1515

    Complexity of naïve matching: O(n^5)

    :type graph: networkx.Graph
    """
    # all forbidden patterns have an induced triangle
    if is_triangle_free(graph):
        return True

    return is_house_free(graph) and is_h_free(graph, ["co-cricket"])


@assign_fisc(["K_{5}"])
@assign_class_id("AUTO_136")
@lru_cache(maxsize=None)
def is_k5_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is K_{5}-free.

    See https://www.graphclasses.org/classes/AUTO_136

    Complexity of naïve matching: O(n^5)

    :type graph: networkx.Graph
    """
    return is_k_clique_free(graph, 5)


@assign_fisc(["5K_{1}"])
@assign_class_id("gc_1377")
@lru_cache(maxsize=None)
def is_gc_1377(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is 5K_{1}-free.

    See https://www.graphclasses.org/classes/gc_1377

    Complexity of naïve matching: O(n^5)

    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["5K_{1}"])


@assign_inherited_fisc()
@assign_class_id("gc_430")
@lru_cache(maxsize=None)
def is_gc_430(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{4}, P_{5})-free.

    See https://www.graphclasses.org/classes/gc_430

    Complexity of naïve matching: O(n^5)

    :type graph: networkx.Graph
    """
    return is_c4_free(graph) and is_p5_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_463")
@lru_cache(maxsize=None)
def is_gc_463(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{5}, co-fork)-free.

    See https://www.graphclasses.org/classes/gc_463

    Complexity of naïve matching: O(n^5)

    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_co_fork_free(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_1521")
@lru_cache(maxsize=None)
def is_auto_1521(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co-diamond, house)-free.

    See https://www.graphclasses.org/classes/AUTO_1521

    Complexity of naïve matching: O(n^5)

    :type graph: networkx.Graph
    """
    return is_co_diamond_free(graph) and is_house_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_574")
@lru_cache(maxsize=None)
def is_gc_574(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (bull, house)-free.

    See https://www.graphclasses.org/classes/gc_574

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_bull_free(graph) and is_house_free(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_1528")
@lru_cache(maxsize=None)
def is_auto_1528(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (bull, co-fork)-free.

    See https://www.graphclasses.org/classes/AUTO_1528

    Complexity of naïve matching: O(n^5)

    :type graph: networkx.Graph
    """
    return is_bull_free(graph) and is_co_fork_free(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_2117")
@lru_cache(maxsize=None)
def is_auto_2117(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co(W_{4}), co-gem)-free.

    See https://www.graphclasses.org/classes/AUTO_2117

    Complexity of naïve matching: O(n^5)

    :type graph: networkx.Graph
    """
    # co(W_{4}) = 2K_{2} U K_{1} = K_{2} U co(P_{3})
    # return is_co_gem_free(graph) and is_h_u_k1_free(graph, is_2k2_free)
    return is_co_gem_free(graph) and is_h_u_2k1_free(graph, is_co_p3_free)


@assign_inherited_fisc()
@assign_class_id("gc_628")
@lru_cache(maxsize=None)
def is_gc_628(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{2, 3}, diamond)-free.

    See https://www.graphclasses.org/classes/gc_628

    Complexity of naïve matching: O(n^5)

    :type graph: networkx.Graph
    """
    return is_diamond_free(graph) and is_k23_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_427")
@lru_cache(maxsize=None)
def is_gc_427(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{5}, cricket)-free.

    See https://www.graphclasses.org/classes/gc_427

    Complexity of naïve matching: O(n^5)

    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_h_free(graph, ["cricket"])


@assign_inherited_fisc()
@assign_class_id("gc_402")
@lru_cache(maxsize=None)
def is_gc_402(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{5}, house)-free.

    See https://www.graphclasses.org/classes/gc_402

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_house_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_403")
@lru_cache(maxsize=None)
def is_gc_403(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{2, 3}, P_{5})-free.

    See https://www.graphclasses.org/classes/gc_403

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_k23_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_408")
@lru_cache(maxsize=None)
def is_gc_408(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{1, 4}, P_{5})-free.

    See https://www.graphclasses.org/classes/gc_408

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_k14_free(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_1472")
@lru_cache(maxsize=None)
def is_auto_1472(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (3K_{1}, house)-free.

    See https://www.graphclasses.org/classes/AUTO_1472

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_3k1_free(graph) and is_house_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_632")
@lru_cache(maxsize=None)
def is_gc_632(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (fork, triangle)-free.

    See https://www.graphclasses.org/classes/gc_632

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_triangle_free(graph) and is_fork_free(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_1520")
@lru_cache(maxsize=None)
def is_auto_1520(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co(P), house)-free.

    See https://www.graphclasses.org/classes/AUTO_1520

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_house_free(graph) and is_co_p_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_510")
@lru_cache(maxsize=None)
def is_gc_510(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co-gem, gem)-free.

    See https://www.graphclasses.org/classes/gc_510

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_co_gem_free(graph) and is_gem_free(graph)


@assign_fisc(["co-butterfly", "co-claw"])
@assign_class_id("AUTO_1728")
@lru_cache(maxsize=None)
def is_auto_1728(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co-butterfly, co-claw)-free.

    See https://www.graphclasses.org/classes/AUTO_1728

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_co_claw_free(graph) and is_h_free(graph, ["co-butterfly"])


@assign_inherited_fisc()
@assign_class_id("gc_413")
@lru_cache(maxsize=None)
def is_gc_413(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{1, 4}, diamond)-free.

    See https://www.graphclasses.org/classes/gc_413

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_diamond_free(graph) and is_k14_free(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_1522")
@lru_cache(maxsize=None)
def is_auto_1522(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co(K_{1, 4}), house)-free.

    See https://www.graphclasses.org/classes/AUTO_1522

    Complexity of naïve matching: O(n^5)

    :type graph: networkx.Graph
    """
    return is_co_k14_free(graph) and is_house_free(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_1481")
@lru_cache(maxsize=None)
def is_auto_1481(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (3K_{1}, co-fork)-free.

    See https://www.graphclasses.org/classes/AUTO_1481

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_3k1_free(graph) and is_co_fork_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_367")
@lru_cache(maxsize=None)
def is_gc_367(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{4}, C_{5})-free.

    See https://www.graphclasses.org/classes/gc_367

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_c4_free(graph) and is_c5_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_812")
@lru_cache(maxsize=None)
def is_gc_812(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{5}, co(P_{2} U P_{3}))-free.

    See https://www.graphclasses.org/classes/gc_812

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_h_free(graph, ["co(P_{2} U P_{3})"])


@assign_inherited_fisc()
@assign_class_id("AUTO_1512")
@lru_cache(maxsize=None)
def is_auto_1512(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, house)-free.

    See https://www.graphclasses.org/classes/AUTO_1512

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_2k2_free(graph) and is_house_free(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_1525")
@lru_cache(maxsize=None)
def is_auto_1525(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{2} U K_{3}, house)-free.

    See https://www.graphclasses.org/classes/AUTO_1525

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_k2_u_k3_free(graph) and is_house_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_409")
@lru_cache(maxsize=None)
def is_gc_409(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{5}, diamond)-free.

    See https://www.graphclasses.org/classes/gc_409

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_diamond_free(graph) and is_p5_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_572")
@lru_cache(maxsize=None)
def is_p5_bull_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{5}, bull)-free.

    See https://www.graphclasses.org/classes/gc_572

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_bull_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_1275")
@lru_cache(maxsize=None)
def is_gc_1275(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, C_{5})-free.

    See https://www.graphclasses.org/classes/gc_1275

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_2k2_free(graph) and is_c5_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_669")
@lru_cache(maxsize=None)
def is_gc_669(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, P_{5})-free.

    See https://www.graphclasses.org/classes/gc_669

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_c5_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_670")
@lru_cache(maxsize=None)
def is_gc_670(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{5}, triangle)-free.

    See https://www.graphclasses.org/classes/gc_670

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_triangle_free(graph) and is_p5_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_1213")
@lru_cache(maxsize=None)
def is_gc_1213(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (butterfly, claw)-free.

    See https://www.graphclasses.org/classes/gc_1213

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_claw_free(graph) and is_h_free(graph, ["butterfly"])


@assign_inherited_fisc()
@assign_class_id("gc_671")
@lru_cache(maxsize=None)
def is_gc_671(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{4}, P_{5})-free.

    See https://www.graphclasses.org/classes/gc_671

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_k4_free(graph) and is_p5_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_871")
@lru_cache(maxsize=None)
def is_gc_871(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (butterfly, gem)-free.

    See https://www.graphclasses.org/classes/gc_871

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    # all forbidden patterns have an induced triangle
    if is_triangle_free(graph):
        return True

    return is_gem_free(graph) and is_h_free(graph, ["butterfly"])


@assign_inherited_fisc()
@assign_class_id("gc_466")
@lru_cache(maxsize=None)
def is_gc_466(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{5}, gem)-free.

    See https://www.graphclasses.org/classes/gc_466

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_gem_free(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_1473")
@lru_cache(maxsize=None)
def is_auto_1473(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, house)-free.

    See https://www.graphclasses.org/classes/AUTO_1473

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_c5_free(graph) and is_house_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_439")
@lru_cache(maxsize=None)
def is_gc_439(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{5}, fork)-free.

    See https://www.graphclasses.org/classes/gc_439

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_fork_free(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_1462")
@lru_cache(maxsize=None)
def is_house_p2_u_p3_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{2} U P_{3}, house)-free.

    See https://www.graphclasses.org/classes/AUTO_1462

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_house_free(graph) and is_h_free(graph, ["P_{2} U P_{3}"])


@assign_inherited_fisc()
@assign_class_id("gc_700")
@lru_cache(maxsize=None)
def is_gc_700(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (W_{4}, gem)-free.

    See https://www.graphclasses.org/classes/gc_700

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    # all forbidden patterns have an induced triangle
    if is_triangle_free(graph):
        return True

    return is_gem_free(graph) and is_h_free(graph, ["W_{4}"])


@assign_inherited_fisc()
@assign_class_id("AUTO_1448")
@lru_cache(maxsize=None)
def is_auto_1448(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co(K_{1, 4}), co-paw)-free.

    See https://www.graphclasses.org/classes/AUTO_1448

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_co_paw_free(graph) and is_co_k14_free(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_1762")
@lru_cache(maxsize=None)
def is_auto_1762(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (4K_{1}, gem)-free.

    See https://www.graphclasses.org/classes/AUTO_1762

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_gem_free(graph) and is_4k1_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_920")
@lru_cache(maxsize=None)
def is_gc_920(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{1, 4}, paw)-free.

    See https://www.graphclasses.org/classes/gc_920

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_paw_free(graph) and is_k14_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_410")
@lru_cache(maxsize=None)
def is_gc_410(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P, P_{5})-free.

    See https://www.graphclasses.org/classes/gc_410

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_h_free(graph, ["P"])


@assign_inherited_fisc()
@assign_class_id("gc_438")
@lru_cache(maxsize=None)
def is_gc_438(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co(P), fork)-free.

    See https://www.graphclasses.org/classes/gc_438

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["fork", "co(P)"])


@assign_fisc(["fork", "bull"])
@assign_class_id("gc_397")
@lru_cache(maxsize=None)
def is_gc_397(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (bull, fork)-free.

    See https://www.graphclasses.org/classes/gc_397

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["fork", "bull"])


@assign_inherited_fisc()
@assign_class_id("AUTO_1510")
@lru_cache(maxsize=None)
def is_auto_1510(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P, co-fork)-free.

    See https://www.graphclasses.org/classes/AUTO_1510

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_p_free(graph) and is_co_fork_free(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_1523")
@lru_cache(maxsize=None)
def is_auto_1523(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co-claw, house)-free.

    See https://www.graphclasses.org/classes/AUTO_1523

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_co_claw_free(graph) and is_h_free(graph, ["house"])


@assign_inherited_fisc()
@assign_class_id("AUTO_1509")
@lru_cache(maxsize=None)
def is_auto_1509(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co-fork, house)-free.

    See https://www.graphclasses.org/classes/AUTO_1509

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_house_free(graph) and is_co_fork_free(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_1508")
@lru_cache(maxsize=None)
def is_auto_1508(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (fork, house)-free.

    See https://www.graphclasses.org/classes/AUTO_1508

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_fork_free(graph) and is_house_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_407")
@lru_cache(maxsize=None)
def is_gc_407(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{5}, claw)-free.

    See https://www.graphclasses.org/classes/gc_407

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_claw_free(graph) and is_p5_free(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_1453")
@lru_cache(maxsize=None)
def is_auto_1453(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co-butterfly, co-gem)-free.

    See https://www.graphclasses.org/classes/AUTO_1453

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_co_gem_free(graph) and is_h_free(graph, ["co-butterfly"])


@assign_inherited_fisc()
@assign_class_id("AUTO_1518")
@lru_cache(maxsize=None)
def is_auto_1518(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co(K_{1, 4}), co-diamond)-free.

    See https://www.graphclasses.org/classes/AUTO_1518

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_co_diamond_free(graph) and is_co_k14_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_1233")
@lru_cache(maxsize=None)
def is_gc_1233(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{4}, co-gem)-free.

    See https://www.graphclasses.org/classes/gc_1233

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_co_gem_free(graph) and is_k4_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_566")
@lru_cache(maxsize=None)
def is_gc_566(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (W_{4}, claw)-free.

    See https://www.graphclasses.org/classes/gc_566

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_claw_free(graph) and is_h_free(graph, ["W_{4}"])


@assign_inherited_fisc()
@assign_class_id("AUTO_1507")
@lru_cache(maxsize=None)
def is_auto_1507(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co-gem, house)-free.

    See https://www.graphclasses.org/classes/AUTO_1507

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_co_gem_free(graph) and is_house_free(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_1471")
@lru_cache(maxsize=None)
def is_auto_1471(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (4K_{1}, house)-free.

    See https://www.graphclasses.org/classes/AUTO_1471

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_4k1_free(graph) and is_house_free(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_2094")
@lru_cache(maxsize=None)
def is_auto_2094(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co(W_{4}), co-claw)-free.

    See https://www.graphclasses.org/classes/AUTO_2094

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_co_claw_free(graph) and is_h_u_k1_free(graph, is_2k2_free)


@assign_inherited_fisc()
@assign_class_id("gc_854")
@lru_cache(maxsize=None)
def is_gc_854(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{2, 3}, P_{4}, co-butterfly)-free.

    See https://www.graphclasses.org/classes/gc_854

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_cograph(graph) and is_k23_free(graph) and is_h_free(graph, ["co-butterfly"])


@assign_inherited_fisc()
@assign_class_id("gc_478")
@lru_cache(maxsize=None)
def is_gc_478(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{5}, bull, house)-free.

    See https://www.graphclasses.org/classes/gc_478

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_bull_free(graph) and is_house_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_518")
@lru_cache(maxsize=None)
def is_gc_518(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, co-gem, gem)-free.

    See https://www.graphclasses.org/classes/gc_518

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_co_gem_free(graph) and is_c5_free(graph) and is_gem_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_519")
@lru_cache(maxsize=None)
def is_gc_519(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (bull, co-gem, gem)-free.

    See https://www.graphclasses.org/classes/gc_519

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_co_gem_free(graph) and is_bull_free(graph) and is_gem_free(graph)


@assign_inherited_fisc()
@assign_class_id("AUTO_1502")
@lru_cache(maxsize=None)
def is_auto_1502(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{5}, bull, co-fork)-free.

    See https://www.graphclasses.org/classes/AUTO_1502

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_bull_free(graph) and is_co_fork_free(graph)


@assign_inherited_fisc()
@assign_class_id("gc_517")
@lru_cache(maxsize=None)
def is_gc_517(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, P_{5}, gem)-free.

    See https://www.graphclasses.org/classes/gc_517

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_c5_free(graph) and is_gem_free(graph)


@assign_inherited_fisc(["P"])
@assign_class_id("gc_404")
@lru_cache(maxsize=None)
def is_gc_404(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{2, 3}, P, P_{5})-free.

    See https://www.graphclasses.org/classes/gc_404

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_k23_free(graph) and is_h_free(graph, ["P"])


@assign_inherited_fisc(["butterfly"])
@assign_class_id("AUTO_1454")
@lru_cache(maxsize=None)
def is_auto_1454(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{2} U K_{3}, P_{4}, butterfly)-free.

    See https://www.graphclasses.org/classes/AUTO_1454

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_cograph(graph) and is_k2_u_k3_free(graph) and is_h_free(graph, ["butterfly"])


@assign_inherited_fisc()
@assign_class_id("gc_477")
@lru_cache(maxsize=None)
def is_gc_477(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (bull, fork, house)-free.

    See https://www.graphclasses.org/classes/gc_477

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_fork_free(graph) and is_bull_free(graph) and is_house_free(graph)


@assign_class_id("gc_475")
@lru_cache(maxsize=None)
def is_gc_475(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (bull, fork, gem)-free.

    See https://www.graphclasses.org/classes/gc_475

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["fork", "bull", "gem"])


@assign_class_id("AUTO_1504")
@lru_cache(maxsize=None)
def is_auto_1504(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (bull, co-fork, co-gem)-free.

    See https://www.graphclasses.org/classes/AUTO_1504

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_co_gem_free(graph) and is_bull_free(graph) and is_co_fork_free(graph)


@assign_class_id("AUTO_1513")
@lru_cache(maxsize=None)
def is_auto_1513(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, P_{2} U P_{3}, house)-free.

    See https://www.graphclasses.org/classes/AUTO_1513

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_house_p2_u_p3_free(graph) and is_c5_free(graph)


@assign_class_id("gc_480")
@lru_cache(maxsize=None)
def is_gc_480(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{5}, fork, house)-free.

    See https://www.graphclasses.org/classes/gc_480

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_fork_free(graph) and is_house_free(graph)


@assign_class_id("AUTO_2074")
@lru_cache(maxsize=None)
def is_auto_2074(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, P_{4}, co-dart)-free.

    See https://www.graphclasses.org/classes/AUTO_2074

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_cograph(graph) and is_2k2_free(graph) and is_h_free(graph, ["co-dart"])


@assign_class_id("gc_308")
@lru_cache(maxsize=None)
def is_gc_308(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{5}, co-fork, house)-free.

    See https://www.graphclasses.org/classes/gc_308

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_house_free(graph) and is_co_fork_free(graph)


@assign_class_id("gc_326")
@lru_cache(maxsize=None)
def is_gc_326(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{4}, P_{4}, dart)-free.

    See https://www.graphclasses.org/classes/gc_326

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_cograph(graph) and is_c4_free(graph) and is_h_free(graph, ["dart"])


@assign_class_id("gc_474")
@lru_cache(maxsize=None)
def is_gc_474(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co(P), fork, gem)-free.

    See https://www.graphclasses.org/classes/gc_474

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["gem", "fork", "co(P)"])


@assign_class_id("gc_429")
@lru_cache(maxsize=None)
def is_gc_429(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, P_{5}, co(P_{2} U P_{3}))-free.

    See https://www.graphclasses.org/classes/gc_429

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return (
            is_p5_free(graph)
            and is_c5_free(graph)
            and is_h_free(graph, ["co(P_{2} U P_{3})"])
    )


@assign_class_id("AUTO_2071")
@lru_cache(maxsize=None)
def is_auto_2071(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co(W_{4}), co-claw, co-gem)-free.

    See https://www.graphclasses.org/classes/AUTO_2071

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_co_gem_free(graph) and is_auto_2094(graph)


@assign_fisc(["claw", "W_{4}", "gem"])
@assign_class_id("gc_180")
@lru_cache(maxsize=None)
def is_gc_180(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (W_{4}, claw, gem)-free.

    See https://www.graphclasses.org/classes/gc_180

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["claw", "W_{4}", "gem"])


@assign_class_id("gc_516")
@lru_cache(maxsize=None)
def is_gc_516(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{5}, co(P), gem)-free.

    See https://www.graphclasses.org/classes/gc_516

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_h_free(graph, ["gem", "co(P)"])


@assign_class_id("AUTO_1503")
@lru_cache(maxsize=None)
def is_auto_1503(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P, P_{5}, co-fork)-free.

    See https://www.graphclasses.org/classes/AUTO_1503

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_p_free(graph) and is_co_fork_free(graph)


@assign_class_id("gc_398")
@lru_cache(maxsize=None)
def is_gc_398(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (bull, co-fork, fork)-free.

    See https://www.graphclasses.org/classes/gc_398

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_fork_free(graph) and is_co_fork_free(graph) and is_bull_free(graph)


@assign_class_id("gc_662")
@lru_cache(maxsize=None)
def is_gc_662(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (3K_{1}, C_{4}, C_{5})-free.

    See https://www.graphclasses.org/classes/gc_662

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_3k1_free(graph) and is_c4_free(graph) and is_c5_free(graph)


@assign_class_id("gc_268")
@lru_cache(maxsize=None)
def is_gc_268(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, P_{5}, house)-free.

    See https://www.graphclasses.org/classes/gc_268

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_c5_free(graph) and is_house_free(graph)


@assign_class_id("AUTO_1496")
@lru_cache(maxsize=None)
def is_auto_1496(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P, co-gem, house)-free.

    See https://www.graphclasses.org/classes/AUTO_1496

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_co_gem_free(graph) and is_p_free(graph) and is_house_free(graph)


@assign_class_id("AUTO_1495")
@lru_cache(maxsize=None)
def is_auto_1495(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, co-gem, house)-free.

    See https://www.graphclasses.org/classes/AUTO_1495

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_co_gem_free(graph) and is_c5_free(graph) and is_house_free(graph)


@assign_class_id("gc_476")
@lru_cache(maxsize=None)
def is_gc_476(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co(P), fork, house)-free.

    See https://www.graphclasses.org/classes/gc_476

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_fork_free(graph) and is_house_free(graph) and is_co_p_free(graph)


@assign_class_id("AUTO_1505")
@lru_cache(maxsize=None)
def is_auto_1505(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P, co-fork, co-gem)-free.

    See https://www.graphclasses.org/classes/AUTO_1505

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_co_gem_free(graph) and is_p_free(graph) and is_co_fork_free(graph)


@assign_class_id("AUTO_1524")
@lru_cache(maxsize=None)
def is_auto_1524(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{2} U K_{3}, co(P), house)-free.

    See https://www.graphclasses.org/classes/AUTO_1524

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_k2_u_k3_free(graph) and is_house_free(graph) and is_co_p_free(graph)


@assign_class_id("AUTO_1533")
@lru_cache(maxsize=None)
def is_auto_1533(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, P_{5}, co(P), house)-free.

    See https://www.graphclasses.org/classes/AUTO_1533

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return (
            is_p5_free(graph)
            and is_c5_free(graph)
            and is_house_free(graph)
            and is_co_p_free(graph)
    )


@assign_class_id("gc_420")
@lru_cache(maxsize=None)
def is_gc_420(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{1, 4}, P, P_{5}, fork)-free.

    See https://www.graphclasses.org/classes/gc_420

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_k14_free(graph) and is_h_free(graph, ["P", "fork"])


@assign_class_id("gc_917")
@lru_cache(maxsize=None)
def is_gc_917(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{4}, C_{5}, K_{4}, diamond)-free.

    See https://www.graphclasses.org/classes/gc_917

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_c4_diamond_free(graph) and is_h_free(graph, ["K_{4}", "C_{5}"])


@assign_class_id("gc_1303")
@lru_cache(maxsize=None)
def is_gc_1303(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (3K_{1}, C_{5}, butterfly, diamond)-free.

    See https://www.graphclasses.org/classes/gc_1303

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_3k1_free(graph) and is_h_free(graph, ["diamond", "C_{5}", "butterfly"])


@assign_class_id("AUTO_1450")
@lru_cache(maxsize=None)
def is_auto_1450(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, 4K_{1}, C_{5}, co-diamond)-free.

    See https://www.graphclasses.org/classes/AUTO_1450

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return (
            is_2k2_free(graph)
            and is_4k1_free(graph)
            and is_co_diamond_free(graph)
            and is_h_free(graph, ["C_{5}"])
    )


@assign_class_id("AUTO_1516")
@lru_cache(maxsize=None)
def is_auto_1516(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P, co-butterfly, co-fork, co-gem)-free.

    See https://www.graphclasses.org/classes/AUTO_1516

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return (
            is_co_gem_free(graph)
            and is_h_free(graph, ["co-butterfly"])
            and is_p_free(graph)
            and is_co_fork_free(graph)
    )


@assign_class_id("gc_479")
@lru_cache(maxsize=None)
def is_gc_479(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P, co(P), co-fork, fork)-free.

    See https://www.graphclasses.org/classes/gc_479

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return (
            is_p_free(graph)
            and is_co_p_free(graph)
            and is_fork_free(graph)
            and is_co_fork_free(graph)
    )


@assign_class_id("gc_224")
@lru_cache(maxsize=None)
def is_gc_224(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, P, P_{5}, house)-free.

    See https://www.graphclasses.org/classes/gc_224

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_h_free(graph, ["P", "C_{5}", "house"])


@assign_class_id("gc_421")
@lru_cache(maxsize=None)
def is_gc_421(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co(P), butterfly, fork, gem)-free.

    See https://www.graphclasses.org/classes/gc_421

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_gem_free(graph) and is_h_free(graph, ["fork", "butterfly", "co(P)"])


@assign_class_id("gc_520")
@lru_cache(maxsize=None)
def is_gc_520(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, bull, co-gem, gem)-free.

    See https://www.graphclasses.org/classes/gc_520

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_co_gem_free(graph) and is_h_free(graph, ["C_{5}", "bull", "gem"])


@assign_class_id("AUTO_1517")
@lru_cache(maxsize=None)
def is_auto_1517(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co(K_{1, 4}), co(P), co-fork, house)-free.

    See https://www.graphclasses.org/classes/AUTO_1517

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_co_k14_free(graph) and is_h_free(graph, ["co-fork", "house", "co(P)"])


@assign_class_id("gc_511")
@lru_cache(maxsize=None)
def is_gc_511(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, P, P_{5}, co(P), house)-free.

    See https://www.graphclasses.org/classes/gc_511

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_h_free(graph, ["C_{5}", "house", "P", "co(P)"])


@assign_class_id("gc_189")
@lru_cache(maxsize=None)
def is_gc_189(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P, P_{5}, co(P), co-fork, fork, house)-free.

    See https://www.graphclasses.org/classes/gc_189

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_h_free(
        graph, ["house", "P", "co(P)", "fork", "co-fork"]
    )


@assign_class_id("gc_512")
@lru_cache(maxsize=None)
def is_gc_512(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, P_{5}, co(P), co-fork, co-gem, fork)-free.

    See https://www.graphclasses.org/classes/gc_512

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return (
            is_co_gem_free(graph)
            and is_p5_free(graph)
            and is_h_free(graph, ["C_{5}", "co(P)", "fork", "co-fork"])
    )


@assign_class_id("AUTO_1498")
@lru_cache(maxsize=None)
def is_auto_1498(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, P, co-fork, fork, gem, house)-free.

    See https://www.graphclasses.org/classes/AUTO_1498

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["C_{5}", "house", "P", "gem", "fork", "co-fork"])


@assign_class_id("gc_24")
@lru_cache(maxsize=None)
def is_gc_24(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, P, P_{5}, co(P), co-fork, fork,
    house)-free.

    See https://www.graphclasses.org/classes/gc_24

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_h_free(
        graph, ["C_{5}", "house", "P", "co(P)", "fork", "co-fork"]
    )


@assign_class_id("AUTO_1497")
@lru_cache(maxsize=None)
def is_auto_1497(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, P, co(P), bull, co-fork, gem, house)-free.

    See https://www.graphclasses.org/classes/AUTO_1497

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["C_{5}", "house", "P", "co(P)", "gem", "bull", "co-fork"])


@assign_class_id("gc_513")
@lru_cache(maxsize=None)
def is_gc_513(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, P, P_{5}, co(P), bull, co-gem, fork)-free.

    See https://www.graphclasses.org/classes/gc_513

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return (
            is_co_gem_free(graph)
            and is_p5_free(graph)
            and is_h_free(graph, ["C_{5}", "P", "co(P)", "fork", "bull"])
    )


@assign_class_id("gc_1359")
@lru_cache(maxsize=None)
def is_gc_1359(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{3} U 2K_{1}, co(K_{3} U 2K_{1}), bull, co-
    cricket, co-dart, cricket, dart)-free.

    See https://www.graphclasses.org/classes/gc_1359

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return is_h_free(
        graph,
        [
            "K_{3} U 2K_{1}",
            "dart",
            "co-dart",
            "co-cricket",
            "bull",
            "co(K_{3} U 2K_{1})",
            "cricket",
        ],
    )


@assign_class_id("gc_502")
@lru_cache(maxsize=None)
def is_gc_502(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, K_{2} U K_{3}, K_{2, 3}, P, P_{2} U P_{3},
    P_{5}, co(P), co(P_{2} U P_{3}), co-fork, fork, house)-free.

    See https://www.graphclasses.org/classes/gc_502

    Complexity of naïve matching: O(n^5)
    :type graph: networkx.Graph
    """
    return (
            is_p5_free(graph)
            and is_k2_u_k3_free(graph)
            and is_k23_free(graph)
            and is_house_p2_u_p3_free(graph)
            and is_h_free(
        graph,
        [
            "C_{5}",
            "co(P_{2} U P_{3})",
            "P",
            "co(P)",
            "fork",
            "co-fork",
        ],
    )
    )


@assign_class_id("gc_503")
@lru_cache(maxsize=None)
def is_xc_9_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is XC_{9}-free, False otherwise. This is equivalent to checking whether
    graph is (P_{5}, K_{2} U K_{3}, K_{2, 3}, house, P_{2} U P_{3}, P, co(P), co(P_{2} U P_{3}),
    co-fork, fork)-free.

    https://www.graphclasses.org/classes/gc_503.html

    @param graph:
    @return:
    """
    return (
            is_p5_free(graph)
            and is_k2_u_k3_free(graph)
            and is_k23_free(graph)
            and is_house_p2_u_p3_free(graph)
            and is_h_free(
        graph,
        [
            "P",
            "co(P)",
            "co(P_{2} U P_{3})",
            "co-fork",
            "fork",
        ],
    )
    )


@assign_inherited_fisc()
@assign_class_id("gc_613")
@lru_cache(maxsize=None)
def is_xc_10_free(graph: nx.Graph) -> bool:
    """
    Characterisation found by my xc_unpacker program

    https://www.graphclasses.org/classes/gc_613.html

    @param graph:
    @return:
    """
    return is_k23_free(graph) and is_h_free(
        graph,
        ["co(K_{3} U 2K_{1})", "co(P_{2} U P_{3})", "co(P_{3} U 2K_{1})"],
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
