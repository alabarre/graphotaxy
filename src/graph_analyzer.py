"""
Anthony Labarre © 2023-2026

Implementation of a GraphAnalyzer class. The purpose of an instance of this class is to produce
classifications for one or more undirected graphs.

To use a GraphAnalyzer:

    analyzer = GraphAnalyzer()                         # instantiate it
    # possibly set options through method calls, see class definition below
    analyzer.run_classification(paths_to_input_files)  # feed it data and go
    analyzer.print_summary_of_findings()               # print results

"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
import subprocess
import sys
import urllib
from collections import defaultdict
from collections.abc import Callable
from copy import deepcopy
from importlib import import_module
from itertools import chain
from typing import Iterable, Set, List

# ----- Third-party imports -----------------------------------------------------------------------
import networkx as nx
from tqdm import tqdm

# ----- My imports --------------------------------------------------------------------------------
from classification_digraph import ClassificationDigraph
from graph_recognition import misc_algo
from graph_recognition.subgraphs import SubgraphMatcher, _dispatch_findings, clear_subgraph_cache
from isgci.isgci_base import (
    isgci_equivalences,
    BASE_CLASS_URL,
    reduced_isgci_inclusion_graph,
    isgci_ids_to_names,
    isgci_exclusion_graph, isgci_recognition_statuses, isgci_version_info,
)
from readwrite import process_graphs, number_of_graphs_in_file
from undirected_graph import UndirectedGraph


# Functions ---------------------------------------------------------------------------------------
# TODO refactor: this has nothing to do with analyzing, should I have a "printing" module?
def underlined(message: str) -> str:
    """
    Returns an underlined version of a message.

    >>> print(underlined("Hello!"))
    Hello!
    ------

    :param message: any text
    :return: the input text, underlined
    """
    return "\n".join([message, len(message) * "-"])


# TODO refactor: this has nothing to do with analyzing
def _clear_other_caches(functions: Iterable[Callable]) -> None:
    """
    Clears the caches of all provided functions. Only functions decorated with lru_cache are
    allowed.

    :param functions: the functions whose cache must be cleared
    :return: nothing
    """
    for func in functions:
        try:
            func.cache_clear()
        except AttributeError:
            print(f"failed to clear cache for function {func.__name__} from {func.__module__}")
            # all provided functions are supposed to be cached, so we exit if something went wrong
            # to signal it has to be fixed
            exit(-1)


# Classes -----------------------------------------------------------------------------------------
class GraphAnalyzer:
    """
    The class responsible for identifying graphs based on their graph class.

    A GraphAnalyzer first loads a set of graphs from a given file into a list, so that each graph
    has a corresponding index. Graph recognition tasks should be carried out first, so that other
    methods can benefit from the acquired knowledge by running algorithms optimized for a given
    graph class (e.g. it is worth knowing that a graph is a permutation graph if we are interested
    in deciding whether two graphs are isomorphic).
    """

    def __init__(self) -> None:
        """
        Initializes all data structures.
        """
        # data related to a modified behavior GraphAnalyzer ---------------------------------------
        self.blacklisted = set()

        # data related to classification ----------------------------------------------------------
        self.enumeration_of_positive_classes = defaultdict(int)
        self.isgci_graph = ClassificationDigraph()
        self.isgci_exclusion_graph = isgci_exclusion_graph()
        self.max_unknown_classes = 0
        self.min_unknown_classes = sys.maxsize
        self.num_graphs = 0
        self.prototype_classification_digraph = ClassificationDigraph()
        self.relevant_classes = set()
        self.tc_isgci = nx.transitive_closure_dag(deepcopy(self.isgci_graph))
        self.unknown_nodes = set(self.isgci_graph.nodes)

        # data related to analysis statistics -----------------------------------------------------
        self.discarded_due_to_exclusion = 0
        self.discarded_due_to_propagation = 0
        self.gss_crashed = False
        self.hits_and_misses = {"hits": 0, "misses": 0}
        self.recognizers_that_were_run = set()

        # other useful data -----------------------------------------------------------------------
        self.equivalences = isgci_equivalences()
        self.recognizers = []
        self.setup_recognizers()

    def register_recognizer(self, class_id: str, recognizer: Callable) -> None:
        """
        Adds a recognizer to the list of recognizers to use for the given class as well as all
        equivalent classes.

        :param class_id:
        :param recognizer:
        :return:
        """
        self.recognizers.append((class_id, recognizer))
        self.recognizers.extend((eq_id, recognizer) for _, eq_id in self.equivalences[class_id])

    def setup_recognizers(self) -> None:
        """
        Registers all recognizers that will be used.

        :return:
        """
        # build the list of modules from which recognizers should be retrieved

        # 1) profitable classes, i.e. classes that have a FISC but can be recognized faster than by
        #    using a naïve algorithm
        modules = ["profitable_hereditary_constant", "profitable_hereditary_n"]
        profitable_modules = [f"profitable_hereditary_n_{i}" for i in range(2, 7)]
        modules.extend(profitable_modules)

        # 2) FISC-based recognizers, which may involve calls to the Glasgow subgraph solver
        modules.extend(["fisc_based_recognizers"])

        # 3) and then recognizers that run in O(n), O(n^2), ... time
        nonprofitable_modules = ["recognizers_n"] + [f"recognizers_n_{i}" for i in range(2, 12)]
        modules.extend(nonprofitable_modules)

        # gather and load all recognizers; they will be run in the order in which they are defined
        # in their respective modules
        for i, mod_name in enumerate(modules, 1):
            algos = getattr(import_module("." + mod_name, "graph_recognition"), "RECOGNIZERS")
            for class_id, recognizer in algos.items():
                self.register_recognizer(class_id, recognizer)

    def run_classification(self, input_files: List[str]) -> None:
        """Starts the classification of all graphs from the given input files."""
        # run all available recognizers on all stored graphs, propagating results as we go to avoid
        # unnecessary work:
        #   - if G is a member of C, then it is also a member of all ancestors of C;
        #   - if G is not a member of C, then it is not a member of any descendant of C either;
        #
        # We also use known exclusion relationships when available:
        #   - if G is a member of C, then it not a member of any class D excluded by C, nor is it
        #       a member of any descendant of D
        self.hits_and_misses = {"hits": 0, "misses": 0}
        self.gss_crashed = False
        # set up the progress bar for graphs
        num_graphs = sum(map(number_of_graphs_in_file, input_files))
        main_pbar = tqdm(
            chain.from_iterable(map(process_graphs, input_files)),
            desc=f"Classifying graphs from {len(input_files)} files",
            unit=" graph",
            total=num_graphs,
        )
        # record functions whose caches need to be cleared and which are not recognizers
        # TODO: later I'll write a function to retrieve these automatically, right now I only
        #   want to check if it's worth it
        other_caches_to_clear = [
            misc_algo.all_pairs_shortest_path_length,
            misc_algo.degree_sequence,
            misc_algo.is_complete,
            misc_algo.is_h_u_k1_free,
            misc_algo.is_h_u_k2_free,
            misc_algo.is_h_u_2k1_free,
            misc_algo.complement,
            misc_algo.number_of_common_neighbours,
            misc_algo.dominates,
            misc_algo.has_dominating_set_of_size_at_most_2,
            misc_algo.empty_graph_by_removing_edges_and_incident_edges,
            misc_algo.empty_graph_by_removing_vertices,
            misc_algo.is_connected,
            misc_algo.plain_co_bfs,
            misc_algo.is_co_connected,
            misc_algo.is_even_clique_free,
            misc_algo.is_odd_clique_free,
            misc_algo.is_even_co_clique_free,
            misc_algo.must_contain_a_clique_of_size,
            misc_algo.must_contain_an_independent_set_of_size,
            misc_algo.is_odd_co_clique_free,
        ]
        # finally, start the analysis
        for graph in main_pbar:
            # create classification for current graph
            classification = deepcopy(self.prototype_classification_digraph)
            # set up the progress bar for the classification of the current graph
            pbar = tqdm(
                self.recognizers,
                desc="  Running recognizers",
                leave=False,
                unit=" recognizer",
            )
            called_recognizers = set()
            for class_id, function in pbar:
                pbar.set_description("".join(["    ", BASE_CLASS_URL, class_id, " "]))
                if classification.has_open_node(class_id):
                    if class_id in self.blacklisted:
                        classification.set_reason(class_id, "user blacklisted this class")
                    else:
                        self.recognize_graph_and_propagate_results(
                            graph,
                            function,
                            called_recognizers,
                            classification,
                            class_id,
                        )

            # current graph has been classified: the corresponding cached data is no longer needed
            self._clear_recognizer_caches(called_recognizers)
            _clear_other_caches(other_caches_to_clear)
            clear_subgraph_cache(graph)
            self.update_classes_stats(classification)
            if self.gss_crashed:
                print("[WARNING] the glasgow subgraph or clique solver crashed")
            self.num_graphs += 1

    def recognize_graph_and_propagate_results(
            self,
            graph: nx.Graph,
            recognizer: Callable,
            called_recognizers: Set[Callable],
            classification: ClassificationDigraph,
            class_id: str,
    ) -> None:
        """
        Determines whether graph belongs to the graph class identified by class_id and propagates
        the implications of the result.

        :param graph: an undirected graph
        :param recognizer: the function to use to recognize the graph
        :param called_recognizers: the set of all recognizers that have been called for this graph
        :param classification: the classification digraph of the given graph
        :param class_id: the id of the class for which membership must be tested
        :return:
        """
        try:
            # recognize graph and store information for analysis and cache clearing
            result = recognizer(graph)
            self.recognizers_that_were_run.add(recognizer.__name__)
            called_recognizers.add(recognizer)
            # use membership information to propagate the results to superclasses or subclasses
            self.discarded_due_to_propagation += len(
                classification.label_and_propagate(
                    class_id,
                    result,
                    f"{recognizer.__name__} returns {result}",
                )
            )
            # additional propagations can be achieved if graph is a member of the given class
            if result:
                # if graph is a member of class and the recognizer has a FISC, then no subgraph in
                # its FISC appears in graph: propagate those findings
                if fisc := getattr(recognizer, "fisc", None):
                    _dispatch_findings(graph, fisc, False)

                # propagate findings using exclusion relationships if possible; class_id might be
                # known under different names in isgci_exclusion_graph, so we first need to find
                # them
                for equiv_id in {eq_id for _, eq_id in self.equivalences[class_id]} | {class_id}:
                    if self.isgci_exclusion_graph.has_node(equiv_id):
                        for successor in map(
                                self._get_stored_class_id,
                                self.isgci_exclusion_graph.successors(equiv_id),
                        ):
                            if classification.has_open_node(successor):
                                self.discarded_due_to_exclusion += len(
                                    classification.label_and_propagate(
                                        successor,
                                        False,
                                        f" successor of {equiv_id} in exclusion graph",
                                    )
                                )

            # note: it is tempting to propagate findings when the graph is NOT a member of the
            # class and the class admits a FISC of size one, since in this case we could conclude
            # that the only forbidden subgraph does appear in the graph. But I strongly advise
            # against it, because incomplete FISCs are allowed (see e.g. bipartite graphs) and
            # therefore non-membership in an S-free class could mean that some other subgraph not
            # listed in S is excluded.

        except subprocess.CalledProcessError:
            # this exception seems to happen when the graph is too large for GSS
            message = recognizer.__name__ + " crashed"
            classification.set_reason(class_id, message)
            self.gss_crashed = True

    def _acknowledge_classes(self, ids: Iterable[str], value: bool) -> None:
        """
        Records that ALL graphs are known to be (or NOT to be, depending on value) members of the
        classes provided in ids.

        :param ids:
        :return:
        """
        for class_id in ids:
            self.prototype_classification_digraph.label_and_propagate(
                self._get_stored_class_id(class_id),
                value,
                "user-provided information",
            )

    def _clear_recognizer_caches(
            self, called_recognizers: Iterable[Callable[[UndirectedGraph], bool]]
    ) -> None:
        """
        Clears the caches of all called recognizers. Only recognizers decorated with lru_cache are
        allowed.

        @return:
        """
        for recognizer in called_recognizers:
            try:
                self.hits_and_misses["hits"] += recognizer.cache_info().hits
                self.hits_and_misses["misses"] += recognizer.cache_info().misses
                recognizer.cache_clear()
            except AttributeError:
                print(
                    f"failed to clear cache for function {recognizer.__name__} from "
                    f"{recognizer.__module__}"
                )
                # all recognizers are supposed to be cached, so we exit if something went wrong
                # to signal it has to be fixed
                exit(-1)

    def acknowledge_positive_classes(self, positive_ids: Iterable[str]) -> None:
        """
        Records that ALL graphs are known to be members of the classes provided in positive_ids.

        :param positive_ids:
        :return:
        """
        self._acknowledge_classes(positive_ids, True)

    def acknowledge_negative_classes(self, negative_ids: Iterable[str]) -> None:
        """
        Records that ALL graphs are known NOT to be members of the classes provided in
        negative_ids.

        :param negative_ids:
        :return:
        """
        self._acknowledge_classes(negative_ids, False)

    def blacklist(self, skip_ids: Iterable[str]) -> None:
        """
        Blacklists the recognizers for classes provided in skip_ids: they will not be run.

        :param skip_ids:
        :return:
        """
        # we maintain a blacklisted data structure instead of removing blacklisted ids from the
        # prototype classification, because we want to tell user why a recognizer has not been
        # run; in order to do that, we keep the corresponding nodes, and skip them in
        # self.run_classification
        self.blacklisted.update(skip_ids)

    def restrict_to(self, only_ids: Iterable[str]) -> None:
        """
        Restricts the classification to the recognizers for classes provided in only_ids.

        :param only_ids:
        :return:
        """
        self.prototype_classification_digraph.remove_nodes_from(
            set(self.prototype_classification_digraph)
            - {self._get_stored_class_id(elem) for elem in only_ids}
        )

    def _get_stored_class_id(self, class_id: str) -> str:
        """
        Returns the class id equivalent stored in the classification graphs that is equivalent to
        the given class_id (possibly class_id itself).

        @type class_id: str
        @rtype: str
        @param class_id:
        @return:
        """
        if class_id in self.isgci_graph:
            return class_id

        for _, eq_id in self.equivalences[class_id]:
            if eq_id in self.isgci_graph:
                return eq_id

        raise ValueError(class_id + " not found, nor any equivalent id")

    def update_classes_stats(self, classification: ClassificationDigraph) -> None:
        """
        Increments the counters of each positive node in the classification, as well as those of
        their ancestors.

        :return:
        """
        # for each positive node in the classification: increment its counter as well as those of
        # its ancestors. it is necessary to compute the union beforehand, otherwise positive nodes
        # that share ancestors will wrongfully increment their counters multiple times
        minus_nodes, plus_nodes = classification.negative_nodes(), classification.positive_nodes()
        for node in set.union(*({v}.union(self.tc_isgci.predecessors(v)) for v in plus_nodes)):
            self.enumeration_of_positive_classes[node] += 1

        # update relevant positive nodes and unknown nodes
        self.relevant_classes.update(plus_nodes)
        self.unknown_nodes.discard(plus_nodes.union(minus_nodes))

        # update other stats
        num_open_nodes = classification.number_of_open_nodes()
        self.max_unknown_classes = max(self.max_unknown_classes, num_open_nodes)
        self.min_unknown_classes = min(self.min_unknown_classes, num_open_nodes)

    def get_recognizer(self, class_id: str) -> Callable:
        """
        Returns a recognizer for the given class_id if one is available, None otherwise.

        @param class_id:
        @return:
        """
        # self.recognizers contains pairs of the form (class_id, recognizer) for each recognizable
        # class as well as for the equivalent classes; which is why we do not explicitly compute
        # equivalences ourselves
        for name, function in self.recognizers:
            if name == class_id:
                return function

        raise ValueError(f"no recognizer found for {class_id} or any equivalent class")

    def number_of_graphs(self) -> int:
        """
        Returns the number of stored graphs.

        @return:
        """
        return self.num_graphs

    def print_summary_of_findings(
            self, print_unknown_descendants: bool = False, print_todo: bool = False
    ) -> None:
        """
        Prints summary of a graph analyzer's findings as a table containing the percentage of
        graphs that belong to each class, sorted by decreasing cardinality.

        @param self:
        @param print_unknown_descendants:
        @param print_todo:
        @return:
        """
        # NEW VERSION
        # discard the counters of all irrelevant classes
        self.enumeration_of_positive_classes = {
            key: val for key, val in self.enumeration_of_positive_classes.items()
            if key in self.relevant_classes
        }
        # sort classes by descending cardinality
        print("# Summary of findings")
        new_results = sorted(
            ((val, key) for key, val in self.enumeration_of_positive_classes.items()), reverse=True
        )

        num_graphs = self.number_of_graphs()

        if num_graphs == 1:
            print("The graph is:\n")

        isgci_graph = reduced_isgci_inclusion_graph()  # TODO isn't self.tc_isgci enough? or self.isgci_graph?
        ids_to_names = isgci_ids_to_names()
        recog_status = isgci_recognition_statuses()
        for num, class_id in new_results:
            print(
                ["{:.2f}".format(100 * num / num_graphs).rjust(6) + "% are", "-"][num_graphs == 1],
                f"[{ids_to_names[class_id]}]({urllib.parse.urljoin(BASE_CLASS_URL, class_id)})"
            )
            # print unidentified maximal subclasses, so I know what to implement next
            if print_unknown_descendants:
                unknown_children = self.unknown_nodes.intersection(isgci_graph.successors(class_id))
                print(f"    class has {len(unknown_children)} unidentified maximal subclasses")
                for child in unknown_children:
                    print(
                        " " * 8,
                        ids_to_names[child],
                        "---",
                        urllib.parse.urljoin(BASE_CLASS_URL, child),
                        recog_status[child],
                    )

                if unknown_children:
                    print()

                unknown_descendants = (
                    set(nx.descendants(isgci_graph, class_id))
                    .intersection(self.unknown_nodes)
                    .difference(unknown_children)
                )
                print(f"    class has {len(unknown_descendants)} further unidentified descendants")
                for child in unknown_descendants:
                    print(
                        " " * 8,
                        ids_to_names[child],
                        "---",
                        urllib.parse.urljoin(BASE_CLASS_URL, child),
                        recog_status[child],
                    )

                print()

        lo, hi = self.min_unknown_classes, self.max_unknown_classes

        print()
        print("We have", [f"between {lo} and {hi}", lo][lo == hi], "unidentified classes.")

        if print_todo:
            # print all classes that can be recognized in polynomial time, but for which we have no
            # implemented recognizer yet
            print("All polynomially-recognizable unknown nodes:")
            for node in self.unknown_nodes:
                if recog_status[node] in {"Linear", "Polynomial"}:
                    print(urllib.parse.urljoin(BASE_CLASS_URL, node), recog_status[node])

        if print_todo:
            # print all classes that can be recognized in polynomial time, but for which we have no
            # implemented recognizer yet
            print("All polynomially-recognizable unknown nodes:")
            for node in self.unknown_nodes:
                if recog_status[node] in {"Linear", "Polynomial"}:
                    print(urllib.parse.urljoin(BASE_CLASS_URL, node), recog_status[node])

    def print_analysis_statistics(self) -> None:
        """
        Prints various information regarding the analysis that has been performed.

        @return:
        """
        # TODO add info on "only" classes as instructed by user
        # TODO add info on positive / negative classes communicated by user
        print(underlined("Analysis statistics"))
        # information on recognizers
        print("- recognizers:")
        print(
            f"    - {len(self.recognizers_that_were_run)} / {len(self.recognizers)} recognizers "
            f"were called by the analyzer."
        )
        print(
            f"    - {self.hits_and_misses['hits']} cache hits and {self.hits_and_misses['misses']} "
            f"cache misses occurred (so "
            f"{round(100 * self.hits_and_misses['hits'] / (self.hits_and_misses['hits'] + self.hits_and_misses['misses']), 2)} % "
            f"of all calls to recognizers were simple lookups)."
        )
        # information on skipped classes
        print("- skipped classes:")
        print(
            f"    - {self.discarded_due_to_propagation // self.number_of_graphs()} classes were "
            f"skipped thanks to inclusion relationships",
            end="",
        )
        print(
            [".", f" (average over {self.number_of_graphs()} graphs)."][
                self.number_of_graphs() > 1
                ]
        )
        print(
            f"    - {self.discarded_due_to_exclusion // self.number_of_graphs()} classes were "
            f"skipped thanks to exclusion relationships",
            end="",
        )
        print(
            [".", f" (average over {self.number_of_graphs()} graphs)."][
                self.number_of_graphs() > 1
                ]
        )
        if self.blacklisted:
            print(
                f"    - {len(self.blacklisted)} classes were skipped as per instructed by the "
                f"user; specifically: {sorted(self.blacklisted)}"
            )

        print("- external tools:")
        print(
            f"    - the Glasgow Clique Solver was run {SubgraphMatcher.number_of_calls_to_gcs} "
            f"times."
        )
        print(
            f"    - the Glasgow Subgraph Solver was run {SubgraphMatcher.number_of_calls_to_gss} "
            f"times."
        )

        print()
        print(underlined("ISGCI statistics"))

        for key, val in isgci_version_info().items():
            print(f"- {key}: {val}")

        print()
