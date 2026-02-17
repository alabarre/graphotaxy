"""
Anthony Labarre © 2020-2026

# TODO distribute package with a copy of isgci_db and pickled files and json files
    get rid of pickled files, only use json files for interoperability
# TODO LATER allow user to download and use his copy of the DB
# TODO file with timestamps

TODO BUGS:
    [ ]

TODO questions:
    [ ] proper naming scheme? should isgci_base.py be called __main__.py? isgci.py? ...
    [ ] and then should I import from isgci.stuff or just from stuff? (see other files)
    [ ] once everything works, follow Dane's book again

This module contains everything related to interacting with the ISGCI database from
https://www.graphclasses.org/ . You can:

    - download the full database as html files to your preferred TARGET_DIR:

            python3 -m isgci --download-db TARGET_DIR

    - obtain the inclusion graph of all classes in ISGCI as a json file (assuming a local copy of
        the database is available at SOURCE_DIR):

            python3 -m isgci --rebuild-graph SOURCE_DIR

    - find out whether and how two classes in ISGCI are related:

            python3 -m isgci --relation FIRST_ID SECOND_ID
"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
import json
import pickle
from collections import defaultdict
from itertools import product
from os import scandir
from os.path import basename, exists, join, isdir
from pathlib import Path
from shutil import rmtree
from sys import stdout
from textwrap import fill
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import urlopen

# ----- Non-standard imports ----------------------------------------------------------------------
from bs4 import BeautifulSoup
from html2text import html2text
from networkx import DiGraph, NetworkXNoPath, NodeNotFound, shortest_path
from networkx.drawing.nx_pydot import read_dot
from networkx.readwrite import json_graph
from tqdm import tqdm

try:
    import htmlmin

except ModuleNotFoundError:
    # htmlmin is not a hard requirement, so we let the import fail silently for now
    pass

# ----- My imports --------------------------------------------------------------------------------
from isgci.vars import ISGCI_DIR, PATHS, OPEN, ROOT
from isgci.functions import class_id_from_url, prettify_name
from isgci.graphclass import GraphClass

# Global variables --------------------------------------------------------------------------------
BASE_URL = "https://www.graphclasses.org/"
BASE_CLASS_URL = urljoin(BASE_URL, "classes/")
HTMLMIN_SETTINGS = {
    "remove_comments": True,
    "remove_empty_space": True,
    "remove_all_empty_space": False,
    "reduce_empty_attributes": True,
    "reduce_boolean_attributes": True,
    "remove_optional_attribute_quotes": True,
    "convert_charrefs": True,
    "keep_pre": False,
    "pre_tags": ("pre", "textarea"),
    "pre_attr": "pre",
}


# Functions ---------------------------------------------------------------------------------------
def download_isgci(target_dir: str) -> None:
    """Downloads the public version of the database available at https://www.graphclasses.org/ as
    webpages to the subdirectory ./isgci_db/, storing classes in ./isgci_db/classes/ .

    :param target_dir: the directory in which the database must be stored.
    :returns: None
    """
    if target_dir != ISGCI_DIR:
        target_dir = join(target_dir, basename(ISGCI_DIR))

    # if target_dir is not empty, we might be mixing old and new files and get a corrupt db; to
    # avoid that, remove it and recreate it
    if isdir(target_dir):
        with scandir(target_dir) as it:
            if any(it):
                print(
                    fill(
                        f"Found nonempty directory {target_dir}, removing it to avoid building a "
                        "corrupted database.",
                        width=80,
                    )
                )
                rmtree(target_dir)

    Path(target_dir).mkdir(exist_ok=True)

    print("Downloading the classes directory... ", end="")
    stdout.flush()
    save_webpage_to_file(
        urljoin(BASE_URL, "classes.cgi"), join(target_dir, "classes.cgi")
    )
    print("done.")

    with open(join(target_dir, "classes.cgi")) as data:
        # retrieve the list of all classes
        all_classes = BeautifulSoup(data, features="html.parser").find_all(
            "span", {"class": "graphclass"}
        )
        # download each individual file
        Path(join(target_dir, "classes")).mkdir(exist_ok=True)
        for elem in tqdm(all_classes, desc="Downloading classes", unit=" files"):
            name = elem.find("a").get("href")
            save_webpage_to_file(
                "".join([BASE_URL, name]),
                join(target_dir, "classes", class_id_from_url(name) + ".html"),
            )


def save_webpage_to_file(url: str, local_path: str) -> None:
    """Retrieves the contents of the webpage located at url and saves them to
    the file pointed to by local_path.

    If the package htmlmin is installed, the resulting pages will take up less
    space on disk; but it is not essential to this function's work.

    :param url: the source of the webpage to save
    :param local_path: its destination on disk
    :returns: None.
    """
    try:
        with urlopen(url) as resource:
            soup = BeautifulSoup(resource, features="html.parser")
            with open(local_path, "w", encoding="utf-8") as file:
                try:
                    data = htmlmin.minify(str(soup), **HTMLMIN_SETTINGS)
                except NameError:
                    # htmlmin was not loaded because it was not found: retrieve data normally
                    print(
                        fill(
                            "Warning: htmlmin not found. I can work without it so you can safely "
                            "ignore this warning, but consider installing it to decrease the size "
                            "of the files I will download.",
                            width=80,
                        )
                    )
                    data = str(soup)
                file.write(data)

    except HTTPError:  # TODO what's this error? how to handle it?
        return
    except URLError:
        raise URLError("could not open " + url + ", are you offline?")


def reduced_isgci_inclusion_graph(
    source_dir: str = ISGCI_DIR, force_rebuild: bool = False
) -> DiGraph:
    """Returns the inclusion graph of all classes known to ISGCI: its vertices are the classes in
    ISGCI, and an arc connects two classes whenever one is a minimal superclass of the other. Each
    vertex receives the following additional fields:

        - "id": the class id in ISGCI
        - "name": the class name in ISGCI
        - "category": set to OPEN
        - "reason": empty if the graph class can be recognized in polynomial time; its recognition
            status otherwise
        - "color": set to "DarkGray",

    :param source_dir: the directory where data should be read from; will also be the target
    directory if data needs to be written.
    :param force_rebuild: if True, rebuild the whole graph even if it exists (default: False)
    :returns: the ISGCI inclusion graph

    """
    if source_dir != ISGCI_DIR:
        filename = join(source_dir, basename(PATHS["isgci_inclusion_graph"]))
        source_dir = join(source_dir, basename(ISGCI_DIR))

    else:
        filename = PATHS["isgci_inclusion_graph"]

    # if we've computed the graph before, return it immediately
    if exists(filename) and not force_rebuild:
        with open(filename, "r") as file:
            return json_graph.node_link_graph(json.load(file), edges="edges")

    # otherwise, build the graph, and save it for future runs
    message = [
        "\nThe basic ISGCI inclusion graph was not found, please wait while I build it (this only "
        "needs to be done once)",
        "Forcing the reconstruction of the basic ISGCI inclusion graph",
    ][force_rebuild]
    print(fill(message, width=80))
    result = DiGraph()
    with open(join(source_dir, "classes.cgi")) as data:
        all_classes = BeautifulSoup(data, features="html.parser").find_all(
            "span", {"class": "graphclass"}
        )

    for elem in tqdm(all_classes, desc="Building graph", unit=" nodes"):
        link = elem.find("a")
        class_id = class_id_from_url(link.get("href"))
        try:
            vertex_data = GraphClass(join(source_dir, "classes", class_id))
        except FileNotFoundError:
            print(
                f"ERROR: missing file {join(source_dir, 'classes', class_id)}, aborting"
            )
            print("Please download the database again")
            exit(-1)

        recognition_status = vertex_data.recognition_status()
        # add node as 'open' and corresponding edges
        result.add_node(
            class_id,
            name=prettify_name(vertex_data.class_name()),
            category=OPEN,
            reason=""
            if recognition_status in {"Linear", "Polynomial"}
            else recognition_status,
            color="DarkGray",
        )
        result.add_edges_from(product([class_id], vertex_data.maximal_subclasses()))
        result.add_edges_from(product(vertex_data.minimal_superclasses(), [class_id]))

    for vertex in tqdm(
        list(result.nodes()), desc="Removing duplicate nodes", unit=" nodes"
    ):
        # checks here and below are mandatory since we are working on a
        # graph from which we are removing nodes
        if vertex in result:
            for eq_id in GraphClass(
                join(source_dir, "classes", vertex)
            ).equivalent_classes():
                if eq_id in result:
                    result.remove_node(eq_id)

    with open(filename, "w") as output:
        # noinspection PyTypeChecker
        json.dump(
            json_graph.node_link_data(result, edges="edges"),
            output,
            default=list,
            indent=4,
            sort_keys=True,
        )

    print(
        "Wrote graph with",
        result.number_of_nodes(),
        "open nodes and",
        result.number_of_edges(),
        "arcs to",
        filename,
    )

    return result


def isgci_exclusion_graph() -> DiGraph:
    """
    Returns an exclusion digraph based on a subset of classes known to ISGCI: its vertices are the
    classes in ISGCI, and an arc connects a class A to a class B if being a member of A implies NOT
    being a member of B.
    """
    # simply read data from a file and return it
    return DiGraph(read_dot(join(ROOT, "exclusion-graph.dot")))


def compute_class_equivalences(metagraph: DiGraph) -> defaultdict[str, set]:
    """
    Returns a dictionary indexed by class id's, whose values contain all
    corresponding equivalent classes as 2-tuples (name, id) sorted by name.

    @return: a dictionary
    @rtype: dict
    @param metagraph: an inclusion graph of graph classes.
    """
    equivalences = defaultdict(set)
    for node in tqdm(
        metagraph.nodes(), desc="Building equivalence dictionary", unit=" nodes"
    ):
        # store the classes that are equivalent to the current node
        equivalences[node].update(
            (html2text(GraphClass(class_id).class_name()), class_id)
            for class_id in GraphClass(node).equivalent_classes()
        )
        # update the equivalence classes of each equivalent name
        current_name = html2text(GraphClass(node).class_name())
        for eq_name, eq_id in equivalences[node]:
            equivalences[eq_id].update(
                equivalences[node]
                .difference({(eq_name, eq_id)})
                .union({(current_name, node)})
            )

    return equivalences


def isgci_equivalences(force_rebuild: bool = False) -> defaultdict[str, set]:
    """Returns the dictionary of all class equivalences known to ISGCI.

    @return:
    @param force_rebuild: if True, rebuild the dictionary even if it already exists (default: False)
    @rtype: dict
    """
    filename = PATHS["isgci_equivalences"]  # TODO switch to json

    # if we haven't computed equivalences before, do it and save them for
    # future uses
    if not exists(filename) or force_rebuild:
        graph = reduced_isgci_inclusion_graph()
        # print("Computing class equivalences ... ", end="")
        stdout.flush()
        with open(filename, "wb") as file:
            result = compute_class_equivalences(graph)
            pickle.dump(result, file, pickle.HIGHEST_PROTOCOL)

        # print("done.")
        print("Wrote dictionary with", len(result), "keys to", filename)

    # return the pre-computed result
    # TODO ok works but let's make the names readable (html_to_utf8)
    with open(filename, "rb") as file:
        return pickle.load(file)


# TODO provide command line argument to call this
def isgci_ids_to_names() -> defaultdict[str, str]:
    """Returns a dictionary mapping each ISGCI id to the corresponding class name.

    @return:
    @rtype: dict
    """
    filename = PATHS["isgci_ids_to_names"]

    # if we haven't computed equivalences before, do it and save them for
    # future uses
    if not exists(filename):
        # parse all downloaded files and build the mapping id -> name
        mapping = dict()
        with open(join(ISGCI_DIR, "classes.cgi")) as data:
            soup = BeautifulSoup(data, features="html.parser")
            all_classes = soup.find_all("span", {"class": "graphclass"})
            for elem in tqdm(
                all_classes, desc="Gathering all ids and names", unit=" class"
            ):
                link = elem.find("a")
                class_id = class_id_from_url(link.get("href"))
                vertex_data = GraphClass(class_id)
                mapping[vertex_data.class_id()] = vertex_data.class_name()

        # store result in file
        with open(filename, "w") as output:
            json.dump(mapping, output, default=list, indent=4, sort_keys=True)

    # return stored result
    with open(filename) as data:
        return json.load(data)


def relation(first_id: str, second_id: str) -> str | list[str]:
    """
    Determines whether classes identified by first_id and second_id are related. Depending on the
    answer, the result may be:

        - a list [id_1, id_2, ..., id_k] of k class ids, which represents a shortest path from id_1
          to id_k in the ISGCI inclusion graph; each node starting from id2 is therefore a maximal
          subclass of the previous node. Note that the path might go either way (from id_1=first_id
          to id_k=second_id, or from id1=second_id to id_k=first_id).
        - "equivalent", if first_id is (an id equivalent to) second_id;
        - "complementary", if first_id is the complement of second_id;
        - or None if no relationship could be identified.

    @rtype: str | list[str]
    @param first_id:
    @param second_id:
    @return:

    >>> relation("gc_43", "gc_953")  # planar and co-planar
    'complementary'
    >>> relation("gc_151", "gc_151")  # cograph and cograph (not a typo, class is self-complementary)
    'complementary'
    >>> relation("gc_43", "gc_955")  # planar and coin
    'equivalent'
    >>> len(relation("gc_741", "gc_43")[0])  # planar and "grandfather" string
    3
    """
    equivalences = isgci_equivalences()

    # check whether given ids correspond to equivalent classes
    if first_id in (equiv for _, equiv in equivalences[second_id]):
        return "equivalent"

    # check whether classes are complementary
    if second_id in GraphClass(first_id).complement_classes():
        return "complementary"

    # nonequivalent classes: check that they are both known under the given
    # ids, or replace them with equivalent ids before proceeding
    inclusions = reduced_isgci_inclusion_graph()
    received_ids = [first_id, second_id]
    for i, node_id in enumerate(received_ids):
        if node_id not in inclusions:
            for _, equiv_id in equivalences[node_id]:
                if equiv_id in inclusions:
                    received_ids[i] = equiv_id
                    break
            else:
                raise NodeNotFound(node_id + " unknown, even with equivalences")

    # check whether first_id is an ancestor of second id, or conversely
    # return orientation as well: since we're trying both ways, a path does not tell us which
    # way to follow
    for direction in (-1, 1):
        first, second = received_ids[::direction]
        try:
            return shortest_path(inclusions, first, second), direction
        except NetworkXNoPath:
            pass

    return [], None  # no path found


def main() -> None:
    """Standalone mode, allows the following actions:

        --download-db:      downloads the ISGCI database
        --rebuild-graph:    rebuilds the graph class inclusion graph
        --relation:         prints how the given classes are related"

    @rtype: None
    """
    # set up the option parser
    from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser

    parser = ArgumentParser(
        prog=basename(__file__),
        description="Interact with the ISGCI database.",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )

    # options
    parser.add_argument(
        "--download-db",
        nargs="?",
        action="store",
        const=ISGCI_DIR,
        help="downloads the ISGCI database to the provided target directory",
    )

    parser.add_argument(
        "--rebuild-graph",
        nargs="?",
        action="store",
        const=ISGCI_DIR,
        help="rebuilds the graph class inclusion graph from the ISGCI database stored in the "
        "provided target directory",
    )

    parser.add_argument(
        "--relation",
        nargs=2,
        help="prints how the given classes are related",
    )

    args = parser.parse_args()

    if args.download_db:
        download_isgci(args.download_db)

    elif args.rebuild_graph:
        reduced_isgci_inclusion_graph(args.rebuild_graph, force_rebuild=True)

    elif args.relation:
        path, *direction = relation(*args.relation)
        if not path:
            print(f"classes are unrelated")
        else:
            if isinstance(direction[0], str):  # TODO very ugly quick fix
                print("".join([path] + direction))
            else:
                direction = direction[0]
                if direction > 0:
                    # show equivalences TODO do that in relation function
                    for i in (-1, 0):
                        if args.relation[i] != path[i]:
                            path[i] = " = ".join([args.relation[i], path[i]])
                else:
                    # show equivalences TODO do that in relation function
                    if args.relation[-1] != path[0]:
                        path[0] = " = ".join([args.relation[-1], path[0]])
                    if args.relation[0] != path[-1]:
                        path[-1] = " = ".join([args.relation[0], path[-1]])
                print("\n ↓ \n".join(path[::]))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
