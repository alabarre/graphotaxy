"""
Anthony Labarre © 2023-2025

Everything related to induced subgraph matching, carried out by instances of the SubgraphMatcher
class.

The matching task itself is ultimately carried out by the Glasgow Subgraph Solver (GSS for short).
SubgraphMatcher provides a number of features designed to avoid carrying out the search at all
whenever possible; namely:

    - caching all results, so that we never search for the same subgraph in the same graph twice;

    - using properties of the pattern and the target to find contradictions: for instance, if the
        target is bipartite but the pattern is not, then the pattern cannot appear in the target,
        and therefore we do not even need to search for it. Only properties that can be computed
        quickly are interesting in that regard.

    - propagating the results of a search to the rest of the cache:
        - if a subgraph appears in the graph, then so do all its induced subgraphs: we mark them as
            found to avoid future searches

        - if a subgraph does not appear in the graph, then the larger patterns that contain it as
            an induced subgraph cannot appear in the graph either; we mark them as missing to avoid
            future searches

"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
import logging
import os.path
import re
import subprocess
from tempfile import NamedTemporaryFile, TemporaryDirectory
from typing import Iterable

# ----- Third-party imports -----------------------------------------------------------------------
import networkx as nx

# ----- My imports --------------------------------------------------------------------------------
from graph_recognition.graph_formats import nx_graph_to_lad_file, lad_file_to_nx_graph
from graph_recognition.misc_algo import degree_sequence
from graph_recognition.recognizers_utils import cached_function
from graph_recognition.smallgraphs import (
    all_smallgraphs_by_order,
    smallgraph_inclusion_graph,
)

logger = logging.getLogger(__name__)

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

# the following data structure maps smallgraph names to their order
SMALLGRAPH_NAMES_AND_ORDERS = {
    # graph.name: k for k, graphbunch in all_smallgraphs_by_order().items()
    graph[0]: k
    for k, graphbunch in all_smallgraphs_by_order().items()
    for graph in graphbunch
}
SMALLGRAPH_INCLUSION_GRAPH = smallgraph_inclusion_graph()
_TEMP_DIR = TemporaryDirectory()


# Classes -----------------------------------------------------------------------------------------
class SubgraphMatcher:
    """
    A SubgraphMatcher answers the question: "is graph G S-free?", where S is a set of graphs, and
    where S-freeness means that none of the graphs in S appear as induced subgraphs in G. This
    question is answered by the method no_match.

    The search itself is ultimately carried out by the Glasgow Subgraph Solver (GSS for short), but
    number of techniques allow us to avoid running the search at all whenever possible. This is the
    role of the method find_induced.
    """
    _unknown_status = -1
    truth_mapping = {"true": True, "false": False}  # for parsing the output of GSS
    number_of_calls_to_gss = 0
    number_of_calls_to_gcs = 0

    def __init__(self, graph: nx.Graph) -> None:
        """

        :param graph:
        @type graph: nx.Graph
        """
        self._graph = graph
        self._checked_subgraphs = dict.fromkeys(
            SMALLGRAPH_NAMES_AND_ORDERS, self._unknown_status
        )

        # store target properties which will be useful to quickly rule out matches in
        # self.find_induced
        self._graph_max_degree = (
            0 if nx.is_empty(self._graph) else degree_sequence(self._graph)[0]
        )
        self._graph_min_degree = (
            0 if nx.is_empty(self._graph) else degree_sequence(self._graph)[-1]
        )

        # write graph to LAD files for further queries, so we translate it only once
        self._graph_lad_path = ""
        with NamedTemporaryFile(prefix=_TEMP_DIR.name + os.sep, delete=False) as output:
            self._graph_lad_path = output.name
            # print("[DEBUG] writing graph to lad file ... ", end="")
            nx_graph_to_lad_file(graph, self._graph_lad_path)
            # print("done.")

    def find_induced(self, smallgraph_name: str) -> bool:
        """
        Returns True if smallgraph is an induced subgraph of our target graph, False if it is not,
        and _unknown_status if checking was not possible.

        :param smallgraph_name:
        :return:
        """
        # print("\n[DEBUG] now searching for", smallgraph_name)
        # *****************************************************************************************
        # * 1) try various tricks to avoid actually looking for induced subgraphs                 *
        # *****************************************************************************************
        path_to_pattern_lad = os.path.join(
            os.path.dirname(__file__), "smallgraphs", smallgraph_name
        )
        pattern = lad_file_to_nx_graph(path_to_pattern_lad)

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
            # print("now checking", smallgraph_name)  # DEBUG
            mis_size = len(nx.maximal_independent_set(self._graph))
            if mis_size >= int(smallgraph_name[0]):
                # also update all larger sets; largest is 7
                for i in range(2, min(8, mis_size)):
                    self._checked_subgraphs[str(i) + "K_{1}"] = True
                return True

        if smallgraph_name == "triangle":
            smallgraph_name = "K_{3}"

        # looking for a clique takes a long time; if we find a large enough one, then we don't need
        # to explicitly look for it
        # TODO why is this commented?
        """
        if smallgraph_name[:3] == "K_{" and smallgraph_name[4:] == "}":
            # print("[DEBUG] now looking for a large clique")
            # max_clique_size = len(nx.approximation.max_clique(self._graph))  # TODO slow
            max_clique_size = nx.approximation.large_clique_size(
                self._graph
            )  # TODO bad results
            if max_clique_size >= int(smallgraph_name[3]):
                # also update all larger sets; largest is 7
                for i in range(2, min(8, max_clique_size)):
                    self._checked_subgraphs["K_{" + str(i) + "}"] = True
                return True
            # print("max clique size:", max_clique_size)
        """
        # restore old name if changed
        # if smallgraph_name == "K_3":
        #     smallgraph_name = "triangle"

        # *****************************************************************************************
        # * 2) recurse on smaller patterns in the hope that they will provide                     *
        # *    answers without relying on the solver for current pattern                          *
        # *****************************************************************************************
        # if subgraph belongs to graph, then so do all its induced subgraphs; therefore, we first
        # recurse on all induced subgraphs sorted by increasing sizes; if any of them is missing,
        # then the pattern does not appear in the graph
        # NOTE: nice idea, but I'm not sure it has any impact in practice.
        """
        for subpattern in sorted(
            nx.descendants(SMALLGRAPH_INCLUSION_GRAPH, smallgraph_name),
            key=SMALLGRAPH_NAMES_AND_ORDERS.get
        ):
            # print("    descendant", subpattern)
            if self._checked_subgraphs[subpattern] == self._unknown_status:
                self.set_and_propagate(
                    [subpattern], self.find_induced(subpattern)
                )

            if self._checked_subgraphs[subpattern] is False:
                return False
        # """
        # NOTE: I'm giving up on the following trick: computing the girth in
        # practice will take much longer for large graphs than simply searching
        # for the pattern
        # if target's shortest cycle is longer than pattern's, then pattern
        # cannot occur in target
        # if girth(self._graph) > girth(pattern):
        #    return False

        # *****************************************************************************************
        # * 3) if none of the above worked, call the solver                                       *
        # *****************************************************************************************
        # print("[DEBUG] saving graph_lad before crash")
        # shutil.copy(self._graph_lad_path, "/tmp/lastgraph.lad.BAK")  # DEBUG
        # print("\nno way around it: using glasgow for\n", smallgraph_name)

        # use the clique solver instead if the pattern is K_{?}
        if smallgraph_name[:3] == "K_{" and smallgraph_name[4:] == "}":
            glasgow_command = [
                os.path.join(os.path.dirname(__file__), "./glasgow_clique_solver"),
                "--format",
                "lad",
                # "--no-nds",
                # "--no-supplementals",
                self._graph_lad_path,
                "--decide",
                smallgraph_name[3],
            ]
            logger.info("Starting GCS to find %s", smallgraph_name)
            output = subprocess.check_output(glasgow_command).decode()
            SubgraphMatcher.number_of_calls_to_gcs += 1
            logger.info("GCS finished successfully")
            return self.truth_mapping[re.findall("status = (false|true)", output)[0]]

        else:
            # this is the command for the glasgow subgraph solver
            glasgow_command = [
                os.path.join(os.path.dirname(__file__), "./glasgow_subgraph_solver"),
                "--format",
                "lad",
                "--induced",
                # "--no-nds",
                # "--no-supplementals",
                path_to_pattern_lad,
                self._graph_lad_path,
            ]
            logger.info("Starting GSS to find %s", smallgraph_name)
            output = subprocess.check_output(glasgow_command).decode()
            SubgraphMatcher.number_of_calls_to_gss += 1
            logger.info("GSS finished successfully")
            return self.truth_mapping[re.findall("status = (false|true)", output)[0]]

    def no_match(self, subgraphs: Iterable[str]) -> bool:
        """Returns True iff none of the input subgraphs appear as induced subgraphs of the input
        graph.

        :param subgraphs: an iterable of strings
        :return:
        """
        # print(
        #     "[DEBUG] checked subgraphs states (before doing anything):",
        #     [(pat, self._checked_subgraphs[pat]) for pat in subgraphs]
        # )
        # trivial condition, but sometimes we receive graphs which may be empty since we might run
        # the method on subgraphs of a larger graph
        if not self._graph:
            return True

        # check for any unknown name
        missing_names = set(subgraphs).difference(SMALLGRAPH_NAMES_AND_ORDERS)
        if missing_names:
            raise ValueError("names", missing_names, "are unknown")

        # if any of the subgraphs is known to appear in target, quit early
        if any(self._checked_subgraphs[graph] is True for graph in subgraphs):
            return False

        # discard already checked subgraphs and sort the rest by subgraph order
        sorted_subgraphs = sorted(
            {
                graph
                for graph in subgraphs
                if self._checked_subgraphs[graph] == self._unknown_status
            },
            key=SMALLGRAPH_NAMES_AND_ORDERS.get,
        )

        # print("[DEBUG] started with", subgraphs, ", kept", sorted_subgraphs)

        for pattern in sorted_subgraphs:
            # print("[DEBUG] now looking for", pattern)
            # none of the subgraphs have been checked initially, but this may change with repeated
            # runs, or even during a single run since unfound patterns will impact their ancestors
            if self._checked_subgraphs[pattern] == self._unknown_status:
                self.set_and_propagate([pattern], self.find_induced(pattern))

            # pattern found: quit early
            # do NOT simplify the expression below: True and False are not the only
            # possible values
            if self._checked_subgraphs[pattern] is True:
                return False

        return True

    def set_and_propagate(self, pattern_bunch: Iterable[str], value: bool) -> None:
        """Records that a bunch of patterns appear (value=True) or do not appear (value=False) in
        the target, and propagates implications: if there is no match, then patterns that contain
        the given patterns as induced subgraph cannot appear in the target either. Likewise, if
        there is a match, then patterns that the given pattern contains as induced subgraphs also
        appear in the target.

        This method is mostly intended for external algorithms to communicate their findings to the
        matcher.

        @type value: bool
        @type pattern_bunch: iterable
        @param value:
        @param pattern_bunch:
        """
        # print("\nsetting value to", value, "for the following patterns")  # DEBUG
        other_patterns = [nx.ancestors, nx.descendants][value]
        for pattern in pattern_bunch:
            # print("    ", pattern)
            self._checked_subgraphs[pattern] = value
            if value != self._unknown_status:
                for other_class in other_patterns(SMALLGRAPH_INCLUSION_GRAPH, pattern):
                    self._checked_subgraphs[other_class] = value

    def contained_subgraphs(self) -> set[str]:
        """Returns the set of all subgraphs that have been found as induced subgraphs of the graph.
        This method only returns the subgraphs that have been queried, and does not perform any
        query itself.

        :return:
        """
        return set(
            filter(
                lambda x: self._checked_subgraphs[x] is True, self._checked_subgraphs
            )
        )

    def _subgraphs_with_property_and_restriction(
        self, _property: str, restriction: str
    ) -> set[str]:
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
        for pattern in SMALLGRAPH_INCLUSION_GRAPH:
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
            if SMALLGRAPH_NAMES_AND_ORDERS[subgraph] <= self._graph.order()
        }

        graph_relation = {"maximal": nx.ancestors, "minimal": nx.descendants}[
            restriction
        ]

        # only record subgraphs whose descendants in the inclusion graph do not appear in the
        # target
        return {
            subgraph
            for subgraph in basis
            if all(
                other not in basis
                for other in graph_relation(SMALLGRAPH_INCLUSION_GRAPH, subgraph)
            )
            and SMALLGRAPH_NAMES_AND_ORDERS[subgraph] <= self._graph.order()
        }

    def minimal_missed_subgraphs(self) -> set[str]:
        """
        Returns the set of all minimal subgraphs that are known not to occur as induced subgraphs
        of the graph. A subgraph H is a minimal miss in the target graph if no induced subgraph of
        H is missing from the target.

        In practice, one will probably be more interested in minimal missed subgraphs than maximal
        missed subgraphs, since the latter set is likely to be much larger than the former.

        :return:
        """
        return self._subgraphs_with_property_and_restriction("missing", "minimal")

    def missing_subgraphs(self) -> set[str]:
        """
        Returns the set of all subgraphs that are known not to occur as induced subgraphs of the
        graph. This method only returns the subgraphs that have been queried, and does not perform
        any query itself.

        :return:
        """
        return set(
            filter(
                lambda x: self._checked_subgraphs[x] is False, self._checked_subgraphs
            )
        )


# Functions ---------------------------------------------------------------------------------------
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
