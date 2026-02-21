"""
Anthony Labarre © 2023-2026

Test generator for recognizers.

Since specific datasets are relatively rare, for each graph class for which we have data, we
generate tests that cover the corresponding recognizer as well as all available recognizers for
that class's ancestors.

You only need to run this program when:

    - the set of all available recognizers changes, i.e., a new recognizer is added and enabled by
      decorating it with @assign_class_id, or an existing recognizer is removed or disabled by
      removing the @assign_class_id decoration;

    - a new dataset is added to PROJECT_ROOT/tests/test_data;

    - the inclusion relationships in ISGCI change;

    - the exclusion relationships in ISGCI change.

The set of tests will not change if existing and enabled recognizers are merely modified, so there
is no need to run this program in those cases: you can simply run existing tests to check the
impact of your modifications.

All tests are written in PROJECT_ROOT/tests, and generated using datasets located in
PROJECT_ROOT/tests/test_data .

To generate new tests: in PROJECT_ROOT/src, run:

$ python3 generate_tests

To run all tests: in PROJECT_ROOT, run:

$ python3 -m unittest

To run a specific test: in PROJECT_ROOT, run:

$ python3 -m unittest tests/WANTED_TEST_FILE.py

Test generation process
-----------------------



TODO works, but far from presentable. explain how all these tests are generated
TODO much better documentation
TODO encapsulate what I can in a class rather than using these global variables

"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
import datetime
import os
import subprocess
import sys
import textwrap
from collections.abc import Callable
from typing import TextIO, Dict, Iterable

# ----- Non-standard imports ----------------------------------------------------------------------
import networkx
from tqdm import tqdm

# ----- My imports --------------------------------------------------------------------------------
from graph_analyzer import GraphAnalyzer
from isgci.isgci_base import (
    reduced_isgci_inclusion_graph,
    isgci_equivalences,
    BASE_CLASS_URL,
    isgci_exclusion_graph,
)

# Globals -----------------------------------------------------------------------------------------
EQUIV_IDS = {
    class_id: {alt_id for _, alt_id in equiv_ids}
    for class_id, equiv_ids in isgci_equivalences().items()
}
EXCLUSION_GRAPH = isgci_exclusion_graph()
ISGCI_GRAPH = reduced_isgci_inclusion_graph()
TEST_OUTPUT_DIR = os.path.join(os.pardir, "tests")
TEST_DATA_DIR = os.path.join(TEST_OUTPUT_DIR, "test_data")
WRAP_WIDTH = 100
TEST_COVERAGE = {"positive": set(), "negative": set()}


# Functions ---------------------------------------------------------------------------------------
def all_recognizable_class_ids_to_recognizers() -> Dict[str, Callable]:
    """
    Returns a dictionary with class ids as keys and a corresponding recognizer for each class id.
    Only recognizers which are actually loaded by the system are taken into account, and therefore
    unrecognizable classes will be missing from the dictionary

    @return:
    """
    # load all classes with the corresponding recognizers
    base_dict = {
        class_id: recognizer for class_id, recognizer in GraphAnalyzer().recognizers
    }
    # for each class with an id equivalent to a recognizable class: map it to the same recognizer
    # as its equivalent class
    for class_id in set(base_dict).intersection(EQUIV_IDS):
        for equiv_id in EQUIV_IDS[class_id]:
            base_dict[equiv_id] = base_dict[class_id]

    return base_dict


def __ancestors_or_descendants_of_some_equivalent_class(
        graph: networkx.Graph, class_id: str, function: Callable
) -> set[str]:
    """
    Returns the ancestors or the descendants of node with label class_id in graph. If that node is
    missing, looks for an equivalent node instead.

    @param graph:
    @param class_id:
    @return:
    """
    # if graph contains class, return its ancestors / descendants
    if class_id in graph:
        return function(graph, class_id)

    # otherwise, return the ancestors / descendants of an equivalent class
    for eq_id in EQUIV_IDS[class_id]:
        if eq_id in graph:
            return function(graph, eq_id)

    # otherwise something is very wrong, raise exception
    raise networkx.exception.NetworkXError(
        f"The node {class_id} is not in the {type(graph)}, and neither are any of its equivalent "
        f"classes."
    )


def ancestors_of_some_equivalent_class(
        graph: networkx.Graph, class_id: str
) -> set[str]:
    """
    Returns the ancestors of node with label class_id in graph. If that node is missing, looks for
    an equivalent node instead.

    @param graph:
    @param class_id:
    @return:
    """
    return __ancestors_or_descendants_of_some_equivalent_class(
        graph, class_id, networkx.ancestors
    )


def descendants_of_some_equivalent_class(
        graph: networkx.Graph, class_id: str
) -> set[str]:
    """
    Returns the descendants of node with label class_id in graph. If that node is missing, looks for
    an equivalent node instead.

    @param graph:
    @param class_id:
    @return:
    """
    return __ancestors_or_descendants_of_some_equivalent_class(
        graph, class_id, networkx.descendants
    )


def test_method(
        class_id: str, recognizer: Callable, base_id: str = "", kind: str = "positive"
) -> str:
    """
    Returns a test method for the recognizer for class_id. base_id is an optional placeholder for a
    descendant of class_id that led to the writing of this test method.

    kind specifies whether the test methods should test positive instances or not; the default
    behavior is to test positive instances, which results in a call to assertTrue. If kind is set
    to "negative", then we are testing negative instances, which results in a call to assertFalse.

    @param class_id:
    @param recognizer:
    @return:
    """
    assert kind in {"positive", "negative"}
    code_string = f'''
    def test_{class_id}(self) -> None:
        """Tests {kind} instances for class {class_id}.'''
    if base_id:
        if "excluded" in base_id:
            code_string += f" {class_id} is a descendant of {base_id}."
        else:
            code_string += f" {class_id} is an ancestor of {base_id}."
    code_string += f'''"""
        print(
            self._testMethodName.join("[]"), "testing", len(self.positive), "graphs", end=" "
        )
        sys.stdout.flush()
        
        # looping over enumerate so we can print failed instances
        for num, graph in enumerate(self.positive):
            self.{["assertFalse", "assertTrue"][kind == "positive"]}(
                {recognizer.__module__}.{recognizer.__name__}(graph), 
                "failed on graph number " + str(num) + " / " + str(len(self.positive)) + 
                " with node set " + str(graph.nodes) + " and edge set " + str(graph.edges)
            )

        print("done.")\n'''

    return code_string


def retrieve_all_classes_with_datasets() -> Dict[str, str]:
    """
    Returns a dictionary with entries of the form (class_id, path_to_dataset), obtained by
    exploring TEST_BASEDIR non-recursively. Only subdirectories that follow the naming convention
    ANY_TEXT=SINGLE_ISGCI_ID are considered.

    @return:
    """
    testable_classes = dict()
    for subdir in os.listdir(TEST_DATA_DIR):
        _, *class_id_list = subdir.split("=")
        testable_classes.update({cid: subdir for cid in class_id_list})

    return testable_classes


def ancestors_or_equivalent(
        classes: Dict[str, str], recognizers: Dict[str, Callable]
) -> Dict[str, set[str]]:
    """
    Returns a dictionary mapping each input class to its ancestors in the ISGCI graph. If a class
    is not found, then an equivalent id is used.

    @param testable_classes:
    @param recognizers:
    @return:
    """
    ancestors = dict()
    for class_id in classes:
        # retrieve all ancestors of class_id (or an equivalent class in ISGCI_GRAPH if need be)
        class_ancestors = ancestors_of_some_equivalent_class(ISGCI_GRAPH, class_id)

        # map class_id to these ancestors, as well as to all classes equivalent to class_id
        ancestors[class_id] = class_ancestors
        if class_id in EQUIV_IDS:
            for eq_id in EQUIV_IDS[class_id]:
                ancestors[eq_id] = class_ancestors

    return ancestors


def descendants_or_equivalent(classes: Dict[str, str]) -> Dict[str, set[str]]:
    """
    Returns a dictionary mapping each input class to its descendants in the ISGCI graph. If a class
    is not found, then an equivalent id is used.

    @param testable_classes:
    @param recognizers:
    @return:
    """
    descendants = dict()
    for class_id in classes:
        # retrieve all descendants of class_id (or an equivalent class in ISGCI_GRAPH if need be)
        class_descendants = descendants_of_some_equivalent_class(ISGCI_GRAPH, class_id)

        # map class_id to these descendants, as well as to all classes equivalent to class_id
        descendants[class_id] = class_descendants
        if class_id in EQUIV_IDS:
            for eq_id in EQUIV_IDS[class_id]:
                descendants[eq_id] = class_descendants

    return descendants


def testable_descendants_of_testable_classes(
        testable_classes: Dict[str, str], recognizers: Dict[str, Callable]
) -> Dict[str, Callable]:
    """
    Returns a dictionary of descendants of all testable classes, along with the corresponding
    recognizers if they exist.

    @param testable_classes:
    @param recognizers:
    @return:
    """
    descendants = dict()
    for testable_id in testable_classes:
        # gather all descendants of the given testable class
        class_descendants = descendants_of_some_equivalent_class(
            ISGCI_GRAPH, testable_id
        )
        descendants[testable_id] = class_descendants
        if testable_id not in recognizers:
            match = EQUIV_IDS[testable_id] & set(recognizers)
            if match:
                for m in match:
                    if class_descendants:
                        descendants[m] = class_descendants

    return descendants


def setupclass_method(class_id: str, path: str) -> str:
    """
    Returns a string containing the setupClass method for the unittest class that will test
    class_id.

    :type class_id: str
    :type path: str
    :return:
    """
    code_string = "    @classmethod\n"
    code_string += "    def setUpClass(self) -> None:\n"
    code_string += '        """Stores positive and negative instances to test."""\n'
    code_string += f"        super(Test_{class_id}_and_ancestors, self).setUpClass()\n"
    code_string += "        self.positive = []\n"
    code_string += f'        basedir = "{os.path.join(TEST_DATA_DIR.replace(os.pardir, os.curdir), path)}"\n'
    code_string += (
        '        print(self.__qualname__.join("[]"), "initializing positive instances '
        'from", basedir, "...", end=" ")\n'
    )
    code_string += "        sys.stdout.flush()\n"
    # the slice below limits test to 5 files in order to keep the running times reasonable
    code_string += (
        "        for dataset in sorted(os.listdir(basedir), key=lambda x: "
        "os.stat(os.path.join(basedir, x)).st_size)[:5]:\n"
    )
    code_string += '            if dataset.endswith(".g6"):\n'
    code_string += (
        "                data = networkx.read_graph6(os.path.join(basedir, dataset))\n"
    )
    code_string += '            elif dataset.endswith(".s6"):\n'
    code_string += (
        "                data = networkx.read_sparse6(os.path.join(basedir, dataset))\n"
    )
    code_string += "            else:\n"
    code_string += "                continue\n"
    code_string += "            if not isinstance(data, list):\n"
    code_string += "                data = [data]\n"
    code_string += "            self.positive.extend(data)\n"
    code_string += '        print("done.")\n'

    return code_string


def prepare_code_string(
        class_id: str,
        path: str,
        recognizers: Iterable[Callable],
        ancestors: Dict[str, str],
        descendants: Dict[str, str],
) -> str:
    """
    Returns the code string for testing class_id and its ancestors. This code is intended to be
    written to a test file that can later be loaded with unittest.

    @param class_id:
    @param path:
    @param recognizers:
    @param ancestors:
    @return:
    """
    # code cannot be written directly, because necessary imports must be written at the beginning
    # of the file and are not known before we start; therefore, we:
    #
    #   1. write the test code to code_string,
    #   2. gather all necessary imports as we go,
    #   3. prepend code_string with those imports and then return it

    # 1. write the test code: this is a class that inherits from unittest.TestCase, and whose
    # methods will each correspond to testing either class_id or one of its ancestors, provided
    # that that ancestor has not been tested yet and that a corresponding recognizer is available.
    code_string = f"class Test_{class_id}_and_ancestors(unittest.TestCase):\n"
    code_string += (
            textwrap.fill(
                f'    """A generic test case for class {class_id} and all its ancestors that have not '
                f'already been covered by other tests."""',
                width=WRAP_WIDTH,
                subsequent_indent="    ",
            )
            + "\n"
    )

    # write the setUpClass method, which initializes all data once for all tests in the class
    code_string += setupclass_method(class_id, path)

    # 2: write test for class_id or an equivalent class, as well as all its ancestors; this is also
    # where we gather all necessary imports as we go, since recognizers need to be imported from
    # their modules when running the tests
    standard_imports = ["os", "sys", "unittest"]
    other_imports = {"networkx"}

    # 2.1: write positive test for class_id if possible and not done in another file
    if class_id in recognizers and class_id not in TEST_COVERAGE["positive"]:
        code_string += f"# Generated test for base class {class_id}:"
        code_string += test_method(class_id, recognizers[class_id])
        other_imports.add(recognizers[class_id].__module__)
        # print(f"    wrote positive test for {class_id}")
        TEST_COVERAGE["positive"].add(class_id)

    else:
        code_string += (
            f"# No recognizer was found for class {class_id} or any equivalent class, so no \n"
            f"# test could be generated for that specific class\n"
        )

    # 2.2: write positive tests for ancestors of class_id
    code_string += f"# Generated tests for ancestors of base class {class_id}:"
    for anc_id in ancestors[class_id]:
        # generate test for ancestor class if it is recognizable and not done already
        if anc_id in recognizers and anc_id not in TEST_COVERAGE["positive"]:
            code_string += test_method(anc_id, recognizers[anc_id], class_id)
            other_imports.add(recognizers[anc_id].__module__)
            # print(f"    wrote positive test for ancestor {anc_id} of {class_id}")
            TEST_COVERAGE["positive"].add(anc_id)

    # 2.3: write negative tests for classes excluded by class_id, as well as for their descendants
    if class_id in EXCLUSION_GRAPH:
        for excluded in EXCLUSION_GRAPH.successors(class_id):
            if excluded in recognizers and excluded not in TEST_COVERAGE["negative"]:
                # by definition, a member of class_id is NOT a member of excluded, so we generate
                # a negative test method for that class ...
                code_string += test_method(
                    excluded, recognizers[excluded], kind="negative"
                )
                other_imports.add(recognizers[excluded].__module__)
                # print(f"    wrote negative test for exclusion {excluded} of {class_id}")
                TEST_COVERAGE["negative"].add(excluded)

            # whether or not excluded is recognizable, no member of excluded can be a member of its
            # descendants; generate tests for those classes too
            # print(descendants)
            for des_id in descendants[excluded]:
                # generate negative test for ancestor class if it is recognizable
                if des_id in recognizers and des_id not in TEST_COVERAGE["negative"]:
                    code_string += test_method(
                        des_id,
                        recognizers[des_id],
                        base_id=f"excluded class {excluded}",
                        kind="negative",
                    )
                    other_imports.add(recognizers[des_id].__module__)
                    # print(f"        wrote negative test for descendant {des_id} of {excluded}")
                    TEST_COVERAGE["negative"].add(des_id)

    # 3. prepend code_string with the necessary imports and return it
    code_string = (
            "# Imports ".ljust(WRAP_WIDTH - 1, "-")
            + "\n"
            + "\n".join(
        "import " + module
        for module in standard_imports
        # the following sort ensures third-party modules are imported before mine
        + sorted(
            other_imports,
            key=lambda mod: "site-packages" not in sys.modules[mod].__file__
                            and "dist-packages" not in sys.modules[mod].__file__,
        )
    )
            + "\n\n\n"
            + code_string
    )

    return code_string


def write_module_header(outfile: TextIO, class_id: str) -> None:
    """
    Writes a header for the test module for class_id and its ancestors.

    @param outfile:
    @param class_id:
    @return:
    """
    today = datetime.date.today()
    outfile.write(
        textwrap.fill('"""Anthony Labarre © ' + str(today.year), width=WRAP_WIDTH)
        + "\n\n"
    )
    outfile.write(
        textwrap.fill(
            f"This file was automatically generated by {os.path.basename(__file__)} on {today}. "
            f"It consists of a test suite for recognizers that identify {class_id} and a number "
            f"of related classes. Specifically, **if** the required recognizers are available, "
            "the test suite should contain:",
            width=WRAP_WIDTH,
        )
        + "\n\n"
    )
    outfile.write(f"    - a positive test for {class_id};\n")
    outfile.write(
        f"    - a positive test for each recognizable ancestor of {class_id};\n"
    )
    outfile.write(f"    - a negative test for each class excluded by {class_id};\n")
    outfile.write(
        f"    - and a negative test for each descendant of each class excluded by {class_id}.\n\n"
    )
    outfile.write(
        textwrap.fill(
            "Depending on which recognizers have been implemented and which representative of "
            "set of equivalent class has been chosen, some class ids may have been substituted "
            "with equivalent ids according to ISGCI.",
            width=WRAP_WIDTH,
        )
        + "\n\n"
    )

    outfile.write(
        textwrap.fill(
            "Some of the ancestors may have been purposefully omitted from this file, either in "
            "order to avoid duplicating tests or because the needed recognizers were missing.",
            width=WRAP_WIDTH,
        )
        + "\n\n"
    )
    outfile.write(
        textwrap.fill(
            f"Check {os.path.join(BASE_CLASS_URL, class_id)} for more information.",
            width=WRAP_WIDTH,
        )
        + "\n"
    )
    outfile.write('"""\n')


def generate_all_test_files() -> None:
    """
    Generates test files for all classes for which we have a test dataset, as well as for all their
    ancestors.

    @return:
    """
    # 1. retrieve all classes for which we have a test dataset; this does NOT mean that we have a
    #    recognizer for each such class
    all_classes_with_datasets = retrieve_all_classes_with_datasets()
    print(f"Found {len(all_classes_with_datasets)} classes with datasets")

    # 2. retrieve all ancestors of these classes, in order to generate tests for the corresponding
    #    recognizers using the base test dataset
    all_recognizers = all_recognizable_class_ids_to_recognizers()
    ancestors = ancestors_or_equivalent(all_classes_with_datasets, all_recognizers)
    descendants = descendants_or_equivalent(set(ISGCI_GRAPH.nodes), all_recognizers)
    # print(f"Found {len(ancestors)} ancestors of these classes")

    # generate actual code; each class with id class_id for which we have a dataset yields a file
    # named test_class_id_or_ancestors.py, which contains tests for the base class (if we have a
    # recognizer) as well as for all ancestors
    for class_id, path in tqdm(
            all_classes_with_datasets.items(), desc="Generating test files", unit=" files"
    ):
        generate_test_file(class_id, path, all_recognizers, ancestors, descendants)


def generate_test_file(
        class_id: str, path: str, recognizers: Dict[str, Callable], ancestors: dict,
        descendants: dict
) -> None:
    """
    Generates a test file for a given class_id. A test file contains a class derived from
    unittest.TestCase, which loads positive instances from the datafiles stored in
    TEST_DATA_DIR/XXX=class_id . Methods in that class test not only the recognizer for the given
    class_id, but also all available recognizers for ancestors of that class_id: indeed, since each
    instance is a positive instance of class_id, that instance is also a member of all ancestors of
    class_id.

    The output file is written to TEST_DATA_DIR/test_class_id_and_ancestors.py .

    @param class_id:
    @param path:
    @param recognizers:
    @param ancestors:
    @return:
    """
    # print(
    #    f"[DEBUG] now generating test file for {class_id} and {len(ancestors)} ancestors"
    # )
    output_file_path = os.path.join(
        TEST_OUTPUT_DIR, class_id.join(["test_", "_and_ancestors.py"])
    )
    with open(output_file_path, "w") as outfile:
        write_module_header(outfile, class_id)
        outfile.write(
            prepare_code_string(class_id, path, recognizers, ancestors, descendants)
        )

    # ruff turns out to be much faster than black
    subprocess.check_output(["ruff", "format", output_file_path])


def remove_existing_test_files() -> None:
    """
    Removes all existing test files from TEST_OUTPUT_DIR. This is necessary to ensure that all new
    test files that will then be written are consistent with the datasets we have.

    @return:
    """
    print("Removing previous test files...", end=" ")
    sys.stdout.flush()
    for filename in os.listdir(TEST_OUTPUT_DIR):
        if filename.startswith("test_") and filename.endswith(".py"):
            os.remove(os.path.join(TEST_OUTPUT_DIR, filename))

    print("done.")


# TODO work in progress: test generator class; on hold because low priority
class TestGenerator:
    """
    A class to generate all test files from a bunch of datasets. Generating all test files at once
    allows us to avoid generating the same test multiple times, by keeping track of the recognizers
    that have already been tested.
    """

    def __init__(self) -> None:
        """
        Initializes the necessary data structures.
        """
        # paths -----------------------------------------------------------------------------------
        self.TEST_OUTPUT_DIR = os.path.join(os.pardir, "tests")
        self.TEST_DATA_DIR = os.path.join(TEST_OUTPUT_DIR, "test_data")

        # useful data structures ------------------------------------------------------------------
        # the ISGCI graph allows us to generate positive tests for ancestors of specific graph
        # class, i.e., tests that verify that a member of a class is indeed identified as such
        self.ISGCI_GRAPH = reduced_isgci_inclusion_graph()

        # the ISGCI exclusion graph allows us to generate negative tests for graph classes excluded
        # by a specific datasets as well as their descendants (e.g., if we are dealing with cubic
        # graphs, then we know that they are NOT trees, and tests will be written to make sure that
        # they are NOT recognized as such)
        self.EXCLUSION_GRAPH = isgci_exclusion_graph()

        # the ids used to identify datasets might differ from the ones we store in the ISGCI graph
        # or the exclusion graph, so we need to map each class id to the set of equivalent ids;
        # this will also force us to write our own ancestors and descendants functions to take
        # these equivalences into account, instead of directly using networkx's functions
        self.EQUIV_IDS = {
            class_id: {alt_id for _, alt_id in equiv_ids}
            for class_id, equiv_ids in isgci_equivalences().items()
        }

        # keep track of the classes for which a test has already been generated so we avoid
        # generating the same test multiple times across different files
        self.TEST_COVERAGE = {"positive": set(), "negative": set()}

        # formatting parameters -------------------------------------------------------------------
        self.WRAP_WIDTH = 100

    def retrieve_all_classes_with_datasets(self) -> Dict[str, str]:
        """
        Returns a dictionary with entries of the form (class_id, path_to_dataset), obtained by
        exploring TEST_BASEDIR non-recursively. Only subdirectories that follow the naming
        convention ANY_TEXT=SINGLE_ISGCI_ID are considered.

        @return:
        """
        testable_classes = dict()
        for subdir in os.listdir(self.TEST_DATA_DIR):
            _, *class_id_list = subdir.split("=")
            testable_classes.update({cid: subdir for cid in class_id_list})

        return testable_classes

    # Graph manipulation methods under equivalence relations --------------------------------------
    def all_recognizable_class_ids_to_recognizers(self) -> Dict[str, Callable]:
        """
        Returns a dictionary with class ids as keys and a corresponding recognizer for each class
        id. Only recognizers which are decorated with @assign_class_id are taken into account, and
        therefore unrecognizable classes will be missing from the dictionary.

        All equivalent classes are mapped to the same recognizer if one is available.

        @return:
        """
        # load all classes with the corresponding recognizers
        base_dict = {
            class_id: recognizer for class_id, recognizer in GraphAnalyzer().recognizers
        }
        # for each recognizable class with at least one equivalent id: map that id to the same
        # recognizer as its equivalent class
        for class_id in set(base_dict).intersection(self.EQUIV_IDS):
            base_dict.update(
                {equiv_id: base_dict[class_id] for equiv_id in self.EQUIV_IDS[class_id]}
            )

        return base_dict

    def __ancestors_or_descendants_of_some_equivalent_class(
            self, graph: networkx.Graph, class_id: str, function: Callable
    ) -> set[str]:
        """
        Returns the ancestors or the descendants of node with label class_id in graph. If that node
        is missing, looks for an equivalent node instead.

        @param graph:
        @param class_id:
        @return:
        """
        # if graph contains class, return its ancestors
        if class_id in graph:
            return function(graph, class_id)

        # otherwise, return the ancestors of an equivalent class
        for eq_id in self.EQUIV_IDS[class_id]:
            if eq_id in graph:
                return function(graph, eq_id)

        # otherwise something is very wrong, raise exception
        raise networkx.exception.NetworkXError(
            f"The node {class_id} is not in the {type(graph)}, and neither are any of its "
            f"equivalent classes."
        )

    def ancestors_of_some_equivalent_class(
            self, graph: networkx.Graph, class_id: str
    ) -> set[str]:
        """
        Returns the ancestors of node with label class_id in graph. If that node is missing, looks
        for an equivalent node instead.

        @param graph:
        @param class_id:
        @return:
        """
        return self.__ancestors_or_descendants_of_some_equivalent_class(
            graph, class_id, networkx.ancestors
        )

    def descendants_of_some_equivalent_class(
            self, graph: networkx.Graph, class_id: str
    ) -> set[str]:
        """
        Returns the descendants of node with label class_id in graph. If that node is missing,
        looks for an equivalent node instead.

        @param graph:
        @param class_id:
        @return:
        """
        return self.__ancestors_or_descendants_of_some_equivalent_class(
            graph, class_id, networkx.descendants
        )

    # TODO keep going
    # Code generation methods ---------------------------------------------------------------------
    def test_method(
            self,
            class_id: str,
            recognizer: Callable,
            base_id: str = "",
            kind: str = "positive",
    ) -> str:
        """
        Returns a test method for the recognizer for class_id. base_id is an optional placeholder
        for a descendant of class_id that led to the writing of this test method.

        kind specifies whether the test methods should test positive instances or not; the default
        behavior is to test positive instances, which results in a call to assertTrue. If kind is
        set to "negative", then we are testing negative instances, which results in a call to
        assertFalse.

        @param class_id:
        @param recognizer:
        @return:
        """
        assert kind in {"positive", "negative"}
        code_string = f'''
        def test_{class_id}(self) -> None:
            """Tests {kind} instances for class {class_id}.'''
        if base_id:
            if "excluded" in base_id:
                code_string += f" {class_id} is a descendant of {base_id}."
            else:
                code_string += f" {class_id} is an ancestor of {base_id}."
        code_string += f'''"""
            print(
                self._testMethodName.join("[]"), "testing", len(self.positive), "graphs", end=" "
            )
            sys.stdout.flush()
    
            # looping over enumerate so we can print failed instances
            for num, graph in enumerate(self.positive):
                self.{["assertFalse", "assertTrue"][kind == "positive"]}(
                    {recognizer.__module__}.{recognizer.__name__}(graph), 
                    "failed on graph number " + str(num) + " / " + str(len(self.positive)) + 
                    " with node set " + str(graph.nodes) + " and edge set " + str(graph.edges)
                )
    
            print("done.")\n'''

        return code_string


def main() -> None:
    """
    Removes previous tests from TEST_OUTPUT_DIR, and generates new ones.

    @return:
    """
    remove_existing_test_files()
    generate_all_test_files()
    # print test statistics
    print(
        f"\nThe generated files cover {sum(map(len, TEST_COVERAGE.values()))} classes, with "
        f"{len(TEST_COVERAGE['positive'])} positive tests and {len(TEST_COVERAGE['negative'])} "
        f"negative tests."
    )
    print("Done. You can now go to the project root and run python3 -m unittest")


if __name__ == "__main__":
    main()
