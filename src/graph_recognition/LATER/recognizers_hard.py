"""
Anthony Labarre © 2023

Recognizers for those classes that are NP-hard to recognize. The actual work is
carried out by specialized solvers.

Some words on those problems.

Computing treewidth is NP-hard in general, but the only relevant classes in
ISGCI so far have 2 <= treewidth <= 5.

I hope that either best_lower_bound_on_treewidth returns a value large enough to
avoid running the solver at all, or that the treewidth is indeed at most 5 and
that the solver will find out quickly.

TODO much later: use our knowledge of graph classification to run specialized, more efficient algorithms

"""
# Imports ----------------------------------------------------------------------
# ----- Standard imports -------------------------------------------------------
from functools import lru_cache
import math
import os
import re
import statistics
import subprocess
from inspect import isgeneratorfunction
from tempfile import NamedTemporaryFile

from CubicHam import HamiltonianCycles
from graph_recognition.graph_formats import nx_graph_to_gr_file
import networkx as nx

from graph_recognition.misc_algo import degree_sequence
from graph_recognition.profitable_hereditary_n import is_planar, is_cubic
from graph_recognition.recognizers_utils import (
    assign_class_id,
    current_module_recognizers,
)

# Cache imported functions that are not already cached ------------------------
# TODO for each of these classes, check whether we can do something useful in
#  addition to caching (bounds, etc.)
for function in (
    nx.is_biconnected,
    nx.girth,
):
    # WARNING: the following condition doesn't identify functions that return
    # a generator object (e.g. return (x for x in stuff)).
    if isgeneratorfunction(function):
        raise TypeError(
            function.__name__ + " is a generator function, decorating it with "
            "lru_cache will cause bugs"
        )

    # check whether function has already been lru_cached
    if not hasattr(function, "cache_info"):
        setattr(nx, function.__name__, lru_cache(maxsize=None)(function))


# Functions --------------------------------------------------------------------
def which(program):
    """Returns True if and only if program exists in system path."""

    # (stackoverflow.com/questions/377017/test-if-executable-exists-in-python)
    def is_exe(file_path):
        """Checks that fpath exists and is executable."""
        return os.path.isfile(file_path) and os.access(file_path, os.X_OK)

    fpath = os.path.split(program)[0]
    if fpath and is_exe(program):
        return True

    for path in os.environ["PATH"].split(os.pathsep):
        if is_exe(os.path.join(path, program)):
            return True

    return False


# ----- Lower bounds on treewidth ----------------------------------------------
@lru_cache(maxsize=None)
def average_degree(graph):
    """
    Returns the average degree of the graph.

    :param graph:
    :return:
    """
    return statistics.mean(degree_sequence(graph))


@lru_cache(maxsize=None)
def treewidth(graph):
    """Returns the treewidth of the graph.

    :param graph:
    :return:
    """
    # easy cases
    if nx.is_chordal(graph):
        return nx.chordal_graph_treewidth(graph)

    # NOTE: this is way too slow for my purposes;
    # TODO maybe there's a way to interrupt the solver if lower bound is too high? or to avoid launching it altogether?
    # TODO read this re lower bounds: https://www.sciencedirect.com/science/article/pii/S0890540111000836
    # write graph to GR file for the solver
    with NamedTemporaryFile(delete=False) as graph_gr:
        nx_graph_to_gr_file(graph, graph_gr.name)
        output = subprocess.check_output(
            "../../tw-exact", stdin=graph_gr, stderr=subprocess.STDOUT
        ).decode()
        return int(re.findall("c width = (\d+)", output)[0])


@lru_cache(maxsize=None)
def best_lower_bound_on_treewidth(graph):
    """
    returns the max of all lower bounds on tw(graph)
    :type graph: nx.Graph
    :param graph:
    :return:
    """
    lower_bounds = list()
    # Corollary 6 in https://www.sciencedirect.com/science/article/pii/S0890540111000836
    n = graph.number_of_nodes()
    gamma_r = n - 1
    if graph.size() < (n * (n - 1)) // 2:
        gamma_r = min(
            max(graph.degree(u), graph.degree(v)) for u, v in nx.non_edges(graph)
        )

    lower_bounds.append(gamma_r)
    # Theorem 7 in https://www.sciencedirect.com/science/article/pii/S0890540111000836
    av_deg = average_degree(graph)
    lower_bounds.append(av_deg // 2)
    # Theorem 7 in https://www.sciencedirect.com/science/article/pii/S0890540111000836
    g = nx.girth(graph)
    lower_bounds.append(((av_deg - 1) ** ((g - 1) // 2)) / (4 * math.e * (g + 1)) - 2)

    return max(lower_bounds)


@assign_class_id("gc_899")
@lru_cache(maxsize=None)
def is_treewidth_2(graph):
    if best_lower_bound_on_treewidth(graph) > 2:
        return False

    return treewidth(graph) == 2


@assign_class_id("gc_900")
@lru_cache(maxsize=None)
def is_treewidth_3(graph):
    if best_lower_bound_on_treewidth(graph) > 3:
        return False

    return treewidth(graph) == 3


@assign_class_id("gc_901")
@lru_cache(maxsize=None)
def is_treewidth_4(graph):
    if best_lower_bound_on_treewidth(graph) > 4:
        return False

    return treewidth(graph) == 4


@assign_class_id("gc_902")
@lru_cache(maxsize=None)
def is_treewidth_5(graph):
    if best_lower_bound_on_treewidth(graph) > 5:
        return False

    return treewidth(graph) == 5


@assign_class_id("gc_749")
@lru_cache(maxsize=None)
def is_maximal_clique_irreducible(graph):
    """
    A graph G is maximal clique irreducible if every maximal clique in G
    contains an edge that is not contained in any other maximal clique.

    TODO this is not an exponential time algorithm, so move it where appropriate once complexity is known
        well, it's not clear that even if the number of cliques is polynomial,
        the algorithm will run in polynomial time. See page on bron kerbosch algo.

        "it's complicated": see https://www.sciencedirect.com/science/article/abs/pii/S0304397521006538

    quoting isgci https://www.graphclasses.org/classes/refs1600.html#ref_1642

    By definition, a graph G is maximal clique irreducible if every maximal
    clique in G contains an edge that is not contained in any other maximal
    clique. Then, the number of maximal cliques is bounded by m, the number of
    edges. Thus, the maximal cliques can be obtained in polynomial time (with
    any algorithm that lists the cliques one by one). This solves the clique
    and weight clique problems. For the recognition problem, observe that you
    can return NO if more than m maximal cliques are found by the enumeration
    algorithm. Otherwise, we just check that every maximal clique has an edge
    not contained in other maximal cliques.

    :param graph:
    :return:
    """
    # go through all maximal cliques
    m = graph.size()
    all_max_cliques = []
    for i, max_clique in enumerate(nx.find_cliques(graph)):
        # too many cliques -> abort
        if i > m:
            return False
        all_max_cliques.append(graph.subgraph(max_clique))

    # check that no edge belongs to more than one maximal clique
    # this is O(m^2), since we check all m edges and there are at most m
    # cliques; each check is performed in O(1)
    for u, v in graph.edges:
        num_occ = 0
        for max_clique in all_max_cliques:
            num_occ += max_clique.has_edge(u, v)
            if num_occ > 1:
                return False

    return True


@assign_class_id("gc_1316")
@lru_cache(maxsize=None)
def is_cubic_and_hamiltonian(graph):
    """

    https://www.graphclasses.org/classes/gc_1316.html

    @param graph:
    @return:
    """
    if is_cubic(graph):
        for _ in HamiltonianCycles(graph):
            return True

    return False


@assign_class_id("gc_1319")
@lru_cache(maxsize=None)
def is_cubic_and_hamiltonian_and_planar(graph):
    """

    https://www.graphclasses.org/classes/gc_1319.html

    @param graph:
    @return:
    """
    if is_cubic(graph) and is_planar(graph):
        for _ in HamiltonianCycles(graph):
            return True

    return False


# not ready yet
@lru_cache(maxsize=None)
def is_hamiltonian(graph):
    """

    @param graph:
    @return:
    """
    if not nx.is_biconnected(graph):
        return False

    # TODO work in progress; this will use a SAT solver

    # TODO or just use this: https://github.com/lutzthies/HCPtoSAT

    if not which("minisat"):
        print(
            "Error: could not find minisat, I won't be able to tell you "
            "whether your graph is Hamiltonian"
        )
        return

    # TODO write model file
    # TODO run solver
    # TODO convert and return answer


# Variables --------------------------------------------------------------------
"""
RECOGNIZERS = {
    "gc_899": is_treewidth_2,  # complement unknown
    "gc_900": is_treewidth_3,  # complement unknown
    "gc_901": is_treewidth_4,  # complement unknown
    "gc_902": is_treewidth_5,  # complement unknown
    "gc_749": is_maximal_clique_irreducible,  # complement unknown
    "gc_1316": is_cubic_and_hamiltonian,  # no info on complement
    "gc_1319": is_cubic_and_hamiltonian_and_planar,  # no info on complement
}
"""

# This code segment must always be at the END of a recognizer file ------------
RECOGNIZERS = current_module_recognizers(
    ".".join(
        [
            os.path.basename(os.path.dirname(__file__)),
            os.path.basename(__file__).strip(".py"),
        ]
    )
)
# -----------------------------------------------------------------------------
