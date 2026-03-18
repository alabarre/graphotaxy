"""
Anthony Labarre © 2023-2026

Implementation of a GraphAnalyzer class. The purpose of an instance of this class is to produce
classifications for one or more undirected graphs.

To use a GraphAnalyzer:

    analyzer = GraphAnalyzer()                         # instantiate it
    # possibly set options through method calls, see class definition below
    analyzer.run_classification(paths_to_input_files)  # feed it data and start classification
    analyzer.print_summary_of_findings()               # print results

"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
import subprocess
import sys
import urllib
from collections import defaultdict, OrderedDict
from copy import deepcopy
from importlib import import_module
from itertools import chain
from os import listdir
from typing import Callable, Iterable, Set, List

# ----- Third-party imports -----------------------------------------------------------------------
import networkx as nx
from cupy import positive
from tqdm import tqdm

# ----- My imports --------------------------------------------------------------------------------
from cache_utils import clear_function_caches, get_cached_non_recognizers
from classification_digraph import ClassificationDigraph
from graph_recognition.subgraphs import SubgraphMatcher, _dispatch_findings, clear_subgraph_cache
from isgci.isgci_base import (
    isgci_equivalences,
    BASE_CLASS_URL,
    isgci_ids_to_names,
    isgci_exclusion_graph, isgci_recognition_statuses, isgci_version_info,
)
from printing import underlined
from readwrite import process_graphs, number_of_graphs_in_file


# Classes -----------------------------------------------------------------------------------------
class GraphAnalyzer:
    """The class responsible for classifying a bunch of undirected graphs."""

    def __init__(self) -> None:
        """
        Initializes all data structures.
        """
        # data related to a modified behavior GraphAnalyzer ---------------------------------------
        self.blacklisted = set()
        self.scope = set()

        # data related to classification ----------------------------------------------------------
        self.classification = None  # stores the classification if we have only one graph
        self.enumeration_of_positive_classes = defaultdict(int)
        self.isgci_exclusion_graph = isgci_exclusion_graph()
        self.max_unknown_classes = 0
        self.min_unknown_classes = sys.maxsize
        self.num_graphs = 0
        self.prototype_classification_digraph = ClassificationDigraph()
        self.provided_negative = set()
        self.provided_positive = set()
        self.relevant_classes = set()
        self.tc_isgci = nx.transitive_closure_dag(ClassificationDigraph())
        self.unknown_nodes = set()

        # data related to analysis statistics -----------------------------------------------------
        self.discarded_due_to_exclusion = 0
        self.discarded_due_to_propagation = 0
        self.gss_crashed = False
        self.hits_and_misses = {"hits": 0, "misses": 0}
        self.recognizers_that_were_run = set()

        # other useful data -----------------------------------------------------------------------
        self.equivalences = isgci_equivalences()
        self.recognizers = OrderedDict()
        self.setup_recognizers()

    # Methods related to recognizers --------------------------------------------------------------
    def get_recognizer(self, class_id: str) -> Callable:
        """
        Returns a recognizer for the given class_id if one is available, None otherwise.

        @param class_id:
        @return:
        """
        # since self.recognizers maps class ids to recognizer for each recognizable class as well
        # as for its equivalent classes, we can simply search for the provided class_id
        return self.recognizers[class_id]

    def register_recognizer(self, class_id: str, recognizer: Callable) -> None:
        """
        Adds a recognizer to the list of recognizers to use for the given class as well as all
        equivalent classes.

        :param class_id:
        :param recognizer:
        :return:
        """
        self.recognizers[class_id] = recognizer
        self.recognizers.update({eq_id: recognizer for _, eq_id in self.equivalences[class_id]})

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

    # Methods related to the actual classification ------------------------------------------------
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
        # record functions whose caches need to be cleared and which are not recognizers; these
        # include all such functions defined in the graph_recognition module
        other_caches_to_clear = set.union(*(
            get_cached_non_recognizers("graph_recognition." + module.replace(".py", ""))
            for module in listdir("graph_recognition") if module.endswith(".py")
        ))
        # finally, start the analysis
        for graph in main_pbar:
            # create classification for current graph
            self.classification = deepcopy(self.prototype_classification_digraph)
            # set up the progress bar for the classification of the current graph
            pbar = tqdm(
                self.recognizers.items(),
                desc="  Running recognizers",
                leave=False,
                unit=" recognizer",
            )
            called_recognizers = set()
            for class_id, function in pbar:
                pbar.set_description("".join(["    ", BASE_CLASS_URL, class_id, " "]))
                if self.classification.has_open_node(class_id):
                    if class_id in self.blacklisted:
                        self.classification.set_reason(class_id, "user blacklisted this class")
                    else:
                        self.recognize_graph_and_propagate_results(
                            graph,
                            function,
                            called_recognizers,
                            self.classification,
                            class_id,
                        )

            # current graph has been classified, update stats:
            self.update_classes_stats(self.classification)
            if self.gss_crashed:
                print("[WARNING] the glasgow subgraph or clique solver crashed")
            self.num_graphs += 1

            # the corresponding cached data is no longer needed, so we clear the caches of:
            hits, misses = clear_function_caches(called_recognizers)  # all called recognizers
            self.hits_and_misses["hits"] += hits
            self.hits_and_misses["misses"] += misses
            clear_subgraph_cache(graph)  # everything related to subgraph matching
            clear_function_caches(other_caches_to_clear)  # and all other cached functions

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

        :param graph: an undirected graph.
        :param recognizer: the function to use to recognize the graph.
        :param called_recognizers: the set of all recognizers that have been called for this graph.
        :param classification: the classification digraph of the given graph.
        :param class_id: the id of the class for which membership must be tested.
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
        if plus_nodes:
            for node in set.union(*({v}.union(self.tc_isgci.predecessors(v)) for v in plus_nodes)):
                self.enumeration_of_positive_classes[node] += 1

        # update relevant positive nodes and unknown nodes
        self.relevant_classes.update(plus_nodes)
        self.unknown_nodes.update(classification.open_nodes())

        # update other stats
        num_open_nodes = classification.number_of_open_nodes()
        self.max_unknown_classes = max(self.max_unknown_classes, num_open_nodes)
        self.min_unknown_classes = min(self.min_unknown_classes, num_open_nodes)

    # Methods related to setting up GraphAnalyzer -------------------------------------------------
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

    def acknowledge_positive_classes(self, positive_ids: Iterable[str]) -> None:
        """
        Records that ALL graphs are known to be members of the classes provided in positive_ids.

        :param positive_ids:
        :return:
        """
        self._acknowledge_classes(positive_ids, True)
        self.provided_positive = sorted(positive_ids)

    def acknowledge_negative_classes(self, negative_ids: Iterable[str]) -> None:
        """
        Records that ALL graphs are known NOT to be members of the classes provided in
        negative_ids.

        :param negative_ids:
        :return:
        """
        self._acknowledge_classes(negative_ids, False)
        self.provided_negative = sorted(negative_ids)

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
        self.scope.update(only_ids)

    # Other helpful methods -----------------------------------------------------------------------
    def _get_stored_class_id(self, class_id: str) -> str:
        """
        Returns the class id stored in the classification graph that is equivalent to the given
        class_id (possibly class_id itself).

        @type class_id: str
        @rtype: str
        @param class_id:
        @return:
        """
        if class_id in self.tc_isgci:
            return class_id

        for _, eq_id in self.equivalences[class_id]:
            if eq_id in self.tc_isgci:
                return eq_id

        raise ValueError(class_id + " not found, nor any equivalent id")

    def number_of_graphs(self) -> int:
        """
        Returns the number of stored graphs.

        @return:
        """
        return self.num_graphs

    # Methods related to reporting results --------------------------------------------------------
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
        # discard the counters of all irrelevant classes
        self.enumeration_of_positive_classes = {
            key: val for key, val in self.enumeration_of_positive_classes.items()
            if key in self.relevant_classes
        }
        # sort classes by descending cardinality
        print(underlined("Summary of findings"))
        results = sorted(
            ((val, key) for key, val in self.enumeration_of_positive_classes.items()), reverse=True
        )

        if self.num_graphs == 1:
            print("The graph is:\n")

        ids_to_names = isgci_ids_to_names()
        recog_status = isgci_recognition_statuses()
        for num, class_id in results:
            print(
                "".join([
                    ["- " + "{:.2f}".format(100 * num / self.num_graphs).rjust(6) + "% are ", "- "][
                        self.num_graphs == 1],
                    f"[{ids_to_names[class_id]}]({urllib.parse.urljoin(BASE_CLASS_URL, class_id)})"
                ]))
            # print unidentified maximal subclasses, so I know what to implement next
            if print_unknown_descendants:
                unknown_children = self.unknown_nodes.intersection(
                    self.prototype_classification_digraph.successors(class_id)
                )
                print(f"    - class has {len(unknown_children)} unidentified maximal subclasses")
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
                    set(nx.descendants(self.prototype_classification_digraph, class_id))
                    .intersection(self.unknown_nodes)
                    .difference(unknown_children)
                )
                print(f"    - class has {len(unknown_descendants)} further unidentified descendants")
                for child in unknown_descendants:
                    print(
                        " " * 8 + f"[{ids_to_names[class_id]}]"
                                  f"({urllib.parse.urljoin(BASE_CLASS_URL, class_id)}) "
                                  f"{recog_status[child]}"
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

    def print_analysis_statistics(self) -> None:
        """
        Prints various information regarding the analysis that has been performed.

        @return:
        """
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
            f"    - {self.discarded_due_to_propagation // self.num_graphs} classes were skipped "
            f"thanks to inclusion relationships",
            end="",
        )
        print([".", f" (average over {self.num_graphs} graphs)."][self.num_graphs > 1])
        print(
            f"    - {self.discarded_due_to_exclusion // self.num_graphs} classes were "
            f"skipped thanks to exclusion relationships",
            end="",
        )
        print([".", f" (average over {self.num_graphs} graphs)."][self.num_graphs > 1])
        if self.blacklisted:
            print(
                f"    - {len(self.blacklisted)} classes were skipped as instructed by the "
                f"user; specifically: {sorted(self.blacklisted)}"
            )
        if self.scope:
            print(
                f"    - only the following {len(self.scope)} classes were considered as "
                f"instructed by the user; specifically: {sorted(self.scope)}"
            )
        if self.provided_negative:
            print(
                f"    - the following {len(self.provided_negative)} classes were identified as "
                f"negative by the user: {self.provided_negative}"
            )
        if self.provided_positive:
            print(
                f"    - the following {len(self.provided_positive)} classes were identified as "
                f"positive by the user: {self.provided_positive}"
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
