"""
Anthony Labarre © 2023-2025

Python rewrite of cognos. Takes as input a graph file containing one or more graphs, and outputs
the classes in ISGCI to which these graphs belong, being as precise as possible.

"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
import argparse
import logging
import os
import sys
from collections import defaultdict
from typing import Iterable

# ----- Non-standard imports ----------------------------------------------------------------------
import networkx as nx
from tqdm import tqdm

# ----- My imports --------------------------------------------------------------------------------
from graph_analyzer import GraphAnalyzer
from isgci.isgci_base import isgci_equivalences

# Global variables --------------------------------------------------------------------------------
logger = logging.getLogger(__name__)


# Functions ---------------------------------------------------------------------------------------
def knows(class_ids: Iterable[str]) -> None:
    """Checks whether the classes provided as class id's can be recognized, whether directly or by
    means of a recognizer for an equivalent class.

    >>> knows(["gc_1362", "gc_66", "gc_2"])
    gc_1362: found recognizer is_2_edge_connected in graph_recognition.recognizers_n
    gc_66  : no recognizer available
    gc_2   : found recognizer is_gc_1 in graph_recognition.profitable_hereditary_n_4

    """
    longest_name_length = max(map(len, class_ids))
    analyzer = GraphAnalyzer()
    for _id in class_ids:
        try:
            function = analyzer.get_recognizer(_id)
            print(
                f"{_id.ljust(longest_name_length)}: found recognizer {function.__name__} in "
                f"{function.__module__}"
            )
            break

        except ValueError:
            print(f"{_id.ljust(longest_name_length)}: no recognizer available")


def check_for_multiple_recognizers() -> None:
    """
    Checks for graph classes that have multiple recognizers.

    This function was written for debugging purposes: only one recognizer, if any, should be
    available for each graph class. If a class has several recognizers, then only one of them is
    really useful: the others may be redundant, less efficient, or the result of wrong
    associations (class id paired with the wrong function).

    @return:
    """
    # scan for classes with multiple recognizers
    ids_to_recognizers = defaultdict(set)
    analyzer = GraphAnalyzer()
    equivs = isgci_equivalences()
    coverage = set()
    for class_id, *_ in analyzer.recognizers:
        coverage.add(class_id)
        coverage.update(eqid for _, eqid in equivs[class_id])
        ids_to_recognizers[class_id].update(_)

    # no problem found -> stop
    if all(len(val) == 1 for val in ids_to_recognizers.values()):
        print("No class with multiple recognizers found")
        return

    # otherwise, print classes with multiple recognizers
    for a, b in ids_to_recognizers.items():
        if len(b) > 1:
            print(
                f"https://www.graphclasses.org/classes/{a} has more than one recognizer:"
            )
            for recognizer in b:
                print(f"  {recognizer.__name__} in {recognizer.__module__}")


def print_capabilities() -> None:
    """Prints program's capabilities. Currently, this means:

    - the number of implemented recognizers
    - the number of classes that can be recognized, taking equivalences into account (e.g., if
        a class C is equivalent to k other classes, then a recognizer for class C allows us to
        recognize k+1 classes)

    """
    # compute the set of all recognizable classes: recognizers handle a class and all equivalent
    # classes
    analyzer = GraphAnalyzer()
    equivs = isgci_equivalences()
    coverage = set()
    for class_id, *_ in analyzer.recognizers:
        coverage.add(class_id)
        coverage.update(eqid for _, eqid in equivs[class_id])

    print(
        f"{len(analyzer.recognizers)} recognizers are currently implemented, covering "
        f"{len(coverage)} classes out of {len(equivs)} "
        f"({round(100 * len(coverage) / len(equivs), 2)} % coverage)"
    )


def main():
    """
    The main part of the program: takes as input a graph file, and outputs the results of its
    analysis.

    @return:
    """
    logging.basicConfig(filename="myapp.log", level=logging.INFO)
    logger.info("Started")

    parser = argparse.ArgumentParser(
        description="graphotaxy analyzes one or several graphs stored in one or more input files, "
        "and outputs membership information about them with respect to the classes "
        "available in ISGCI (see https://www.graphclasses.org/)."
    )
    parser.add_argument("-i", "--input", help="the graph file(s) to analyze", nargs="+")

    info_options = parser.add_argument_group(
        "info options",
        description="The following options cause the program to display various information "
        "instead of performing an analysis. Using them will cause any input file to be "
        "ignored.",
    )

    info_options.add_argument(
        "--capabilities",
        action="store_true",
        help="display various information about what the program can do",
    )
    info_options.add_argument(
        "--knows",
        nargs="+",
        help="identify classes that the program can(not) recognize; use ISGCI ids",
    )

    input_options = parser.add_argument_group(
        "input options",
        description="The following options modify the information that is given as input to the "
        "program.",
    )
    input_options.add_argument(
        "--negative",
        nargs="+",
        help="classes to which all input graphs are known not to belong; use ISGCI ids",
    )
    input_options.add_argument(
        "--positive",
        nargs="+",
        help="classes to which all input graphs are known to belong; use ISGCI ids",
    )
    input_options.add_argument(
        "--only",
        nargs="+",
        help="classes to which the classification must be restricted; use ISGCI ids",
    )
    input_options.add_argument(
        "--skip",
        nargs="+",
        help="classes whose recognition should be skipped; use ISGCI ids",
    )

    display_options = parser.add_argument_group(
        "display options",
        description="The following options modify the information that is displayed by the program.",
    )
    display_options.add_argument(
        "--disable-progress-bars",
        action="store_true",
        help="disables all progress bars; only the final result will appear",
    )
    display_options.add_argument(
        "--print-unknown-descendants",
        action="store_true",
        help="in addition to each recognized class, print its descendants, if "
        "any, which have not been identified",
    )
    display_options.add_argument(
        "--todo",
        action="store_true",
        help="show the classes that have not been identified, although recognizable in "
        "polynomial time, due to the lack of an implemented recognizer",
    )

    debug_options = parser.add_argument_group(
        "debug options",
        description="The following options are helpful to debug the program. They should be of no "
        "interest to the end user.",
    )
    debug_options.add_argument(
        "--check-multiple",
        action="store_true",
        help="show which classes, if any, have multiple recognizers",
    )

    if len(sys.argv) == 1:
        parser.print_help()
        parser.exit()

    args = parser.parse_args()

    if args.capabilities:
        print_capabilities()
        return

    if args.check_multiple:
        check_for_multiple_recognizers()
        return

    if args.knows:
        knows(args.knows)
        return

    # if any input file does not exist, print it and abort
    for path in args.input:
        if not os.path.exists(path):
            print("Error:", path, "does not exist")
            sys.exit(-1)

    if args.disable_progress_bars:
        # from https://stackoverflow.com/a/67238486/
        from functools import partialmethod

        tqdm.__init__ = partialmethod(tqdm.__init__, disable=True)

    print()
    analyzer = GraphAnalyzer()

    # pass known classification information if provided
    if args.positive:
        analyzer.acknowledge_positive_classes(args.positive)

    if args.negative:
        analyzer.acknowledge_negative_classes(args.negative)

    if args.only and args.skip:
        print("Error: --only and --skip options are mutually exclusive")
        exit(-1)

    if args.only:
        analyzer.restrict_to(args.only)

    if args.skip:
        analyzer.blacklist(args.skip)

    analyzer.run_classification(args.input)
    print()
    analyzer.print_summary_of_findings(args.print_unknown_descendants, args.todo)
    print()
    analyzer.print_analysis_statistics()

    # single graph classification: output classification as a GML graph so that it can later be
    # read by tools like cytoscape
    if analyzer.number_of_graphs() == 1:
        print()
        print(
            f"Writing GraphML file to {os.path.basename(args.input[0])}.graphml ... ",
            end="",
        )
        nx.write_graphml(
            next(iter(analyzer.classifications)),
            os.path.basename(args.input[0]) + ".graphml",
        )
        print("done.")

    logger.info("Finished")


if __name__ == "__main__":
    main()
