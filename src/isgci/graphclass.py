"""
Anthony Labarre © 2020-2026

Implementation of a GraphClass class. This does NOT provide a class for using graphs, but rather to
obtain information about a specific graph class from ISGCI.

"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
from os.path import join
from typing import Iterable, Set

# ----- Third-party imports -----------------------------------------------------------------------
from bs4 import BeautifulSoup

# ----- My imports --------------------------------------------------------------------------------
from isgci.functions import class_id_from_url, prettify_name
from isgci.vars import ISGCI_DIR


class GraphClass:
    """
    A class for storing information about a graph class known to ISGCI. The graph class must be
    initialized using its ISGCI id, or the URL to its page on ISGCI.
    """

    def __init__(self, path_or_id: str, problem_name: str = "") -> None:
        """
        Initializes data and retrieves information on graph class from path_or_id.

        @type problem_name: None, str
        @type path_or_id: str
        @param path_or_id:
        @param problem_name:
        """
        # initialise data structures
        self._problem_info = dict()
        self._id = ""
        self.problem_name = problem_name

        # turn id into url if need be
        if not path_or_id.lower().endswith(".html"):
            self._id = path_or_id
            path_or_id = join(ISGCI_DIR, "classes", path_or_id + ".html")

        # read and store page contents
        self.url = path_or_id
        with open(self.url, encoding="utf-8") as data:
            self.page_contents = data.read()
        self.soup = BeautifulSoup(self.page_contents, features="html.parser")

    def class_id(self) -> str:
        """
        Returns the class' id.

        @rtype: str
        """
        return self._id

    def class_name(self) -> str:
        """
        Returns the class' name.

        @rtype: str
        """
        return prettify_name(
            self.soup.find("h1").decode_contents().replace("Graphclass:", "").strip()
        )

    def _get_classes(self, relation: str) -> Set[str]:
        """
        Returns all classes that satisfy the specified relation.

        @type relation: str
        @param relation:
        @rtype: set[str]
        @return:
        """
        # assert relation in {'maxsub', 'minsuper', 'equivs', 'complements'}
        try:
            # jump to the relevant section in the class' page
            relevant_section = self.soup.find("div", {"class": relation})

            # self-complementary classes only have a <p>self-complementary</p> child in that
            # section; in that case, just return a set with the current class id
            if relevant_section.p and relevant_section.p.text == "self-complementary":
                return {self._id}

            # otherwise, check if there is a section with the wanted relation and list the contents
            classes = (
                self.soup.find("div", {"class": relation})
                .find_next("ul", {"class": "classeslist"})
                .find_all("li")
            )

            return {class_id_from_url(elem.find("a").get("href")) for elem in classes}

        except AttributeError:
            # "'NoneType' object has no attribute 'find_next'" occurs when no minimal superclass or
            # maximal subclass is known to ISGCI
            return set()

    def complement_classes(self) -> Iterable[str]:
        """
        Returns the ID's of the class's complement classes.

        >>> G = GraphClass("gc_151")
        >>> G.complement_classes()

        @rtype: Iterable[str]
        @return:
        """
        return self._get_classes("complements")

    def equivalent_classes(self) -> Iterable[str]:
        """
        Returns the ID's of the class's equivalent classes.

        @rtype: Iterable[str]
        @return:
        """
        return self._get_classes("equivs")

    def fisc(self) -> Iterable[str]:
        """
        Returns the class's FISC as a set of smallgraph names if one exists, or an empty iterable
        otherwise.

        >>> not GraphClass("gc_302").fisc()
        True
        >>> sorted(GraphClass("gc_329").fisc())
        ['2K_{2}', 'C_{4}', 'P_{4}']

        @rtype: Iterable[str]
        @return:
        """
        _fisc = set()
        classes = self.soup.find("p", {"id": "forbdetails"})
        if classes is not None:
            # jump to the span that contains each subgraph
            for cell in classes.find_all("span", {"style": "display:table-cell"}):
                # ignore links to pictures
                if cell.next_element.name == "a":
                    continue

                # strip surrounding <b> and </b>
                _fisc.add(prettify_name(str(cell.next_element)[3:-4]))

        # the following two strings may have been erroneously gathered from pages where a different
        # figure from the actual graph is shown (e.g. gc_1330, AUTO_2092), so we remove them
        _fisc.discard("igure sho")
        _fisc.discard("igure show")

        return _fisc

    def maximal_subclasses(self) -> Set[str]:
        """
        Returns the ID's of the class's maximal subclasses.

        >>> G = GraphClass("gc_1059")  # self-complementary: no subclass known
        >>> G.maximal_subclasses()
        set()
        >>> G = GraphClass("gc_110")  # outerplanar: 4 maximal subclasses
        >>> sorted(G.maximal_subclasses())
        ['gc_1028', 'gc_108', 'gc_109', 'gc_723']

        @rtype: set[str]
        @return:
        """
        return self._get_classes("maxsub")

    def minimal_superclasses(self) -> Set[str]:
        """
        Returns the ID's of the class's minimal superclasses.

        >>> G = GraphClass("gc_1059")  # self-complementary: no superclass known
        >>> G.minimal_superclasses()
        set()

        @rtype: set[str]
        @return:
        """
        return self._get_classes("minsuper")

    def recognition_status(self) -> str:
        """
        Returns the status of the recognition problem for this class, or "[status not found]".

        @rtype: str
        @return:
        """
        # look for the td right after "<td>Recognition"
        for elem in self.soup.find_all("td"):
            if elem.text.startswith("Recognition"):
                return elem.next_sibling.text

        return "[status not found]"
