"""
Anthony Labarre © 2023-2026

Everything related to induced subgraph matching, carried out by instances of the SubgraphMatcher
class. Anyone needing to check whether a set of smallgraphs known to ISGCI appears in a graph can
simply use the function is_h_free, for instance as follows:

    is_h_free(my_graph, ["K_{3}", "P_{5}"])  # any iterable of strings is fine

The function returns True if none of the given subgraphs appear in my_graph, False otherwise.

Internals of the matching process
---------------------------------

The matching task itself is ultimately carried out by the Glasgow Subgraph Solver (GSS for short).
SubgraphMatcher provides a number of features designed to avoid carrying out the search at all
whenever possible; namely:

    - caching all results, so that we never search for the same subgraph in the same graph twice;
    - using properties of the pattern and the target to find contradictions: for instance, if the
        target is bipartite but the pattern is not, then the pattern cannot appear in the target,
        and therefore we do not even need to search for it. Only properties that can be computed
        quickly are used.
    - propagating the results of a search to the rest of the cache:
        - if a subgraph appears in the graph, then so do all its induced subgraphs: we mark them as
            "found" to avoid future searches
        - if a subgraph does not appear in the graph, then the larger patterns that contain it as
            an induced subgraph cannot appear in the graph either; we mark them as "missing" to
            avoid future searches

"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
import inspect
import logging
import os.path
import re
import shutil
import subprocess
from itertools import filterfalse
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from typing import Iterable, Set

# ----- Third-party imports -----------------------------------------------------------------------
import networkx as nx

from graph_recognition.adjacency_matrix import HalfAdjacencyMatrix
# ----- My imports --------------------------------------------------------------------------------
from graph_recognition.graph_formats import nx_graph_to_lad_file, lad_file_to_nx_graph, half_adj_mat_to_lad_file
from graph_recognition.misc_algo import degree_sequence, maximal_independent_set
from graph_recognition.recognizers_utils import cached_function
from graph_recognition.smallgraphs import (
    all_smallgraphs_by_order,
    smallgraph_inclusion_graph,
)

logger = logging.getLogger(__name__)
logging.basicConfig(filename="myapp.log")

# from https://stackoverflow.com/questions/3220284/how-to-customize-the-time-format-for-python-logging
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s")

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

# Cache selected imported functions ---------------------------------------------------------------
functions_to_cache = [
    nx.ancestors,
    nx.descendants,
]
for i, function in enumerate(functions_to_cache):
    functions_to_cache[i] = cached_function(function)

# Global variables --------------------------------------------------------------------------------
# a dictionary mapping graphs to SubgraphMatcher instances; since SubgraphMatcher.__init__ requires
# a graph as parameter, we cannot make __MATCHERS a defaultdict
__MATCHERS = dict()


# Classes -----------------------------------------------------------------------------------------
class SubgraphMatcher:
    """
    A SubgraphMatcher answers the question: "is graph G S-free?", where S is a set of graphs, and
    where S-freeness means that none of the graphs in S appear as induced subgraphs in G. This
    question is answered by the method no_match.

    The search itself is ultimately carried out by the Glasgow Subgraph Solver (GSS for short), but
    a number of techniques allow us to avoid running the search at all whenever possible. This is
    the role of the method find_induced.
    """
    _unknown_status = -1
    _truth_mapping = {"true": True, "false": False}  # for parsing the output of GSS
    # map smallgraph names to their order so we can search for them by increasing order
    smallgraph_names_and_orders = {
        graph[0]: k
        for k, graphbunch in all_smallgraphs_by_order().items()
        for graph in graphbunch
    }
    inclusion_graph = smallgraph_inclusion_graph()
    _temp_dir = TemporaryDirectory()

    # the following variables are only used for statistics
    number_of_calls_to_gss = 0
    number_of_calls_to_gcs = 0

    def __init__(self, graph: nx.Graph) -> None:
        """

        :param graph:
        @type graph: nx.Graph
        """
        self._graph = graph
        self._checked_subgraphs = dict.fromkeys(
            SubgraphMatcher.smallgraph_names_and_orders,
            self._unknown_status
        )

        # store target properties which will be useful to quickly rule out matches in
        # self.find_induced
        self._graph_max_degree = 0 if not self._graph else degree_sequence(self._graph)[0]
        self._graph_min_degree = 0 if not self._graph else degree_sequence(self._graph)[-1]

        # write graph to LAD file for further queries, so we translate it only once
        self._graph_lad_path = ""
        with NamedTemporaryFile(prefix=SubgraphMatcher._temp_dir.name + os.sep, delete=False) as output:
            self._graph_lad_path = output.name
            if isinstance(graph, nx.Graph):
                nx_graph_to_lad_file(graph, self._graph_lad_path)
            elif isinstance(graph, HalfAdjacencyMatrix):
                half_adj_mat_to_lad_file(graph, self._graph_lad_path)
            else:
                raise TypeError(f"cannot handle type {type(self._graph)}")

    def find_induced(self, smallgraph_name: str) -> bool:
        """
        Returns True if smallgraph is an induced subgraph of our target graph, False if it is not,
        and _unknown_status if checking was not possible.

        :param smallgraph_name:
        :return:
        """
        # trivial cases that don't even require loading the pattern graph
        if smallgraph_name == "K_{2}":
            return not self._graph.number_of_edges()

        path_to_pattern_lad = os.path.join(
            os.path.dirname(__file__), "smallgraphs", smallgraph_name
        )
        pattern = lad_file_to_nx_graph(path_to_pattern_lad)

        # *****************************************************************************************
        # * 1) try various tricks to avoid actually looking for induced subgraphs                 *
        # *****************************************************************************************

        # O(1) verifications ----------------------------------------------------------------------
        # if graph has fewer vertices or edges than pattern, then it cannot contain the pattern
        if self._graph.order() < pattern.order() or self._graph.size() < pattern.size():
            return False

        # if graph's max degree is smaller than pattern's, then it cannot contain the pattern
        if pattern.degree and degree_sequence(pattern)[0] > self._graph_max_degree:
            return False

        # O(m+n) verifications --------------------------------------------------------------------
        # looking for an independent set takes a long time; if we find a large
        # enough one, then we don't need to explicitly look for it
        if smallgraph_name[1:] == "K_{1}":
            mis_size = len(maximal_independent_set(self._graph, cutoff=7))
            if mis_size >= int(smallgraph_name[0]):
                # also update all larger sets; largest is 7
                for i in range(2, min(8, mis_size)):
                    self._checked_subgraphs[str(i) + "K_{1}"] = True
                return True

        if smallgraph_name == "triangle":
            smallgraph_name = "K_{3}"

        # looking for a clique takes a long time; if we find a large enough one, then we don't need
        # to explicitly look for it
        '''
        if smallgraph_name[:3] == "K_{" and smallgraph_name[4:] == "}":
            max_clique_size = nx.approximation.large_clique_size(self._graph)
            if max_clique_size >= int(smallgraph_name[3]):
                # also update all larger sets; largest is 7
                for i in range(2, min(8, max_clique_size)):
                    self._checked_subgraphs["K_{" + str(i) + "}"] = True
                return True
        '''
        # *****************************************************************************************
        # * 2) recurse on smaller patterns in the hope that they will provide                     *
        # *    answers without relying on the solver for current pattern                          *
        # *****************************************************************************************
        # if subgraph belongs to graph, then so do all its induced subgraphs; therefore, we first
        # recurse on all induced subgraphs sorted by increasing sizes; if any of them is missing,
        # then the pattern does not appear in the graph

        # """
        for subpattern in sorted(
                nx.descendants(SubgraphMatcher.inclusion_graph, smallgraph_name),
                key=SubgraphMatcher.smallgraph_names_and_orders.get
        ):
            if self._checked_subgraphs[subpattern] == self._unknown_status:
                self.set_and_propagate([subpattern], self.find_induced(subpattern))

            # WARNING: do NOT simplify the expression below: True and False are not the only
            # possible values
            # noinspection PySimplifyBooleanCheck
            if self._checked_subgraphs[subpattern] is False:
                return False
        # """

        # 2b) try profitable hereditary recognizers but only O(m+n) ones
        # NOTE: the same trick could be applied to more profitable recognizers, but at some point
        # we reach diminishing returns. Experimentally, so far, I've only been convinced by the
        # improved running times we obtain with linear time algorithms, which is why I'm not going
        # higher than that in complexity. Remember that the point of using ISGCI inclusion
        # relationships is to avoid running expensive algorithms, and we will lose that benefit at
        # some point if we lose sight of that.

        # I've been turning this on and off for a while and cannot decide whether to include it;
        # I'm giving up on it for now because for large graphs we spend ages in this part of the
        # code
        '''
        if any(
                recognizer(self._graph) and not recognizer(pattern)
                for recognizer in graph_recognition.profitable_hereditary_n.RECOGNIZERS.values()
        ):
            return False
        '''
        # *****************************************************************************************
        # * 3) if none of the above worked, call the solver                                       *
        # *****************************************************************************************
        # use the clique solver if the pattern is K_{?}
        use_clique_solver = smallgraph_name[:3] == "K_{" and smallgraph_name[4:] == "}"
        solver_name = "glasgow_clique_solver" if use_clique_solver else "glasgow_subgraph_solver"
        solver_path = _path_to_solver(solver_name)
        if use_clique_solver:
            glasgow_command = [
                solver_path,
                "--format",
                "lad",
                # "--no-nds",
                # "--no-supplementals",
                self._graph_lad_path,
                "--decide",
                smallgraph_name[3],
            ]

        else:  # use the general-purpose solver if pattern is not a clique
            glasgow_command = [
                solver_path,
                "--format",
                "lad",
                "--induced",
                # "--no-nds",
                # "--no-supplementals",
                path_to_pattern_lad,
                self._graph_lad_path,
            ]

        logger.info(
            f"Starting {solver_name} to find {smallgraph_name} (caller: "
            f"{inspect.getmodule(inspect.stack()[1][0]).__name__})"
        )
        output = subprocess.check_output(glasgow_command).decode()
        if use_clique_solver:
            SubgraphMatcher.number_of_calls_to_gcs += 1
        else:
            SubgraphMatcher.number_of_calls_to_gss += 1
        logger.info(f"{solver_name} finished successfully")
        return self._truth_mapping[re.findall("status = (false|true)", output)[0]]

    def no_match(self, subgraphs: Iterable[str]) -> bool:
        """
        Returns True iff none of the input subgraphs appear as induced subgraphs of the input
        graph.

        :param subgraphs: an iterable of strings
        :return:
        """
        # trivial but necessary check: we might receive an empty subgraph from a larger graph
        if not self._graph:
            return True

        # check for any unknown name
        missing_names = set(subgraphs).difference(SubgraphMatcher.smallgraph_names_and_orders)
        if missing_names:
            raise ValueError("names", missing_names, "are unknown")

        # if any of the subgraphs is known to appear in target, quit early
        if any(self._checked_subgraphs[graph] is True for graph in subgraphs):
            return False

        # discard already checked subgraphs and sort the rest by subgraph order
        sorted_subgraphs = sorted(
            {
                graph for graph in subgraphs
                if self._checked_subgraphs[graph] == self._unknown_status
            },
            key=SubgraphMatcher.smallgraph_names_and_orders.get,
        )

        for pattern in sorted_subgraphs:
            # print("[DEBUG] now checking", pattern)
            # none of the subgraphs have been checked initially, but this may change with repeated
            # runs, or even during a single run since unfound patterns will impact their ancestors
            if self._checked_subgraphs[pattern] == self._unknown_status:
                self.set_and_propagate([pattern], self.find_induced(pattern))

            # pattern found: quit early
            # WARNING: do NOT simplify the expression below: True and False are not the only
            # possible values
            # noinspection PySimplifyBooleanCheck
            if self._checked_subgraphs[pattern] is True:
                return False

        return True

    def set_and_propagate(self, pattern_bunch: Iterable[str], value: bool) -> None:
        """
        Records that a bunch of patterns appear (value=True) or do not appear (value=False) in the
        target, and propagates implications: if there is no match, then patterns that contain the
        given patterns as induced subgraph cannot appear in the target either. Likewise, if there
        is a match, then patterns that the given pattern contains as induced subgraphs also appear
        in the target.

        This method is mostly intended for external algorithms to communicate their findings to the
        matcher.

        @type value: bool
        @type pattern_bunch: iterable
        @param value:
        @param pattern_bunch:
        """
        other_patterns = [nx.ancestors, nx.descendants][value]
        for pattern in pattern_bunch:
            self._checked_subgraphs[pattern] = value
            if value != self._unknown_status:
                for other_class in other_patterns(SubgraphMatcher.inclusion_graph, pattern):
                    self._checked_subgraphs[other_class] = value

    def contained_subgraphs(self) -> Set[str]:
        """
        Returns the set of all subgraphs that have been found as induced subgraphs of the graph.
        This method only returns the subgraphs that have been queried, and does not perform any
        query itself.

        :return:
        """
        # WARNING: don't simplify using self._checked_subgraphs, that expression would accept
        # subgraphs with an unknown status, and we only want the ones that are "truly True"
        # (as opposed to "merely not False")
        return set(
            filter(
                lambda x: self._checked_subgraphs[x] is True, self._checked_subgraphs
            )
        )

    def _subgraphs_with_property_and_restriction(self, _property: str, restriction: str) -> Set[str]:
        """
        Returns the set of all subgraphs that satisfy:

            - known to occur (_property="matched") or not to occur (_property="missing") in the
                target graph;

            - being minimal or maximal with respect to induced subgraph inclusion
                (restriction="minimal" or restriction="maximal").

        """
        if _property not in {"matched", "missing"}:
            raise ValueError("property must be 'matched' or 'missing'")

        if restriction not in {"minimal", "maximal"}:
            raise ValueError("restriction must be 'maximal' or 'minimal'")

        # make sure every pattern has been checked
        for pattern in SubgraphMatcher.inclusion_graph:
            self.no_match([pattern])

        # set up the basis (all matched or all missing subgraphs)
        if _property == "matched":
            basis = self.contained_subgraphs()
        else:
            basis = self.missing_subgraphs()

        # discard subgraphs with more vertices than graph
        basis = {
            subgraph
            for subgraph in basis
            if SubgraphMatcher.smallgraph_names_and_orders[subgraph] <= self._graph.order()
        }

        graph_relation = {"maximal": nx.ancestors, "minimal": nx.descendants}[restriction]

        # only record subgraphs whose descendants in the inclusion graph do not appear in the
        # target
        return {
            subgraph
            for subgraph in basis
            if all(
                other not in basis
                for other in graph_relation(SubgraphMatcher.inclusion_graph, subgraph)
            )
               and SubgraphMatcher.smallgraph_names_and_orders[subgraph] <= self._graph.order()
        }

    def minimal_missed_subgraphs(self) -> Set[str]:
        """
        Returns the set of all minimal subgraphs that are known not to occur as induced subgraphs
        of the graph. A subgraph H is a minimal miss in the target graph if no induced subgraph of
        H is missing from the target.

        In practice, one will probably be more interested in minimal missed subgraphs than maximal
        missed subgraphs, since the latter set is likely to be much larger than the former.

        :return:
        """
        return self._subgraphs_with_property_and_restriction("missing", "minimal")

    def missing_subgraphs(self) -> Set[str]:
        """
        Returns the set of all subgraphs that are known not to occur as induced subgraphs of the
        graph. This method only returns the subgraphs that have been queried, and does not perform
        any query itself.

        :return:
        """
        return set(filterfalse(self._checked_subgraphs.get, self._checked_subgraphs))

    def get_status(self, subgraph: str) -> int:
        """
        Returns the status of the subgraph with respect to the target graph: unknown (-1), known to
        appear (True), or known not to appear (False). Does not perform any search.

        :param subgraph:
        :return:
        """
        return self._checked_subgraphs[subgraph]


# Functions ---------------------------------------------------------------------------------------
# ----- Private functions -------------------------------------------------------------------------
def _dispatch_findings(graph: nx.Graph, subgraphs: Iterable[str], value: bool) -> None:
    """
    Records that all the given subgraphs appear as induced subgraphs of the given graph
    (value=True), or that none of them do (value=False).

    @param graph:
    @param subgraphs:
    @param value:
    @return:
    """
    if graph not in __MATCHERS:
        __MATCHERS[graph] = SubgraphMatcher(graph)

    __MATCHERS[graph].set_and_propagate(subgraphs, value)


def _path_to_solver(name: str) -> str:
    """
    Resolve solver binary location.

    Priority:
    1. System PATH (recommended)
    2. ~/.local/bin (default install location)
    """

    # 1) PATH (best case)
    system_path = shutil.which(name)
    if system_path:
        return system_path

    # 2) ~/.local/bin fallback
    local_bin = Path.home() / ".local" / "bin" / name
    if local_bin.exists() and os.access(local_bin, os.X_OK):
        return str(local_bin)

    # 3) failure
    raise FileNotFoundError(
        f"{name} not found.\nPlease install it using install_gss.sh or ensure it is in your PATH."
    )


# ----- Public functions --------------------------------------------------------------------------
def is_h_free(graph: nx.Graph, subgraphs: Iterable[str]) -> bool:
    """
    Returns True iff none of the input subgraphs appear as induced subgraphs of the input graph.

    :param graph:
    :param subgraphs:
    :return:
    """
    if graph not in __MATCHERS:
        __MATCHERS[graph] = SubgraphMatcher(graph)

    return __MATCHERS[graph].no_match(subgraphs)


def clear_subgraph_cache(graph: nx.Graph) -> None:
    """
    Clears the subgraphs cache for a given graph.

    :param graph:
    :return:
    """
    # note: this function normally belongs in cache_utils, but I want to keep __MATCHERS private so
    # it will remain here
    if graph in __MATCHERS:  # mandatory check: we may not have called is_h_free at all
        del __MATCHERS[graph]


def query_status(graph: nx.Graph, subgraph: str) -> int:
    """
    Returns the status of subgraph in graph: unknown (-1), known to appear (True), or known not to
    appear (False). Does not perform any search.

    :param graph:
    :param subgraph:
    :return:
    """
    if graph not in __MATCHERS:
        return SubgraphMatcher._unknown_status

    return __MATCHERS[graph].get_status(subgraph)
