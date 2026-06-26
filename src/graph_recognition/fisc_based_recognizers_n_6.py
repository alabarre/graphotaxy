"""Anthony Labarre © 2023-2026

This file contains all naïve recognizers with complexity O(n^6) for those graph classes in ISGCI
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

from graph_recognition.fisc_based_recognizers_n_4 import is_c4_free, is_4k1_free, is_co_claw_free, is_claw_free
# ----- My imports --------------------------------------------------------------------------------
from graph_recognition.fisc_based_recognizers_n_5 import is_p5_free, is_c5_free, is_gem_free, is_k23_free, \
    is_house_free, is_k_clique_free, is_k2_u_k3_free
from graph_recognition.misc_algo import (
    is_h_u_k1_free,
    must_contain_an_independent_set_of_size, )
from graph_recognition.profitable_hereditary_n import (
    is_cograph,
    is_p3_triangle_free,
    is_split,
    is_2k2_free, )
from graph_recognition.profitable_hereditary_n_2 import (
    is_co_gem_free, )
from graph_recognition.profitable_hereditary_n_3 import (
    is_3k1_free,
    is_triangle_free,
    is_p2up4_free,
)
from graph_recognition.profitable_hereditary_n_4 import (
    is_k4_free,
    is_co_diamond_free, is_hole_free,
)
from graph_recognition.profitable_hereditary_n_5 import is_2p3_free
from graph_recognition.recognizers_utils import (
    assign_class_id,
    current_module_recognizers,
    assign_fisc, assign_inherited_fisc, )
from graph_recognition.subgraphs import is_h_free


# Recognizers -------------------------------------------------------------------------------------

# All recognizers for patterns on at most 6 vertices ----------------------------------------------
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


@assign_fisc(["K_{6}"])
@assign_class_id("gc_1344")
@lru_cache(maxsize=None)
def is_k6_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is K_{6}-free.

    See https://www.graphclasses.org/classes/gc_1344

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_k_clique_free(graph, 6)


@assign_fisc(["6K_{1}"])
@assign_class_id("AUTO_2584")
@lru_cache(maxsize=None)
def is_6k1_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is 6K_{1}-free.

    See https://www.graphclasses.org/classes/AUTO_2584

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    if must_contain_an_independent_set_of_size(graph, 6):
        return False

    return is_h_free(graph, ["6K_{1}"])


@assign_fisc(["K_{2} U claw"])
@assign_class_id("gc_735")
@lru_cache(maxsize=None)
def is_gc_735(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is K_{2} U claw-free.

    See https://www.graphclasses.org/classes/gc_735

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["K_{2} U claw"])
    # faster than:
    # return is_h_u_k2_free(graph, is_claw_free)


@assign_fisc(["C_{6}"])
@assign_class_id("gc_436")
@lru_cache(maxsize=None)
def is_c6_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is C_{6}-free.

    See https://www.graphclasses.org/classes/gc_436

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    # if graph has a C_6 then it has a P_4, so if graph is a cograph it has no P_4 and therefore no
    # C_6
    if is_cograph(graph):
        return True

    return is_h_free(graph, ["C_{6}"])


@assign_class_id("AUTO_224")
@lru_cache(maxsize=None)
def is_auto_224(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is co(2P_{3})-free.

    See https://www.graphclasses.org/classes/AUTO_224

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["co(2P_{3})"])


@assign_class_id("AUTO_407")
@lru_cache(maxsize=None)
def is_co_domino_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is co-domino-free.

    See https://www.graphclasses.org/classes/AUTO_407

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["co-domino"])


@assign_class_id("AUTO_2123")
@lru_cache(maxsize=None)
def is_auto_2123(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is co(K_{2} U claw)-free.

    See https://www.graphclasses.org/classes/AUTO_2123

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["co(K_{2} U claw)"])


@assign_class_id("AUTO_202")
@lru_cache(maxsize=None)
def is_auto_202(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is co(P_{2} U P_{4})-free.

    See https://www.graphclasses.org/classes/AUTO_202

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["co(P_{2} U P_{4})"])


@assign_class_id("gc_592")
@lru_cache(maxsize=None)
def is_domino_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is domino-free.

    See https://www.graphclasses.org/classes/gc_592

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["domino"])


@assign_class_id("AUTO_92")
@lru_cache(maxsize=None)
def is_auto_92(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is co(C_{6})-free.

    See https://www.graphclasses.org/classes/AUTO_92

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["co(C_{6})"])


@assign_class_id("gc_816")
@lru_cache(maxsize=None)
def is_e_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is E-free.

    See https://www.graphclasses.org/classes/gc_816

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["E"])


@assign_class_id("gc_638")
@lru_cache(maxsize=None)
def is_p6_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is P_{6}-free.

    See https://www.graphclasses.org/classes/gc_638

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    # if graph has no P_{4}, then it has no P_{6}
    if is_cograph(graph):
        return True

    return is_h_free(graph, ["P_{6}"])


@assign_class_id("gc_376")
@lru_cache(maxsize=None)
def is_s3_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is S_{3}-free.

    See https://www.graphclasses.org/classes/gc_376

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["S_{3}"])


@assign_class_id("AUTO_41")
@lru_cache(maxsize=None)
def is_co_p6_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is co(P_{6})-free.

    See https://www.graphclasses.org/classes/AUTO_41

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["co(P_{6})"])


@assign_class_id("gc_1357")
@lru_cache(maxsize=None)
def is_net_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is net-free.

    See https://www.graphclasses.org/classes/gc_1357

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["net"])


@assign_class_id("AUTO_497")
@lru_cache(maxsize=None)
def is_co_e_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is co(E)-free.

    See https://www.graphclasses.org/classes/AUTO_497

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["co(E)"])


@assign_class_id("AUTO_1635")
@lru_cache(maxsize=None)
def is_auto_1635(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (3K_{1}, co(C_{6}))-free.

    See https://www.graphclasses.org/classes/AUTO_1635

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_3k1_free(graph) and is_h_free(graph, ["co(C_{6})"])


@assign_class_id("gc_815")
@lru_cache(maxsize=None)
def is_gc_815(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{4}, P_{6})-free.

    See https://www.graphclasses.org/classes/gc_815

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_c4_free(graph) and is_p6_free(graph)


@assign_fisc(["P_{5}", "co(P_{6})"])
@assign_class_id("gc_677")
@lru_cache(maxsize=None)
def is_p5_co_p6_free(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{5}, co(P_{6}))-free.

    See https://www.graphclasses.org/classes/gc_677

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_co_p6_free(graph)


@assign_class_id("gc_633")
@lru_cache(maxsize=None)
def is_gc_633(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (cross, triangle)-free.

    See https://www.graphclasses.org/classes/gc_633

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_triangle_free(graph) and is_h_free(graph, ["cross"])


@assign_class_id("AUTO_1441")
@lru_cache(maxsize=None)
def is_auto_1441(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (3K_{1}, co(3K_{2}))-free.

    See https://www.graphclasses.org/classes/AUTO_1441

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_3k1_free(graph) and is_h_free(graph, ["co(3K_{2})"])


@assign_class_id("AUTO_1511")
@lru_cache(maxsize=None)
def is_auto_1511(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{3}, house)-free.

    See https://www.graphclasses.org/classes/AUTO_1511

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["house", "2K_{3}"])


@assign_class_id("AUTO_1465")
@lru_cache(maxsize=None)
def is_auto_1465(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co(E), co(P))-free.

    See https://www.graphclasses.org/classes/AUTO_1465

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["co(P)", "co(E)"])


@assign_class_id("gc_1076")
@lru_cache(maxsize=None)
def is_gc_1076(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{4}, co(2P_{3}))-free.

    See https://www.graphclasses.org/classes/gc_1076

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_cograph(graph) and is_h_free(graph, ["co(2P_{3})"])


@assign_class_id("AUTO_1451")
@lru_cache(maxsize=None)
def is_auto_1451(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (3K_{1}, co(2P_{3}))-free.

    See https://www.graphclasses.org/classes/AUTO_1451

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_3k1_free(graph) and is_h_free(graph, ["co(2P_{3})"])


@assign_class_id("AUTO_1447")
@lru_cache(maxsize=None)
def is_auto_1447(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (3K_{1}, co(P_{6}))-free.

    See https://www.graphclasses.org/classes/AUTO_1447

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_3k1_free(graph) and is_co_p6_free(graph)


@assign_class_id("gc_678")
@lru_cache(maxsize=None)
def is_gc_678(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{5}, co(C_{6}))-free.

    See https://www.graphclasses.org/classes/gc_678

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_h_free(graph, ["co(C_{6})"])


@assign_class_id("gc_929")
@lru_cache(maxsize=None)
def is_gc_929(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (3K_{2}, triangle)-free.

    See https://www.graphclasses.org/classes/gc_929

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_triangle_free(graph) and is_h_free(graph, ["3K_{2}"])


@assign_class_id("AUTO_1477")
@lru_cache(maxsize=None)
def is_auto_1477(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (3K_{1}, co(E))-free.

    See https://www.graphclasses.org/classes/AUTO_1477

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_3k1_free(graph) and is_h_free(graph, ["co(E)"])


@assign_class_id("AUTO_1445")
@lru_cache(maxsize=None)
def is_auto_1445(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (3K_{1}, co(X_{172}))-free.

    See https://www.graphclasses.org/classes/AUTO_1445

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_3k1_free(graph) and is_h_free(graph, ["co(X_{172})"])


@assign_class_id("gc_431")
@lru_cache(maxsize=None)
def is_gc_431(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{3, 3}, P_{5})-free.

    See https://www.graphclasses.org/classes/gc_431

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_h_free(graph, ["K_{3,3}"])


@assign_class_id("AUTO_1470")
@lru_cache(maxsize=None)
def is_auto_1470(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{6}, house)-free.

    See https://www.graphclasses.org/classes/AUTO_1470

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["house", "C_{6}"])


@assign_class_id("AUTO_1767")
@lru_cache(maxsize=None)
def is_auto_1767(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co(P_{6}), co-claw)-free.

    See https://www.graphclasses.org/classes/AUTO_1767

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_co_claw_free(graph) and is_co_p6_free(graph)


@assign_class_id("AUTO_1443")
@lru_cache(maxsize=None)
def is_auto_1443(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{4}, S_{3})-free.

    See https://www.graphclasses.org/classes/AUTO_1443

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_c4_free(graph) and is_h_free(graph, ["S_{3}"])


@assign_class_id("gc_922")
@lru_cache(maxsize=None)
def is_gc_922(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{6}, triangle)-free.

    See https://www.graphclasses.org/classes/gc_922

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_triangle_free(graph) and is_p6_free(graph)


@assign_class_id("gc_635")
@lru_cache(maxsize=None)
def is_gc_635(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (H, triangle)-free.

    See https://www.graphclasses.org/classes/gc_635

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_triangle_free(graph) and is_h_free(graph, ["H"])


@assign_class_id("gc_648")
@lru_cache(maxsize=None)
def is_gc_648(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{3, 3}-e, P_{5})-free.

    See https://www.graphclasses.org/classes/gc_648

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_h_free(graph, ["K_{3,3}-e"])


@assign_class_id("gc_925")
@lru_cache(maxsize=None)
def is_gc_925(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{2} U claw, triangle)-free.

    See https://www.graphclasses.org/classes/gc_925

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_triangle_free(graph) and is_gc_735(graph)


@assign_class_id("gc_433")
@lru_cache(maxsize=None)
def is_gc_433(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{6}, co(C_{6}))-free.

    See https://www.graphclasses.org/classes/gc_433

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["C_{6}", "co(C_{6})"])


@assign_class_id("gc_373")
@lru_cache(maxsize=None)
def is_gc_373(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (S_{3}, net)-free.

    See https://www.graphclasses.org/classes/gc_373

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["net", "S_{3}"])


@assign_class_id("AUTO_1442")
@lru_cache(maxsize=None)
def is_auto_1442(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{4}, S_{3})-free.

    See https://www.graphclasses.org/classes/AUTO_1442

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_k4_free(graph) and is_h_free(graph, ["S_{3}"])


@assign_class_id("AUTO_1476")
@lru_cache(maxsize=None)
def is_auto_1476(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{3} + e, house)-free.

    See https://www.graphclasses.org/classes/AUTO_1476

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["house", "2K_{3} + e"])


@assign_class_id("gc_1234")
@lru_cache(maxsize=None)
def is_gc_1234(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{6}, claw)-free.

    See https://www.graphclasses.org/classes/gc_1234

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_claw_free(graph) and is_p6_free(graph)


@assign_class_id("gc_1024")
@lru_cache(maxsize=None)
def is_gc_1024(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{6}, triangle)-free.

    See https://www.graphclasses.org/classes/gc_1024

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_triangle_free(graph) and is_h_free(graph, ["C_{6}"])


@assign_class_id("gc_137")
@lru_cache(maxsize=None)
def is_gc_137(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (claw, net)-free.

    See https://www.graphclasses.org/classes/gc_137

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["claw", "net"])


@assign_class_id("gc_927")
@lru_cache(maxsize=None)
def is_gc_927(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, net)-free.

    See https://www.graphclasses.org/classes/gc_927

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_2k2_free(graph) and is_h_free(graph, ["net"])


@assign_class_id("AUTO_1480")
@lru_cache(maxsize=None)
def is_auto_1480(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (3K_{1}, co-cross)-free.

    See https://www.graphclasses.org/classes/AUTO_1480

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_3k1_free(graph) and is_h_free(graph, ["co-cross"])


@assign_class_id("gc_636")
@lru_cache(maxsize=None)
def is_gc_636(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (E, triangle)-free.

    See https://www.graphclasses.org/classes/gc_636

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_triangle_free(graph) and is_e_free(graph)


@assign_class_id("AUTO_1460")
@lru_cache(maxsize=None)
def is_auto_1460(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, co(P_{6}))-free.

    See https://www.graphclasses.org/classes/AUTO_1460

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_2k2_free(graph) and is_co_p6_free(graph)


@assign_class_id("gc_914")
@lru_cache(maxsize=None)
def is_gc_914(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2P_{3}, triangle)-free.

    See https://www.graphclasses.org/classes/gc_914

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    # check instead that the graph is both (triangle, P_{3})-free and 2P_{3}-free, since the former
    # can be achieved in time O(m+n); in the worst-case, we'll have to check 2P_{3}-freeness too,
    # but the running time will be the same as checking for (triangle, 2P_{3})-directly
    return is_p3_triangle_free(graph) and is_2p3_free(graph)


@assign_class_id("AUTO_2154")
@lru_cache(maxsize=None)
def is_auto_2154(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (3K_{1}, co(K_{2} U claw))-free.

    See https://www.graphclasses.org/classes/AUTO_2154

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_3k1_free(graph) and is_h_free(graph, ["co(K_{2} U claw)"])


@assign_class_id("AUTO_1700")
@lru_cache(maxsize=None)
def is_auto_1700(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2P_{3}, P_{4})-free.

    See https://www.graphclasses.org/classes/AUTO_1700

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_cograph(graph) and is_2p3_free(graph)


@assign_class_id("gc_924")
@lru_cache(maxsize=None)
def is_gc_924(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (X_{172}, triangle)-free.

    See https://www.graphclasses.org/classes/gc_924

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_triangle_free(graph) and is_h_free(graph, ["X_{172}"])


@assign_class_id("AUTO_1446")
@lru_cache(maxsize=None)
def is_auto_1446(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (3K_{1}, co(P_{2} U P_{4}))-free.

    See https://www.graphclasses.org/classes/AUTO_1446

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_3k1_free(graph) and is_h_free(graph, ["co(P_{2} U P_{4})"])


@assign_class_id("AUTO_1478")
@lru_cache(maxsize=None)
def is_auto_1478(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (3K_{1}, co(H))-free.

    See https://www.graphclasses.org/classes/AUTO_1478

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_3k1_free(graph) and is_h_free(graph, ["co(H)"])


@assign_class_id("AUTO_1537")
@lru_cache(maxsize=None)
def is_auto_1537(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (S_{3}, co-claw)-free.

    See https://www.graphclasses.org/classes/AUTO_1537

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_co_claw_free(graph) and is_s3_free(graph)


@assign_class_id("AUTO_2153")
@lru_cache(maxsize=None)
def is_auto_2153(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (3K_{1}, co(K_{1, 5}))-free.

    See https://www.graphclasses.org/classes/AUTO_2153

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_3k1_free(graph) and is_h_free(graph, ["co(K_{1,5})"])


@assign_class_id("gc_756")
@lru_cache(maxsize=None)
def is_gc_756(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (E, P)-free.

    See https://www.graphclasses.org/classes/gc_756

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["P", "E"])


@assign_class_id("gc_928")
@lru_cache(maxsize=None)
def is_gc_928(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (4K_{1}, net)-free.

    See https://www.graphclasses.org/classes/gc_928

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_4k1_free(graph) and is_net_free(graph)


@assign_class_id("gc_585")
@lru_cache(maxsize=None)
def is_gc_585(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (domino, gem, house)-free.

    See https://www.graphclasses.org/classes/gc_585

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_gem_free(graph) and is_house_free(graph) and is_domino_free(graph)


@assign_class_id("AUTO_2102")
@lru_cache(maxsize=None)
def is_auto_2102(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co(W_{4}), co(W_{5}), co-butterfly)-free.

    See https://www.graphclasses.org/classes/AUTO_2102

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    #      co(W_{4})
    return (
            is_h_u_k1_free(graph, is_2k2_free)
            and is_h_free(graph, ["co-butterfly"])
            and is_h_free(graph, ["co(W_{5})"])
    )


@assign_class_id("AUTO_1488")
@lru_cache(maxsize=None)
def is_auto_1488(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P_{5}, co-domino, co-gem)-free.

    See https://www.graphclasses.org/classes/AUTO_1488

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return (
            is_p5_free(graph) and is_co_gem_free(graph) and is_h_free(graph, ["co-domino"])
    )


@assign_class_id("AUTO_1490")
@lru_cache(maxsize=None)
def is_auto_1490(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co(A), co(P_{6}), co-domino)-free.

    See https://www.graphclasses.org/classes/AUTO_1490

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["co(A)", "co(P_{6})", "co-domino"])


@assign_class_id("gc_1074")
@lru_cache(maxsize=None)
def is_gc_1074(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, P_{4}, co(2P_{3}))-free.

    See https://www.graphclasses.org/classes/gc_1074

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_cograph(graph) and is_2k2_free(graph) and is_h_free(graph, ["co(2P_{3})"])


@assign_class_id("gc_1279")
@lru_cache(maxsize=None)
def is_gc_1279(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2P_{3}, C_{4}, C_{6})-free.

    See https://www.graphclasses.org/classes/gc_1279

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_c4_free(graph) and is_h_free(graph, ["C_{6}", "2P_{3}"])


@assign_class_id("gc_355")
@lru_cache(maxsize=None)
def is_gc_355(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (S_{3}, claw, net)-free.

    See https://www.graphclasses.org/classes/gc_355

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["claw", "net", "S_{3}"])


@assign_class_id("gc_1075")
@lru_cache(maxsize=None)
def is_gc_1075(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2P_{3}, C_{4}, P_{4})-free.

    See https://www.graphclasses.org/classes/gc_1075

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_cograph(graph) and is_c4_free(graph) and is_h_free(graph, ["2P_{3}"])


@assign_class_id("gc_428")
@lru_cache(maxsize=None)
def is_gc_428(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{3, 3}-e, P_{5}, X_{98})-free.

    See https://www.graphclasses.org/classes/gc_428

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_h_free(graph, ["X_{98}", "K_{3,3}-e"])


@assign_class_id("AUTO_1821")
@lru_cache(maxsize=None)
def is_auto_1821(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, co(2P_{3}), co(C_{6}))-free.

    See https://www.graphclasses.org/classes/AUTO_1821

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_2k2_free(graph) and is_h_free(graph, ["co(C_{6})", "co(2P_{3})"])


@assign_class_id("AUTO_1530")
@lru_cache(maxsize=None)
def is_auto_1530(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (S_{3}, co-claw, net)-free.

    See https://www.graphclasses.org/classes/AUTO_1530

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_co_claw_free(graph) and is_h_free(graph, ["net", "S_{3}"])


@assign_class_id("gc_273")
@lru_cache(maxsize=None)
def is_gc_273(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, P_{6}, co(P_{6}))-free.

    See https://www.graphclasses.org/classes/gc_273

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_p6_free(graph) and is_h_free(graph, ["C_{5}", "co(P_{6})"])


@assign_class_id("AUTO_1491")
@lru_cache(maxsize=None)
def is_auto_1491(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{4}, co(A), co(H))-free.

    See https://www.graphclasses.org/classes/AUTO_1491

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_c4_free(graph) and is_h_free(graph, ["co(A)", "co(H)"])


@assign_class_id("gc_563")
@lru_cache(maxsize=None)
def is_gc_563(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (A, P_{6}, domino)-free.

    See https://www.graphclasses.org/classes/gc_563

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_p6_free(graph) and is_h_free(graph, ["A", "domino"])


@assign_class_id("AUTO_1514")
@lru_cache(maxsize=None)
def is_auto_1514(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{3} + e, co(X_{98}), house)-free.

    See https://www.graphclasses.org/classes/AUTO_1514

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["house", "2K_{3} + e", "co(X_{98})"])


@assign_class_id("gc_542")
@lru_cache(maxsize=None)
def is_gc_542(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, A, H)-free.

    See https://www.graphclasses.org/classes/gc_542

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_2k2_free(graph) and is_h_free(graph, ["H", "A"])


@assign_class_id("AUTO_1466")
@lru_cache(maxsize=None)
def is_auto_1466(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (3K_{2}, E, P_{2} U P_{4}, net)-free.

    See https://www.graphclasses.org/classes/AUTO_1466

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_p2up4_free(graph) and is_h_free(graph, ["net", "E", "3K_{2}"])


@assign_class_id("gc_411")
@lru_cache(maxsize=None)
def is_gc_411(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P, P_{5}, co(3K_{2}), gem)-free.

    See https://www.graphclasses.org/classes/gc_411

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_h_free(graph, ["P", "gem", "co(3K_{2})"])


@assign_class_id("AUTO_1710")
@lru_cache(maxsize=None)
def is_auto_1710(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (3K_{1}, C_{5}, co(C_{6}), co(P_{6}))-free.

    See https://www.graphclasses.org/classes/AUTO_1710

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_3k1_free(graph) and is_h_free(graph, ["C_{5}", "co(C_{6})", "co(P_{6})"])


@assign_class_id("AUTO_1636")
@lru_cache(maxsize=None)
def is_auto_1636(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, C_{5}, co(C_{6}), net)-free.

    See https://www.graphclasses.org/classes/AUTO_1636

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_2k2_free(graph) and is_h_free(graph, ["C_{5}", "net", "co(C_{6})"])


@assign_class_id("gc_1026")
@lru_cache(maxsize=None)
def is_gc_1026(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{4}, C_{5}, C_{6}, S_{3})-free.

    See https://www.graphclasses.org/classes/gc_1026

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_c4_free(graph) and is_h_free(graph, ["C_{5}", "C_{6}", "S_{3}"])


@assign_class_id("AUTO_1563")
@lru_cache(maxsize=None)
def is_auto_1563(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (3K_{2}, C_{5}, P_{2} U P_{4}, net)-free.

    See https://www.graphclasses.org/classes/AUTO_1563

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_p2up4_free(graph) and is_h_free(
        graph, ["P_{2} U P_{4}", "C_{5}", "net", "3K_{2}"]
    )


@assign_class_id("gc_1176")
@lru_cache(maxsize=None)
def is_gc_1176(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, C_{6}, P_{6}, triangle)-free.

    See https://www.graphclasses.org/classes/gc_1176

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return (
            is_triangle_free(graph)
            and is_p6_free(graph)
            and is_h_free(graph, ["C_{5}", "C_{6}"])
    )


@assign_class_id("AUTO_1519")
@lru_cache(maxsize=None)
def is_auto_1519(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (3K_{2}, co(P), co-gem, house)-free.

    See https://www.graphclasses.org/classes/AUTO_1519

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_co_gem_free(graph) and is_h_free(graph, ["house", "co(P)", "3K_{2}"])


@assign_class_id("gc_748")
@lru_cache(maxsize=None)
def is_gc_748(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (S_{3}, co(3K_{2}), co(E), co(P_{2} U P_{4}))-free.

    See https://www.graphclasses.org/classes/gc_748

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["S_{3}", "co(P_{2} U P_{4})", "co(E)", "co(3K_{2})"])


@assign_class_id("gc_960")
@lru_cache(maxsize=None)
def is_gc_960(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, S_{3}, co(3K_{2}), co(P_{2} U P_{4}))-free.

    See https://www.graphclasses.org/classes/gc_960

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["C_{5}", "S_{3}", "co(P_{2} U P_{4})", "co(3K_{2})"])


@assign_class_id("AUTO_756")
@lru_cache(maxsize=None)
def is_auto_756(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (A, H, K_{3, 3}, X_{45}, triangle)-free.

    See https://www.graphclasses.org/classes/AUTO_756

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_triangle_free(graph) and is_h_free(graph, ["X_{45}", "K_{3,3}", "H", "A"])


@assign_class_id("gc_260")
@lru_cache(maxsize=None)
def is_gc_260(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, P_{5}, co-fish, fish, house)-free.

    See https://www.graphclasses.org/classes/gc_260

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_h_free(graph, ["C_{5}", "house", "co-fish", "fish"])


@assign_class_id("AUTO_2766")
@lru_cache(maxsize=None)
def is_auto_2766(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{3}, 3K_{1}, co(A), co(H), co(X_{45}))-free.

    See https://www.graphclasses.org/classes/AUTO_2766

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_3k1_free(graph) and is_h_free(
        graph, ["co(H)", "co(A)", "2K_{3}", "co(X_{45})"]
    )


@assign_class_id("AUTO_734")
@lru_cache(maxsize=None)
def is_auto_734(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, C_{6}, P_{6}, co(C_{6}), co(P_{6}))-free.

    See https://www.graphclasses.org/classes/AUTO_734

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_p6_free(graph) and is_h_free(
        graph, ["C_{5}", "C_{6}", "co(P_{6})", "co(C_{6})"]
    )


@assign_class_id("gc_627")
@lru_cache(maxsize=None)
def is_gc_627(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, K_{3, 3}, K_{3, 3}+e, P_{4}, co(2P_{3}))-free.

    See https://www.graphclasses.org/classes/gc_627

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return (
            is_cograph(graph)
            and is_2k2_free(graph)
            and is_h_free(graph, ["co(2P_{3})", "K_{3,3}", "K_{3,3}+e"])
    )


@assign_class_id("gc_38")
@lru_cache(maxsize=None)
def is_gc_38(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, C_{4}, C_{5}, S_{3}, net)-free.

    See https://www.graphclasses.org/classes/gc_38

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_split(graph) and is_h_free(graph, ["S_{3}", "net"])


@assign_class_id("AUTO_1483")
@lru_cache(maxsize=None)
def is_auto_1483(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{3}, 2P_{3}, C_{4}, K_{3} U P_{3}, P_{4})-free.

    See https://www.graphclasses.org/classes/AUTO_1483

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return (
            is_cograph(graph)
            and is_c4_free(graph)
            and is_h_free(graph, ["K_{3} U P_{3}", "2P_{3}", "2K_{3}"])
    )


@assign_class_id("gc_845")
@lru_cache(maxsize=None)
def is_gc_845(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (A, C_{5}, C_{6}, P_{6}, domino, house)-free.

    See https://www.graphclasses.org/classes/gc_845

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_p6_free(graph) and is_h_free(
        graph, ["C_{5}", "house", "C_{6}", "A", "domino"]
    )


@assign_class_id("gc_809")
@lru_cache(maxsize=None)
def is_gc_809(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{2, 3}, P, P_{5}, X_{163}, X_{95}, diamond)-free.

    See https://www.graphclasses.org/classes/gc_809

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return (
            is_p5_free(graph)
            and is_k23_free(graph)
            and is_h_free(graph, ["diamond", "P", "X_{163}", "X_{95}"])
    )


@assign_class_id("AUTO_3700")
@lru_cache(maxsize=None)
def is_auto_3700(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, C_{4}, C_{5}, S_{3}, co-claw, net)-free.

    See https://www.graphclasses.org/classes/AUTO_3700

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return (
            is_split(graph)
            and is_co_claw_free(graph)
            and is_h_free(graph, ["S_{3}", "net"])
    )


@assign_class_id("AUTO_2140")
@lru_cache(maxsize=None)
def is_auto_2140(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (K_{2} U K_{3}, co(P), co(X_{163}), co(X_{95}), co-diamond,
    house)-free.

    See https://www.graphclasses.org/classes/AUTO_2140

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return (
            is_co_diamond_free(graph)
            and is_k2_u_k3_free(graph)
            and is_h_free(
        graph,
        ["house", "co(P)", "co(X_{163})", "co(X_{95})"],
    )
    )


@assign_class_id("AUTO_1456")
@lru_cache(maxsize=None)
def is_auto_1456(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, P_{5}, co(A), co(C_{6}), co(P_{6}), co-domino)-free.

    See https://www.graphclasses.org/classes/AUTO_1456

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_h_free(
        graph, ["C_{5}", "co(P_{6})", "co(A)", "co(C_{6})", "co-domino"]
    )


@assign_class_id("AUTO_1765")
@lru_cache(maxsize=None)
def is_auto_1765(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{2}, C_{4}, C_{5}, S_{3}, claw, net)-free.

    See https://www.graphclasses.org/classes/AUTO_1765

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_split(graph) and is_h_free(graph, ["claw", "S_{3}", "net"])


@assign_class_id("gc_188")
@lru_cache(maxsize=None)
def is_gc_188(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (P, P_{5}, S_{3}, co(P), co-fork, fork, house, net)-free.

    See https://www.graphclasses.org/classes/gc_188

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_h_free(
        graph, ["house", "P", "co(P)", "fork", "co-fork", "S_{3}", "net"]
    )


@assign_class_id("gc_17")
@lru_cache(maxsize=None)
def is_gc_17(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{5}, P, P_{5}, S_{3}, co(P), co-fork, fork, house, net)-free.

    See https://www.graphclasses.org/classes/gc_17

    Complexity of naïve matching: O(n^6)

    :type graph: networkx.Graph
    """
    return is_p5_free(graph) and is_h_free(
        graph,
        ["C_{5}", "house", "P", "co(P)", "fork", "co-fork", "S_{3}", "net"],
    )


@assign_class_id("gc_1037")
@lru_cache(maxsize=None)
def is_gc_1037(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (C_{4} U P_{2}, C_{5}, C_{6}, K_{2} U K_{3}, K_{2,
    3}, P_{6}, W_{4}, X_{18}, X_{5}, X_{84}, co(C_{4} U P_{2}), co(C_{6}),
    co(P_{6}), co(W_{4}), co(X_{18}), co(X_{5}), co(X_{84}), antenna, co-
    antenna, co-domino, co-fish, domino, fish)-free.

    See https://www.graphclasses.org/classes/gc_1037

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return (
            is_p6_free(graph)
            and is_k2_u_k3_free(graph)
            and is_k23_free(graph)
            and is_h_free(
        graph,
        [
            "C_{4} U P_{2}",
            "W_{4}",
            "co(W_{4})",
            "C_{5}",
            "co-fish",
            "co(P_{6})",
            "fish",
            "co-domino",
            "C_{6}",
            "X_{84}",
            "co(X_{5})",
            "co-antenna",
            "X_{18}",
            "co(C_{6})",
            "domino",
            "X_{5}",
            "antenna",
            "co(X_{18})",
            "co(X_{84})",
            "co(C_{4} U P_{2})",
        ],
    )
    )


@assign_class_id("gc_842")
@lru_cache(maxsize=None)
def is_gc_842(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{3} + e, A, C_{5}, C_{6}, E, H, K_{3, 3}-e, R,
    X_{168}, X_{171}, X_{18}, X_{45}, X_{5}, X_{58}, X_{84}, X_{95}, co(A),
    co(C_{6}), co(E), co(H), co(R), co(X_{168}), co(X_{171}), co(X_{18}),
    co(X_{45}), co(X_{5}), co(X_{58}), co(X_{84}), co(X_{95}), antenna, co-
    antenna, co-domino, co-fish, co-twin-house, domino, fish, twin-house)-free.

    See https://www.graphclasses.org/classes/gc_842

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_h_free(
        graph,
        [
            "C_{5}",
            "co-fish",
            "fish",
            "co(R)",
            "co(X_{171})",
            "2K_{3} + e",
            "co(A)",
            "co-domino",
            "co(X_{95})",
            "C_{6}",
            "X_{84}",
            "co(X_{5})",
            "X_{168}",
            "co(X_{45})",
            "co-antenna",
            "co(H)",
            "X_{45}",
            "X_{58}",
            "co(E)",
            "X_{18}",
            "co(C_{6})",
            "X_{95}",
            "X_{171}",
            "domino",
            "X_{5}",
            "R",
            "antenna",
            "E",
            "A",
            "H",
            "co(X_{58})",
            "co(X_{18})",
            "K_{3,3}-e",
            "co-twin-house",
            "twin-house",
            "co(X_{84})",
            "co(X_{168})",
        ],
    )


@assign_class_id("gc_840")
@lru_cache(maxsize=None)
def is_gc_840(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{3} + e, A, C_{5}, C_{6}, E, K_{3, 3}-e,
    P_{6}, R, X_{166}, X_{167}, X_{169}, X_{170}, X_{171}, X_{172}, X_{18},
    X_{45}, X_{5}, X_{58}, X_{84}, X_{95}, X_{98}, co(A), co(C_{6}), co(E),
    co(P_{6}), co(R), co(X_{166}), co(X_{167}), co(X_{169}), co(X_{170}),
    co(X_{171}), co(X_{172}), co(X_{18}), co(X_{45}), co(X_{5}), co(X_{58}),
    co(X_{84}), co(X_{95}), co(X_{98}), antenna, co-antenna, co-domino, co-fish,
    co-twin-house, domino, fish, twin-house)-free.

    See https://www.graphclasses.org/classes/gc_840

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_h_free(
        graph,
        [
            "C_{5}",
            "X_{169}",
            "co(P_{6})",
            "X_{166}",
            "co-fish",
            "fish",
            "co(R)",
            "co(X_{171})",
            "2K_{3} + e",
            "X_{170}",
            "co(A)",
            "co-domino",
            "X_{167}",
            "co(X_{95})",
            "C_{6}",
            "P_{6}",
            "X_{84}",
            "co(X_{5})",
            "X_{172}",
            "co(X_{98})",
            "co(X_{45})",
            "co-antenna",
            "X_{45}",
            "X_{58}",
            "co(E)",
            "co(X_{170})",
            "X_{18}",
            "co(X_{172})",
            "co(C_{6})",
            "X_{95}",
            "X_{171}",
            "X_{98}",
            "domino",
            "X_{5}",
            "R",
            "antenna",
            "E",
            "A",
            "co(X_{169})",
            "co(X_{58})",
            "co(X_{18})",
            "K_{3,3}-e",
            "co(X_{167})",
            "co-twin-house",
            "co(X_{166})",
            "twin-house",
            "co(X_{84})",
        ],
    )


@assign_class_id("gc_1108")
@lru_cache(maxsize=None)
def is_gc_1108(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{3} + e, 5-pan, A, C_{6}, E, K_{3, 3}-e,
    P_{6}, R, X_{166}, X_{167}, X_{169}, X_{170}, X_{171}, X_{172}, X_{18},
    X_{37}, X_{45}, X_{5}, X_{58}, X_{84}, X_{95}, X_{98}, co(5-pan), co(A),
    co(C_{6}), co(E), co(P_{6}), co(R), co(X_{166}), co(X_{167}), co(X_{169}),
    co(X_{170}), co(X_{171}), co(X_{172}), co(X_{18}), co(X_{37}), co(X_{45}),
    co(X_{5}), co(X_{58}), co(X_{84}), co(X_{95}), co(X_{98}), antenna, co-
    antenna, co-domino, co-fish, co-twin-C_{5}, co-twin-house, domino, fish,
    twin-C_{5}, twin-house)-free.

    See https://www.graphclasses.org/classes/gc_1108

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_h_free(
        graph,
        [
            "X_{169}",
            "co(P_{6})",
            "X_{166}",
            "co-fish",
            "fish",
            "co(R)",
            "X_{37}",
            "co(X_{171})",
            "2K_{3} + e",
            "X_{170}",
            "co(A)",
            "co-domino",
            "twin-C_{5}",
            "X_{167}",
            "co(X_{95})",
            "C_{6}",
            "P_{6}",
            "co(X_{37})",
            "co-twin-C_{5}",
            "co(5-pan)",
            "X_{84}",
            "co(X_{5})",
            "X_{172}",
            "co(X_{98})",
            "co(X_{45})",
            "co-antenna",
            "X_{45}",
            "X_{58}",
            "co(E)",
            "co(X_{170})",
            "X_{18}",
            "co(X_{172})",
            "co(C_{6})",
            "X_{95}",
            "X_{171}",
            "X_{98}",
            "domino",
            "X_{5}",
            "R",
            "antenna",
            "E",
            "A",
            "co(X_{169})",
            "co(X_{58})",
            "co(X_{18})",
            "K_{3,3}-e",
            "co(X_{167})",
            "co-twin-house",
            "co(X_{166})",
            "twin-house",
            "co(X_{84})",
            "5-pan",
        ],
    )


@assign_class_id("gc_839")
@lru_cache(maxsize=None)
def is_gc_839(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2K_{3} + e, A, C_{5}, C_{6}, E, H, K_{3, 3}-e,
    P_{6}, R, S_{3}, X_{166}, X_{167}, X_{168}, X_{169}, X_{170}, X_{171},
    X_{172}, X_{18}, X_{45}, X_{5}, X_{58}, X_{84}, X_{95}, X_{96}, X_{98},
    co(A), co(C_{6}), co(E), co(H), co(P_{6}), co(R), co(X_{166}), co(X_{167}),
    co(X_{168}), co(X_{169}), co(X_{170}), co(X_{171}), co(X_{172}), co(X_{18}),
    co(X_{45}), co(X_{5}), co(X_{58}), co(X_{84}), co(X_{95}), co(X_{96}),
    co(X_{98}), antenna, co-antenna, co-cross, co-domino, co-fish, co-twin-
    house, cross, domino, fish, net, twin-house)-free.

    See https://www.graphclasses.org/classes/gc_839

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_h_free(
        graph,
        [
            "C_{5}",
            "X_{169}",
            "co(P_{6})",
            "X_{166}",
            "co-fish",
            "fish",
            "co(R)",
            "co(X_{171})",
            "2K_{3} + e",
            "X_{170}",
            "co(A)",
            "co-domino",
            "X_{167}",
            "co(X_{95})",
            "C_{6}",
            "P_{6}",
            "S_{3}",
            "X_{84}",
            "co(X_{96})",
            "co(X_{5})",
            "co-cross",
            "X_{168}",
            "X_{172}",
            "net",
            "co(X_{98})",
            "co(X_{45})",
            "co-antenna",
            "co(H)",
            "X_{45}",
            "X_{58}",
            "co(E)",
            "co(X_{170})",
            "X_{18}",
            "co(X_{172})",
            "co(C_{6})",
            "X_{95}",
            "X_{171}",
            "X_{98}",
            "domino",
            "X_{5}",
            "R",
            "antenna",
            "X_{96}",
            "E",
            "A",
            "H",
            "co(X_{169})",
            "co(X_{18})",
            "K_{3,3}-e",
            "co(X_{167})",
            "co(X_{58})",
            "co(X_{166})",
            "cross",
            "co-twin-house",
            "co(X_{84})",
            "twin-house",
            "co(X_{168})",
        ],
    )


@assign_class_id("gc_838")
@lru_cache(maxsize=None)
def is_p4_tidy(graph: nx.Graph) -> bool:
    """
    A partner of a P4 A in G is a vertex v in G-A such that A+v induces at least two P4s.
    A graph G is P4-tidy if any P4 has at most one partner.

    Self-complementary class.

    https://www.graphclasses.org/classes/gc_8.html

    @param graph:
    @return:
    """
    """
    V. Giakoumakis, F. Roussel, H. Thuillier
    On P4--tidy graphs
    Discrete Math. and Theor. Comp. Sci. 1 1997 17--41
    ZMath 0930.05073
    """
    # I'm using the fact that this class is equivalent to the class
    # https://www.graphclasses.org/classes/gc_838.html , as well as the
    # characterization provided by my xc_unpacker program, which tells me that
    # the union of the graphs covered by XZ_6 to XZ_14 (XZ_10 excluded) is:
    #
    # ['2K_{3} + e', '5-pan', 'A', 'C_{6}', 'E', 'H', 'P_{6}', 'X_{166}',
    #  'X_{169}', 'X_{170}', 'X_{171}', 'X_{172}', 'X_{18}', 'X_{37}',
    #  'X_{45}', 'X_{58}', 'X_{5}', 'X_{84}', 'X_{95}', 'X_{96}', 'antenna',
    #  'co(5-pan)', 'co(R)', 'co(X_{167})', 'co(X_{168})', 'co(X_{37})',
    #  'co(X_{5})', 'co(X_{98})', 'co-domino', 'co-fish', 'co-twin-C_{5}',
    #  'co-twin-house', 'cross', 'twin-C_{5}']
    #
    # so a graph is P_4-tidy iff it contains none of the above subgraphs, and
    # none of their complements either
    return is_h_free(
        graph,
        {  # the result of unpacking XZ_6 to XZ_14 excluding XZ_10
            "2K_{3} + e",
            "5-pan",
            "A",
            "C_{6}",
            "E",
            "H",
            "P_{6}",
            "X_{166}",
            "X_{169}",
            "X_{170}",
            "X_{171}",
            "X_{172}",
            "X_{18}",
            "X_{37}",
            "X_{45}",
            "X_{58}",
            "X_{5}",
            "X_{84}",
            "X_{95}",
            "X_{96}",
            "antenna",
            "co(5-pan)",
            "co(R)",
            "co(X_{167})",
            "co(X_{168})",
            "co(X_{37})",
            "co(X_{5})",
            "co(X_{98})",
            "co-domino",
            "co-fish",
            "co-twin-C_{5}",
            "co-twin-house",
            "cross",
            "twin-C_{5}",
        }.union(
            {  # the complements of the above subgraphs
                "K_{3,3}-e",
                "co(5-pan)",
                "co(A)",
                "co(C_{6})",
                "co(E)",
                "co(H)",
                "co(P_{6})",
                "co(X_{166})",
                "co(X_{169})",
                "co(X_{170})",
                "co(X_{171})",
                "co(X_{172})",
                "co(X_{18})",
                "co(X_{37})",
                "co(X_{45})",
                "co(X_{58})",
                "co(X_{5})",
                "co(X_{84})",
                "co(X_{95})",
                "co(X_{96})",
                "co-antenna",
                "5-pan",
                "R",
                "X_{167}",
                "X_{168}",
                "X_{37}",
                "X_{5}",
                "X_{98}",
                "domino",
                "fish",
                "twin-C_{5}",
                "twin-house",
                "co-cross",
                "co-twin-C_{5}",
            }
        ),
    )


@assign_class_id("gc_13")
@lru_cache(maxsize=None)
def is_c5_free_and_p4_tidy(graph: nx.Graph) -> bool:
    """
    Returns True if graph is C_{5}-free and P_{4}-tidy, False otherwise.

    Self-complementary class.

    https://www.graphclasses.org/classes/gc_13.html

    @param graph:
    @return:
    """
    return is_c5_free(graph) and is_p4_tidy(graph)


@assign_class_id("gc_961")
@lru_cache(maxsize=None)
def is_p4_tidy_and_balanced(graph: nx.Graph) -> bool:
    """
    https://www.graphclasses.org/classes/gc_958.html
    @param graph:
    @return:
    """
    # using equivalence with https://www.graphclasses.org/classes/gc_961.html
    return is_gc_960(graph) and is_p4_tidy(graph)


@assign_class_id("AUTO_3683")
@lru_cache(maxsize=None)
def is_auto_3683(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/AUTO_3683.html

    @param graph:
    @return:
    """
    return is_auto_1563(graph) and is_p4_tidy(graph)


@assign_class_id("gc_1372")
@lru_cache(maxsize=None)
def is_gc_1372(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (2P_3, C_4, C_5, P_5, X_170, co(A))-free.

    See https://www.graphclasses.org/classes/gc_1372

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """
    return is_h_free(graph, ["2P_{3}", "C_{4}", "C_{5}", "P_{5}", "X_{170}", "co(A)"])


@assign_class_id("AUTO_1930")
@lru_cache(maxsize=None)
def is_auto_1930(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is (co(2P_3), 2K_2, C_5, house, co(X_170), A)-free.

    See https://www.graphclasses.org/classes/AUTO_1930

    Complexity of naïve matching: O(n^6)
    :type graph: networkx.Graph
    """

    return is_2k2_free(graph) and is_h_free(
        graph, ["co(2P_{3})", "house", "C_{5}", "co(X_{170})", "A"]
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
