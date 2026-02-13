"""
Anthony Labarre © 2023-2025

Utilities for handling smallgraphs. This module is responsible for providing the LAD files that
will be used by the Glasgow Subgraph Solver.

I'll often use the following acronyms in my code:

    FIS = Forbidden Induced Subgraph;
    FISC = Forbidden Induced Subgraph Characterisation;
    fiscky [class] = [class that] has a finite FISC.

As a stand-alone module, this program can be used to do two things (if you are not contributing to
the development of this software, you have no need for them):

    --generate-recognizers: generates all functions for recognizing fiscky classes, and writes the
        corresponding recognizers to ./generated_recognizers.py

    --build-inclusion-graph: generates and writes the smallgraph inclusion graph to
        ./smallgraph_inclusion_graph, so the subgraphs.py module can take advantage of it.

TODO make it much more user-friendly for people who want to add their own smallgraphs; explain how somewhere
"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
import json
import logging
import os
import pathlib
import shutil
import sys
import textwrap
from collections import defaultdict
from datetime import datetime
from io import TextIOWrapper
from itertools import combinations
from shutil import copyfile
from typing import Iterable, Any

# ----- Third-party imports -----------------------------------------------------------------------
import networkx as nx
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

# ----- My imports --------------------------------------------------------------------------------
from graph_recognition.graph_formats import g6string_to_lad, lad_file_to_nx_graph
from isgci.functions import prettify_name
from isgci.graphclass import GraphClass
from isgci.isgci_base import BASE_URL, save_webpage_to_file
from isgci.vars import ISGCI_DIR, PATHS

# Globals and classes -----------------------------------------------------------------------------
SMALLGRAPH_DIR = os.path.join(os.path.dirname(__file__), "smallgraphs")
__JSON_DUMP_ARGS = {"default": list, "indent": 4, "sort_keys": True}
WRAP_WIDTH = 100


# The following custom JSON encoder returns a dictionary representation of a GraphClass, so we can
# use json.dumps on those structures
class GraphClassEncoder(json.JSONEncoder):
    def default(self, gc: GraphClass):
        if isinstance(gc, GraphClass):
            return {
                "class_id": gc.class_id(),
                "class_name": gc.class_name(),
                "fisc": list(
                    gc.fisc()
                ),  # conversion is mandatory since json cannot serialize sets
            }

        # let the base class default method raise the TypeError
        return super().default(gc)


# Functions ---------------------------------------------------------------------------------------
# The following functions help us generate code in "the right order" ------------------------------
def partition_by_pattern_max_size_then_number(
    graphclass_bunch: Iterable[dict], smallgraph_names_and_orders: dict[str, int]
) -> defaultdict[int, list[dict]]:
    """
    Returns a dictionary indexed by order in which graphclass objects from the input are grouped
    according to the size of the largest pattern they contain. Assumes only fiscky classes are
    given.

    :param smallgraph_names_and_orders:
    :param graphclass_bunch: an iterable of GraphClass objects.
    :return:
    """
    partition = defaultdict(list)

    # first pass on data: partition by maximum pattern size
    for gc in graphclass_bunch:
        partition[max(map(smallgraph_names_and_orders.get, gc["fisc"]))].append(gc)

    # second pass on data: sort groups by numbers of patterns
    for order in partition:
        partition[order].sort(key=lambda _gc: len(_gc["fisc"]))

    return partition


def url_to_soup(url: str) -> BeautifulSoup:
    """
    Returns the contents of url as a soup object.

    :type url: str
    """
    return BeautifulSoup(requests.get(url, timeout=10).text, "html.parser")


def all_smallgraphs_by_order(force_rebuild=False) -> defaultdict[int, set]:
    """
    Returns all smallgraphs in ISGCI as a dictionary of graph6 strings, partitioned by graph order.

    The following tests count smallgraphs by their order and are valid as of 2024-07-13 (but might
    not be later if their database of smallgraphs changes). They include all 542 smallgraphs listed
    at https://www.graphclasses.org/smallgraphs.html , as well as some others that appear in a few
    classes' description but have been omitted from their smallgraph directory:

    >>> result = all_smallgraphs_by_order()
    >>> sorted(result.keys())
    [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13]
    >>> [len(val) for _, val in sorted(result.items())]
    [2, 6, 13, 36, 102, 183, 162, 50, 31, 6, 3]
    >>> sum(len(val) for val in result.values())
    594
    >>> sorted(result[2])
    [['2K_{1}', 'A?'], ['K_{2}', 'A_']]

    :return:
    """
    # if we've computed the data before, return it immediately
    filename = os.path.join(os.path.dirname(__file__), "smallgraphs_by_order.json")

    if os.path.exists(filename) and not force_rebuild:
        with open(filename, "r") as file:
            # the object_hook below converts string keys to int keys
            return json.load(
                file, object_hook=lambda d: {int(k): v for k, v in d.items()}
            )

    # otherwise compute smallgraphs
    path_to_smallgraphs = os.path.join(ISGCI_DIR, "smallgraphs.html")
    if not os.path.exists(path_to_smallgraphs):
        save_webpage_to_file(
            requests.compat.urljoin(BASE_URL, "smallgraphs.html"), path_to_smallgraphs
        )

    with open(path_to_smallgraphs) as data:
        soup = BeautifulSoup(data, features="html.parser")

    graphs_by_order = defaultdict(set)
    for graph_h4 in soup.find_all("h4"):
        if not graph_h4.text:  # skip empty sections, i.e. <h4></h4>
            continue

        # give up on configurations with no drawings
        if graph_h4.get("id") is not None and graph_h4.get("id").startswith("XC"):
            break  # and not continue: once we reach this section, all remaining configurations can be skipped

        # retrieve graph6 encoding
        g6string = graph_h4.find(class_="graph6").text.strip()

        # the graph name is everything before '<span class="graph6"'
        name = prettify_name(
            str(graph_h4.extract())[4:]
            .split('<span class="graph6">', maxsplit=1)[0]
            .strip()
        )

        # the first letter of the g6string is the order n of the graph; since
        # we are dealing with small graphs only, we know that this letter has
        # value n+63 (https://users.cecs.anu.edu.au/~bdm/data/formats.txt)
        graphs_by_order[ord(g6string[0]) - 63].add((name, g6string))

    # write LAD files **now**, because some of them need to be read by
    # missing_smallgraphs()
    for graphbunch in graphs_by_order.values():
        dump_graphs_to_lad_files(graphbunch)

    # get all smallgraphs that are missing from the above directory and update
    # return value
    for key, val in missing_smallgraphs().items():
        graphs_by_order[key].update(val)
        dump_graphs_to_lad_files(val)

    logging.info(
        "done, got %s smallgraphs", sum(len(val) for _, val in graphs_by_order.items())
    )

    # write graph to json for further uses
    with open(filename, "w") as file:
        json.dump(graphs_by_order, file, **__JSON_DUMP_ARGS)

    return graphs_by_order


def build_inclusion_graph(graph_dictionary: dict[int, set]) -> nx.DiGraph:
    """
    Returns the inclusion DAG of a graph dictionary, whose keys are the orders of our graphs and
    whose values are iterables of pairs (graph name: str, graph6 encoding: str).

    The inclusion DAG is defined by:
        - vertices: the graph names given in the input dictionary:
        - arcs: an arc (A, B) connects graph with name A to graph with name B if B is an induced
            subgraph of A

    Note: as of 2025-04-23, building the graph takes about 2 minutes on my machine.

    TODO explain that actually, we return the transitive closure of that graph.
        it will be faster to compute containment between pairwise levels only (i, i+1) but we need to make sure this is correct.

    :param graph_dictionary:
    :return:
    """
    inclusion_graph = nx.DiGraph()

    # sorting is not required for the process to work, I only use it for reproducibility
    graph_dictionary = {key: sorted(val) for key, val in graph_dictionary.items()}

    # convert all g6 strings to actual graph objects
    actual_graphs = dict()
    for graphbunch in graph_dictionary.values():
        for _, g6string in graphbunch:
            actual_graphs[g6string] = nx.from_graph6_bytes(g6string.encode())

    # some clarifications on the code below: to have networkx check whether G is an induced
    # subgraph of H, we ask whether a subgraph of H is isomorphic to G as follows:
    #
    #   matcher = GraphMatcher(H, G)
    #   if matcher.subgraph_is_isomorphic():
    #       ...
    #
    # we are computing containment relationships between all pairs of graphs of different order,
    # which will actually yield the transitive closure of the smallgraph inclusion graph
    with tqdm(
        total=sum(
            len(graph_dictionary[lower_order]) * len(graph_dictionary[higher_order])
            for lower_order, higher_order in combinations(sorted(graph_dictionary), 2)
        ),
        desc="Building smallgraph inclusion graph",
        unit=" pairs",
    ) as pbar:
        for lower_order, higher_order in combinations(sorted(graph_dictionary), 2):
            for smaller_graph_name, graph_1_g6 in graph_dictionary[lower_order]:
                inclusion_graph.add_node(smaller_graph_name)
                smaller_graph = actual_graphs[graph_1_g6]
                for larger_graph_name, graph_2_g6 in graph_dictionary[higher_order]:
                    inclusion_graph.add_node(larger_graph_name)
                    larger_graph = actual_graphs[graph_2_g6]
                    # if smaller_graph is an induced subgraph of larger_graph, add arc
                    # larger_graph_name -> smaller_graph_name
                    matcher = nx.algorithms.isomorphism.GraphMatcher(
                        larger_graph, smaller_graph
                    )
                    if matcher.subgraph_is_isomorphic():
                        inclusion_graph.add_edge(larger_graph_name, smaller_graph_name)
                    pbar.update()

    return inclusion_graph


def smallgraph_inclusion_graph(force_rebuild: bool = False) -> nx.DiGraph:
    """
    Returns the inclusion DAG of all smallgraphs in ISGCI.

    Note: takes between 3 and 4 minutes to build from scratch on my machine. I'm not looking for
    faster ways now since we'll only need to build it once.

    >>> smallgraph_inclusion_graph()

    :rtype: networkx.DiGraph
    :return:
    """
    # if we've computed the graph before, return it immediately
    filename = os.path.join(
        os.path.dirname(__file__), "smallgraph_inclusion_graph.json"
    )
    if os.path.exists(filename) and not force_rebuild:
        with open(filename, "r") as file:
            return nx.node_link_graph(json.load(file), edges="edges")

    # otherwise, compute it from scratch
    logging.info("building the smallgraphs inclusion graph... ")

    # retrieve all smallgraphs from ISGCI's list
    all_smallgraphs = all_smallgraphs_by_order()
    inclusion_graph = build_inclusion_graph(all_smallgraphs)

    # write graph to json for further uses
    with open(filename, "w") as file:
        print("done, dumping json data to", filename)
        json.dump(
            nx.node_link_data(inclusion_graph, edges="edges"), file, **__JSON_DUMP_ARGS
        )

    return inclusion_graph


def dump_graphs_to_lad_files(graphbunch: Iterable) -> None:
    """
    Dump each smallgraph to a separate LAD file in SMALLGRAPH_DIR.

    :type graphbunch: Iterable
    :return:
    """
    pathlib.Path(SMALLGRAPH_DIR).mkdir(exist_ok=True)
    for name, g6string in graphbunch:
        with open(os.path.join(SMALLGRAPH_DIR, name), "w") as output_file:
            output_file.write(g6string_to_lad(g6string))


def get_fiscky_classes(force_rebuild=False) -> list[dict]:
    """
    Returns all fiscky classes in ISGCI.

    >>> get_fiscky_classes()

    @return:
    """
    # if we've computed the data before, return it immediately
    filename = os.path.join(os.path.dirname(__file__), "fiscky_classes.json")

    if os.path.exists(filename) and not force_rebuild:
        with open(filename, "r") as file:
            return json.load(file)

    # otherwise, compute result, store it, then return it
    fiscky_classes = list()

    # 1) retrieve classes that have a FISC in local database
    class_files = os.listdir(PATHS["classes"])

    # TODO ugly, these names should be loaded from isgci_base.py which should load them itself
    #   move this bit to a function in isgci module
    for class_filename in tqdm(
        class_files, desc="Retrieving fiscky classes from local db", unit=" files"
    ):
        current_class = GraphClass(class_filename.split(".")[0])
        if current_class.fisc():
            fiscky_classes.append(current_class)

    # compute classes for which we can actually generate recognizers; the following keywords
    # describe generic families which cannot be recognized directly, so we discard them
    forbidden_substrings = {
        "building",
        "cycle",
        "even",
        "hole",
        "minor",
        "probe",
        "XC",
        "XF",
        "XZ",
        "n+",
    }
    fiscky_classes = [
        gc
        for gc in fiscky_classes
        if all(
            taboo not in word for word in gc.fisc() for taboo in forbidden_substrings
        )
    ]

    # second pass needed: exclude "sun" but not "rising sun" nor "co-rising sun"
    forbidden_words = ["co-sun", "odd co-sun", "odd-sun", "sun"]
    fiscky_classes = [
        gc
        for gc in fiscky_classes
        if all(word not in gc.fisc() for word in forbidden_words)
    ]

    # write data to json for further uses
    with open(filename, "w") as file:
        json.dump(
            fiscky_classes, file, cls=GraphClassEncoder, indent=4, sort_keys=True
        )  # don't add **__JSON_DUMP_ARGS)

    return fiscky_classes


def generate_recognizers() -> None:
    """
    Generates all recognizers for classes that can be recognised using fixed forbidden induced
    subgraphs. This does NOT include configurations like C_{n+4}, holes, XZ, etc.

    >>> generate_recognizers()

    :return:
    """
    # make backup if file exists
    filename = os.path.join(os.path.dirname(__file__), "generated_recognizers.py")
    if os.path.exists(filename):
        bakname = "".join(
            [filename, ".BAK.", datetime.today().strftime("%Y-%m-%d %H:%M:%S")]
        )
        print(
            f"{os.path.basename(filename)} already exists, backing it up to "
            f"{os.path.basename(bakname)}"
        )
        copyfile(filename, bakname)

    # generate the recognizers by increasing max pattern size
    with open(filename, "w") as output:
        # write module docstring and all necessary imports
        write_recognizer_module_header(output)

        # write recognizers
        output.write("# Recognizers ".ljust(WRAP_WIDTH - 1, "-") + "\n")

        smallgraph_names_and_orders = {
            name: k
            for k, graphbunch in all_smallgraphs_by_order().items()
            for name, *_ in graphbunch
        }

        partition = partition_by_pattern_max_size_then_number(
            get_fiscky_classes(), smallgraph_names_and_orders
        )

        pbar = tqdm(
            # sorted(partition),
            partition,
            total=sum(map(len, partition.values())),
            desc="Writing recognizers",
            unit=" functions",
        )
        for order, graphclass_list in sorted(partition.items()):
            message = (
                "# All recognizers for patterns on at most " + str(order) + " vertices "
            )
            output.write(message.ljust(WRAP_WIDTH - 1, "-") + "\n")
            for gc in graphclass_list:
                write_recognizer_code(output, gc, order, smallgraph_names_and_orders)
                pbar.update()

        # write RECOGNIZERS dictionary's initialization
        output.write(
            "# This code segment must always be at the END of a recognizer file ".ljust(
                WRAP_WIDTH - 2, "-"
            )
            + "\n"
        )
        output.write(
            "\n".join(
                [
                    "RECOGNIZERS = current_module_recognizers(",
                    '    ".".join([',
                    "        os.path.basename(os.path.dirname(__file__)),",
                    '        os.path.basename(__file__).removesuffix(".py")',
                    "    ])",
                    ")\n",
                ]
            )
        )

        output.write("# ".ljust(WRAP_WIDTH - 2, "-") + "\n")


def write_recognizer_module_header(output: TextIOWrapper) -> None:
    """
    Writes the header of a recognizer module file. This is only intended for automatically
    generated recognizers at the moment.

    :param output:
    :return:
    """
    # write module header ---------------------------------------------------------------------
    today = datetime.today()
    output.write(
        textwrap.fill('"""Anthony Labarre © ' + str(today.year), width=WRAP_WIDTH)
    )
    output.write("\n\n")
    output.write(
        textwrap.fill(
            f"This file was automatically generated by {os.path.basename(__file__)} on "
            f"{today}. It contains all recognizers for those graph classes in ISGCI that "
            f"admit a FISC (forbidden subgraph characterisation).",
            width=WRAP_WIDTH,
        )
    )
    output.write("\n\n")
    output.write(
        textwrap.fill(
            "recognizers are sorted first on the basis of the order of their largest pattern, "
            "then by number of patterns. Additionally, every pattern in a given set will be "
            "examined by increasing size.",
            width=WRAP_WIDTH,
        )
    )
    output.write("\n\n")
    output.write(
        textwrap.fill(
            'For now, only "fixed" subgraphs are taken into account. This excludes general '
            "configurations like C_{n+4}, XC, XZ, ...",
            width=WRAP_WIDTH,
        )
    )
    output.write("\n\n")
    output.write('"""\n')

    # write imports ---------------------------------------------------------------------------
    output.write(
        textwrap.fill("# Imports ".ljust(WRAP_WIDTH - 1, "-"), width=WRAP_WIDTH) + "\n"
    )
    output.write(
        textwrap.fill(
            "# ----- Standard imports ".ljust(WRAP_WIDTH - 1, "-"), width=WRAP_WIDTH
        )
        + "\n"
    )
    output.write("import os\n")
    output.write("from functools import lru_cache\n\n")

    output.write(
        textwrap.fill(
            "# ----- Third-party imports ".ljust(WRAP_WIDTH - 1, "-"),
            width=WRAP_WIDTH,
        )
        + "\n"
    )
    output.write("import networkx as nx\n\n")

    output.write(
        textwrap.fill(
            "# ----- My imports ".ljust(WRAP_WIDTH - 1, "-"), width=WRAP_WIDTH
        )
        + "\n"
    )
    output.write(
        "from graph_recognition.recognizers_utils import assign_class_id, "
        "current_module_recognizers\n"
    )
    output.write("from graph_recognition.subgraphs import is_h_free\n\n\n")


def write_recognizer_code(
    output: TextIOWrapper,
    gc: dict,
    order: int,
    smallgraph_names_and_orders: dict,
):
    """
    Writes the code of a recognizer for graph class gc to output.

    :return:
    """
    # write decorated function definition
    class_id = gc["class_id"]
    output.write('@assign_class_id("' + class_id + '")\n')
    output.write("@lru_cache(maxsize=None)\n")
    output.write("def is_" + class_id.lower() + "(graph: nx.Graph) -> bool:\n")

    # write function docstring
    output.write('    """\n')
    output.write(
        textwrap.fill(
            f"    Returns True iff graph is {prettify_name(gc['class_name']).replace(',', ', ')}.",
            width=WRAP_WIDTH,
            subsequent_indent="    ",
        )
    )
    output.write("\n")
    output.write(
        f"\n    See {requests.compat.urljoin(BASE_URL, 'classes/' + class_id)}\n"
    )
    output.write(f"\n    Complexity of naïve matching: O(n^{order})\n\n")
    output.write("    :type graph: nx.Graph\n")
    output.write('    """\n')

    # write actual code: a single call to is_h_free, with patterns sorted by size
    output.write(
        f"    return is_h_free(graph, {sorted(gc['fisc'], key=smallgraph_names_and_orders.get)})\n"
    )
    output.write("\n\n")


def store_graph(graph: nx.Graph, name: str, graph_dictionary: dict[int, Any]) -> None:
    """
    Stores the graph into the dictionary.

    :param name:
    :param graph:
    :param graph_dictionary:
    :return:
    """
    graph_dictionary[graph.number_of_nodes()].add(
        (name, nx.to_graph6_bytes(graph, header=False).decode().strip())
    )


def missing_smallgraphs() -> dict[int, Any]:
    """
    Writes the LAD files for some smallgraphs that appear in the FISC of some graph classes, or in
    various papers, but not on the smallgraphs page. The doctest below lists the names of the
    graphs that are generated:

    >>> graphs = missing_smallgraphs()
    # >>> print('\\n'.join(sorted(g.name for g in set.union(*graphs.values()))))
    >>> print('\\n'.join(sorted(name for name, *_ in set.union(*graphs.values()))))
    2K_{1,3}
    2K_{4}
    2P_{4}
    3K_{1}
    3K_{3}
    3P_{3}
    6K_{1}
    7K_{1}
    C_{6} U K_{1}
    K_{1,3} U C_{4}
    K_{1,5}
    K_{1,6}
    K_{3,3,3}
    K_{3,3}-e U K_{1}
    K_{3,4}
    K_{3,4}-e
    K_{3}
    K_{3} U C_{4}
    K_{3} U K_{4}
    K_{4,4}
    K_{6}
    K_{7}
    P_{8}
    W_{7}
    co(2P_{4})
    co(3P_{3})
    co(C_{4})
    co(C_{5})
    co(C_{6} U K_{1})
    co(K_{1,5})
    co(K_{3,3}-e U K_{1})
    co(K_{3,4}-e)
    co(P_{4})
    co(P_{8})
    co(S_{4})
    co(T_{3})
    co(W_{7})
    co(X_{160})
    co(X_{186})
    co(X_{202})
    co(X_{208})
    co(X_{57})
    co(X_{59})
    co(X_{81})
    co(domino U K_{1})
    co-bull
    co-star_{1,2,4}
    co-star_{1,2,5}
    domino U K_{1}
    friendship_{3}
    star_{1,2,4}
    star_{1,2,5}

    :return:
    """
    smallgraphs = defaultdict(set)
    os.chdir(SMALLGRAPH_DIR)

    # the following graphs are listed on ISGCI's smallgraphs page as self complementary; therefore,
    # no g6 string is provided for them, and they all_smallgraphs_by_order() will miss them, so we
    # have to provide their complements here if we need them: P_4, bull, C_{5}, S_{4}, X_{186},
    # X_{160}, X_{202}
    for filename in ("P_{4}", "C_{5}", "S_{4}", "X_{186}", "X_{160}", "X_{202}"):
        graph = lad_file_to_nx_graph(filename)
        store_graph(graph, "co(" + filename + ")", smallgraphs)
        shutil.copy(filename, "co(" + filename + ")")

    # apparently graphs with special names are complemented with co-... rather than co(...), so I'm
    # following ISGCI's conventions
    graph = lad_file_to_nx_graph("bull")
    store_graph(graph, "co-bull", smallgraphs)
    shutil.copy("bull", "co-bull")

    # co(C_{4}), co(C_{5})
    store_graph(nx.complement(nx.cycle_graph(4)), "co(C_{4})", smallgraphs)

    # cliques: K_{3}, K_{6}, K_{7} and empty graphs: 3K_{1}, 6K_{1}, 7K_{1}
    for k in [3, 6, 7]:
        store_graph(nx.complete_graph(k), "K_{" + str(k) + "}", smallgraphs)
        store_graph(nx.empty_graph(k), str(k) + "K_{1}", smallgraphs)

    # 2K_{4}
    store_graph(
        nx.disjoint_union(nx.complete_graph(4), nx.complete_graph(4)),
        "2K_{4}",
        smallgraphs,
    )

    # 3K_{3}
    graph = nx.disjoint_union(nx.complete_graph(3), nx.complete_graph(3))
    graph = nx.disjoint_union(graph, nx.complete_graph(3))
    store_graph(graph, "3K_{3}", smallgraphs)

    # K_{3} U K_{4}
    store_graph(
        nx.disjoint_union(nx.complete_graph(3), nx.complete_graph(4)),
        "K_{3} U K_{4}",
        smallgraphs,
    )

    # 2P_{4} and complement
    graph = nx.disjoint_union(nx.path_graph(4), nx.path_graph(4))
    store_graph(graph, "2P_{4}", smallgraphs)
    graph = nx.complement(graph)
    store_graph(graph, "co(2P_{4})", smallgraphs)

    # 3P_{3} and complement
    graph = nx.disjoint_union(nx.path_graph(3), nx.path_graph(3))
    graph = nx.disjoint_union(graph, nx.path_graph(3))
    store_graph(graph, "3P_{3}", smallgraphs)
    graph = nx.complement(graph)
    store_graph(graph, "co(3P_{3})", smallgraphs)

    # complete bipartite graphs: K_{1,5}, K_{3,4}, K_{4,4}
    for k, p in [(1, 5), (3, 4), (4, 4)]:
        store_graph(
            nx.complete_bipartite_graph(k, p),
            "K_{" + str(k) + "," + str(p) + "}",
            smallgraphs,
        )

    # K_{1,6}
    store_graph(nx.complete_bipartite_graph(1, 6), "K_{1,6}", smallgraphs)

    # co(K_{1,5})
    store_graph(
        nx.complement(nx.complete_bipartite_graph(1, 5)), "co(K_{1,5})", smallgraphs
    )

    # K_{3,3,3}
    store_graph(nx.complete_multipartite_graph(3, 3, 3), "K_{3,3,3}", smallgraphs)

    # the following smallgraphs can be constructed from known smallgraphs: their structure is
    # "graph U K_{1}" (and "co(graph U K_{1})"
    for filename in ("C_{6}", "domino", "K_{3,3}-e"):
        graph = lad_file_to_nx_graph(filename)
        graph.add_node(graph.number_of_nodes())
        store_graph(graph, filename + " U K_{1}", smallgraphs)
        store_graph(nx.complement(graph), "co(" + filename + " U K_{1})", smallgraphs)

    # the following smallgraphs are complement of known smallgraphs
    for filename in ("T_{3}", "X_{208}", "X_{57}", "X_{59}", "X_{81}"):
        store_graph(
            nx.complement(lad_file_to_nx_graph(filename)),
            "co(" + filename + ")",
            smallgraphs,
        )

    # K_{3,4}-e:
    graph = nx.complete_bipartite_graph(3, 4)
    graph.remove_edge(*(list(graph.edges)[0]))
    store_graph(graph, "K_{3,4}-e", smallgraphs)
    store_graph(nx.complement(graph), "co(K_{3,4}-e)", smallgraphs)

    # P_{8}
    graph = nx.path_graph(8)
    store_graph(graph, "P_{8}", smallgraphs)
    store_graph(nx.complement(graph), "co(P_{8})", smallgraphs)

    # W_{7}
    graph = nx.cycle_graph(7)
    graph.add_node(8)
    graph.add_edges_from((u, 8) for u in range(8))
    store_graph(graph, "W_{7}", smallgraphs)
    store_graph(nx.complement(graph), "co(W_{7})", smallgraphs)

    for i, j, k in [(1, 2, 4), (1, 2, 5)]:
        # build star_{i,j,k}
        # build the three paths
        graph = nx.disjoint_union(nx.path_graph(i), nx.path_graph(j))
        graph = nx.disjoint_union(graph, nx.path_graph(k))

        # add new node connected to each path
        new_node = graph.number_of_nodes()
        graph.add_node(new_node)
        graph.add_edge(0, new_node)  # connect to min of first path
        graph.add_edge(j, new_node)  # connect to first elem of second path
        graph.add_edge(new_node - 1, new_node)  # connect to max of last path

        # write both graphs
        store_graph(graph, "star_{" + ",".join(map(str, [i, j, k])) + "}", smallgraphs)
        store_graph(
            nx.complement(graph),
            "co-star_{" + ",".join(map(str, [i, j, k])) + "}",
            smallgraphs,
        )

    # 2K_{1,3}
    store_graph(
        nx.disjoint_union(nx.star_graph(3), nx.star_graph(3)), "2K_{1,3}", smallgraphs
    )

    # K_{3} U C_{4}
    store_graph(
        nx.disjoint_union(nx.complete_graph(3), nx.cycle_graph(4)),
        "K_{3} U C_{4}",
        smallgraphs,
    )

    # K_{1,3} U C_{4}
    store_graph(
        nx.disjoint_union(nx.star_graph(3), nx.cycle_graph(4)),
        "K_{1,3} U C_{4}",
        smallgraphs,
    )

    # friendship_{3}
    graph = nx.star_graph(6)
    graph.add_edges_from([(1, 2), (3, 4), (5, 6)])
    store_graph(graph, "friendship_{3}", smallgraphs)

    os.chdir(os.pardir)

    return smallgraphs


def main() -> None:
    """

    :return:
    """
    from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser

    parser = ArgumentParser(
        prog=os.path.basename(__file__),
        description="Utilities for smallgraphs.",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )

    # options
    parser.add_argument(
        "--generate-recognizers",
        action="store_true",
        help="generates and writes all recognizers based on smallgraphs to "
        "./generated_recognizers.py",
    )
    parser.add_argument(
        "--build-inclusion-graph",
        action="store_true",
        help="generates and writes the smallgraph inclusion graph to "
        "./smallgraph_inclusion_graph",
    )
    parser.add_argument(
        "--dump-g6",
        action="store_true",
        help="writes all smallgraphs to ./smallgraphs.g6",
    )

    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        parser.exit()

    if args.generate_recognizers:
        generate_recognizers()
        sys.exit()

    if args.build_inclusion_graph:
        # TODO ask for confirmation if exists
        smallgraph_inclusion_graph(force_rebuild=True)
        sys.exit()

    if args.dump_g6:
        output_path = "smallgraphs.g6"
        with open(output_path, "w") as output:
            print("Writing smallgraphs to", output_path, "... ", end="")
            for smallgraph_bunch in all_smallgraphs_by_order().values():
                for smallgraph in smallgraph_bunch:
                    output.write(smallgraph.g6 + "\n")
            print("done.")

    # TODO and then finally generate all recognizers
    """
    - generate all smallgraphs LADS
    - generate all missing smallgraph LADS
    - then we can generate the containment graph
    - generate actual code
    """


if __name__ == "__main__":
    main()
