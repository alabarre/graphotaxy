"""
Anthony Labarre © 2025-2026

O(n^8) algorithms.

"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
import os
from functools import lru_cache
from itertools import combinations

# ----- Third-party imports -----------------------------------------------------------------------
import networkx as nx

# ----- My imports --------------------------------------------------------------------------------
from graph_recognition.profitable_hereditary_n import (
    is_chordal,
)
from graph_recognition.recognizers_utils import (
    assign_class_id,
    current_module_recognizers, assign_fisc,
)
from graph_recognition.subgraphs import is_h_free
from graph_recognition.undirected_graph import UndirectedGraph


# Recognizers -------------------------------------------------------------------------------------


@assign_fisc([
    "co(C_{5})",
    "co(C_{6})",
    "co(C_{7})",
    "co(C_{8})",
    "domino",
    "C_{7}",
    "C_{8}",
])  # partial fisc also used in the code of the function
@assign_class_id("gc_352")
@lru_cache(maxsize=None)
def is_wing_triangulated(graph: nx.Graph) -> bool:
    """
    For a graph G the graph W(G) having all edges of G as its vertices, two edges of G being
    adjacent in W(G) if they are the non-incident edges (called wings) of an induced path on four
    vertices in G, is called the wing-graph of G. A graph G is wing-triangulated if W(G) is
    triangulated.

    https://www.graphclasses.org/classes/gc_352

    @param graph:
    @return:
    """
    # see https://doi.org/10.1002/(SICI)1097-0118(199701)24:1%3C25::AID-JGT4%3E3.0.CO;2-L ,
    # observation 1:
    # wing-triangulated graphs are C_k free for all k >= 7; domino-free; and co(C_k)-free for all
    # k >= 5; we are only testing the smallgraphs we already have
    if not is_h_free(
            graph,
            [
                "co(C_{5})",
                "co(C_{6})",
                "co(C_{7})",
                "co(C_{8})",
                "domino",
                "C_{7}",
                "C_{8}",
            ],
    ):
        return False

    # build the wing-graph; no need to add all edges as nodes since we only build the graph to
    # check that it is chordal, so only nodes that belong to an edge need to be considered
    wing_graph = UndirectedGraph()

    # connect each pair of nodes in wing_graph that corresponds to edges in the graph that satisfy
    # both conditions; we can actually just check that they are disjoint and induce a P_4
    for e, f in combinations(graph.edges(), 2):
        endpoints = set(e + f)
        # if set has 4 elements, then e and f are independent, so checking whether they induce a
        # P_{4} is equivalent to checking that the subgraph has exactly 3 edges
        if len(endpoints) == 4 and sum(graph.has_edge(x, y) for x, y in combinations(endpoints, 2)) == 3:
            wing_graph.add_edge(e, f)

    # check wing_graph's chordality (preemptively return True for empty graphs, as nx.is_chordal
    # crashes on those)
    return not wing_graph or is_chordal(wing_graph, internal_type=set)


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
