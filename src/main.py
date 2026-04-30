"""
Anthony Labarre © 2023-2026

graphotaxy's main file. Takes as input one or more files each containing one or more graphs, and
outputs the classes in ISGCI to which these graphs belong, being as precise as possible.

"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
import argparse
import os
import sys
from typing import Iterable, Callable

# ----- Non-standard imports ----------------------------------------------------------------------
import networkx as nx

nx.config.cache_converted_graphs = False
from tqdm import tqdm

# ----- My imports --------------------------------------------------------------------------------
from graph_analyzer import GraphAnalyzer
from graph_recognition import recognizers_utils
from isgci.isgci_base import isgci_equivalences


# Global variables --------------------------------------------------------------------------------


# Functions ---------------------------------------------------------------------------------------
def knows(class_ids: Iterable[str]) -> None:
    """
    Checks whether the classes provided as class id's can be recognized, whether directly or by
    means of a recognizer for an equivalent class.

    >>> knows(["gc_1362", "gc_66", "gc_2"])
    gc_1362: found recognizer is_2_edge_connected in graph_recognition.recognizers_n
    gc_66  : no recognizer available
    gc_2   : found recognizer is_gc_1 in graph_recognition.profitable_hereditary_n_4

    """

    # applying assign_inherited_fisc to all recognizers takes a long time and is useless in this
    # particular use case; so we replace the decorator by an identity mapping, which simply returns
    # the original function.
    def identity_mapping(*_args, **_kwargs) -> Callable:
        """
        Useless decoration of a function (has no effect).

        :return:
        """

        def decorator(func: Callable) -> Callable:
            """
            Returns func.

            :param func:
            :return:
            """
            return func

        return decorator

    setattr(recognizers_utils, "assign_inherited_fisc", identity_mapping)

    longest_name_length = max(map(len, class_ids))
    analyzer = GraphAnalyzer(run_exponential_algos=True)
    for _id in class_ids:
        try:
            function = analyzer.get_recognizer(_id)
            print(
                f"{_id.ljust(longest_name_length)}: found recognizer {function.__name__} in "
                f"{function.__module__}"
            )
            break

        except KeyError:
            print(f"{_id.ljust(longest_name_length)}: no recognizer available")


def print_capabilities() -> None:
    """
    Prints program's capabilities. Currently, this means:

    - the number of implemented recognizers
    - the number of classes that can be recognized, taking equivalences into account (e.g., if
        a class C is equivalent to k other classes, then a recognizer for class C allows us to
        recognize k+1 classes)

    """
    # compute the set of all recognizable classes: recognizers handle a class and all equivalent
    # classes
    analyzer = GraphAnalyzer(run_exponential_algos=True)
    equivs = isgci_equivalences()

    print(
        f"{analyzer.number_of_recognizers} recognizers are currently implemented, covering "
        f"{len(analyzer.recognizers)} classes out of {len(equivs)} "
        f"({round(100 * len(analyzer.recognizers) / len(equivs), 2)} % coverage)"
    )
    print("\nThe classes with the following ids can be recognized:\n")
    for class_id in sorted(analyzer.recognizers):
        print(f"    - {class_id}")


def main() -> None:
    """
    The main part of the program: takes as input one or several files each containing one or more
    graphs, and outputs the results of its analysis.

    @return:
    """
    parser = argparse.ArgumentParser(
        description="graphotaxy analyzes one or several graphs stored in one or more input files, "
                    "and outputs membership information about them with respect to the classes "
                    "available in ISGCI (see https://www.graphclasses.org/)."
    )
    parser.add_argument(
        "-i", "--input",
        help="the graph file(s) to analyze; acceptable extensions are .dot, .edges, .g6, .mtx, .s6, "
             ".g6.[bz2,gz,xz], and .s6.[bz2,gz,xz]",
        nargs="+"
    )

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
                    "program. Use ISGCI ids for all values.",
    )
    input_options.add_argument(
        "--negative",
        nargs="+",
        help="classes to which all input graphs are known not to belong",
    )
    input_options.add_argument(
        "--positive",
        nargs="+",
        help="classes to which all input graphs are known to belong",
    )
    behavior_options = parser.add_argument_group(
        "behavior options",
        description="The following options modify the behavior of the program, i.e., which "
                    "recognizers should be run or skipped.",
    )

    behavior_options.add_argument(
        "--exponential",
        action="store_true",
        help="run exponential-time recognizers (default: False)",
    )
    behavior_options.add_argument(
        "--only",
        nargs="+",
        help="classes to which the classification must be restricted",
    )
    behavior_options.add_argument(
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
        help="in addition to each recognized class, print its descendants which have not been "
             "identified (if any)",
    )
    display_options.add_argument(
        "--todo",
        action="store_true",
        help="show the classes that have not been identified, although recognizable in "
             "polynomial time, due to the lack of an implemented recognizer",
    )

    if len(sys.argv) == 1:
        parser.print_help()
        parser.exit()

    args = parser.parse_args()

    if args.capabilities:
        print_capabilities()
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
    analyzer = GraphAnalyzer(run_exponential_algos=args.exponential)

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
        class_ids_without_a_recognizer = set()
        for class_id in args.only:
            try:
                analyzer.get_recognizer(class_id)
            except KeyError:
                class_ids_without_a_recognizer.add(class_id)

        if class_ids_without_a_recognizer:
            print(
                "The following class ids have no recognizer. Make sure you use the --exponential "
                "option to include all recognizers.\n"
            )
            for class_id in sorted(class_ids_without_a_recognizer):
                print(f"- {class_id}")

            print("\nAborting.")
            exit(-1)

    if args.skip:
        analyzer.blacklist(args.skip)

    analyzer.run_classification(args.input)
    print()
    analyzer.print_summary_of_findings(args.print_unknown_descendants, args.todo)
    print()
    analyzer.print_analysis_statistics()

    # single graph classification: output classification as a GML graph so that it can later be
    # read by tools like cytoscape
    if analyzer.num_graphs == 1:
        print(
            f"\nWriting GraphML file to {os.path.basename(args.input[0])}.graphml ... ", end="",
        )
        nx.write_graphml(analyzer.classification, os.path.basename(args.input[0]) + ".graphml")
        print("done.\n")


if __name__ == "__main__":
    main()
