"""
Anthony Labarre © 2023-2025

Implementation of a classification digraph.

"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
from typing import Set

# ----- Third party imports -----------------------------------------------------------------------
import networkx as nx

# ----- My imports --------------------------------------------------------------------------------
from isgci.isgci_base import reduced_isgci_inclusion_graph
from isgci.vars import OPEN, HARD, EASY


# Classes -----------------------------------------------------------------------------------------
class ClassificationDigraph(nx.DiGraph):
    """
    A classification digraph is a subgraph of ISGCI's graph class inclusion digraph: its vertices
    are all undirected graph classes in ISGCI's database, and an arc connects each class to its
    maximal subclasses. A classification digraph is meant to be bound to an undirected graph G to
    analyze, and will therefore provide a label for each class vertex C it contains:

        - positive ("+"): G belongs to C
        - negative ("-"): G does not belong to C
        - open ("?"): G is not known to belong or not belong to C

    Positive, negative, and open nodes are colored in shades of green, red, and gray, respectively,
    for ease of visualization when ClassificationDigraph is exported to formats such as GraphML.

    When available, some nodes also contain a reason for their classification.
    """
    # we don't need edge attributes, so we remove them as in the example at
    # https://networkx.org/documentation/stable/reference/classes/digraph.html
    all_edge_dict = dict()

    def single_edge_dict(self) -> dict:
        """

        @return:
        """
        return self.all_edge_dict

    edge_attr_dict_factory = single_edge_dict

    # static attributes
    open, negative, positive = OPEN, HARD, EASY

    # colors play no functional role in this implementation; they only exist
    # for convenience of visualization when exporting to GraphML
    node_colors = {negative: "IndianRed", open: "DarkGray", positive: "LightGreen"}

    def __init__(self) -> None:
        """
        Initializes the ClassificationDigraph. Its value defaults to the whole, simplified ISGCI
        graph class inclusion graph, albeit without directed graph classes.
        """
        super().__init__(reduced_isgci_inclusion_graph())
        # remove directed graph classes
        for directed_id in ("gc_1197", "gc_1198", "gc_1199", "gc_1200", "gc_1201"):
            if directed_id in self:
                self.remove_node(directed_id)

    def has_open_node(self, class_id: str) -> bool:
        """
        Returns True if class_id is an open node in the classification, False otherwise.

        @type class_id: str
        @rtype: bool
        @param class_id:
        @return:
        """
        return class_id in self.nodes and self.nodes[class_id]["category"] == self.open

    def label_and_propagate(self, class_id: str, bool_val: bool, reason: str = "") -> set:
        """
        Labels node with id = class_id with the given value, and removes either its ancestors in
        classification_digraph (if value is positive), or its descendants (if value is negative).

        @type bool_val: bool
        @type class_id: str
        @param bool_val:
        @param class_id:
        @param self:
        @param reason: (optional) the reason for the classification
        """
        # set label and associated color
        val = [self.negative, self.positive][bool_val]
        self.nodes[class_id]["category"] = val
        self.nodes[class_id]["color"] = self.node_colors[val]
        self.nodes[class_id]["reason"] = reason
        # propagate implications
        other_classes = [nx.ancestors, nx.descendants][val == self.negative]
        to_remove = other_classes(self, class_id)
        self.remove_nodes_from(other_classes(self, class_id))
        return to_remove

    def _nodes_from_category(self, category: str) -> Set[str]:
        """
        Returns the set of all nodes from a particular category.

        :return:
        """
        return {cid for cid, data in self.nodes(data=True) if data["category"] == category}

    def negative_nodes(self) -> Set[str]:
        """
        Returns the set of all negative nodes.

        @return:
        """
        return self._nodes_from_category(self.negative)

    def open_nodes(self) -> Set[str]:
        """
        Returns the set of all open nodes.

        @return:
        """
        return self._nodes_from_category(self.open)

    def positive_nodes(self) -> Set[str]:
        """
        Returns the set of all positive nodes.

        @return:
        """
        return self._nodes_from_category(self.positive)

    def number_of_open_nodes(self) -> int:
        """
        Returns the number of open nodes in the classification.

        @rtype: int
        @return:
        """
        return sum(1 for _, data in self.nodes(data=True) if data["category"] == self.open)

    def set_reason(self, class_id: str, reason: str) -> None:
        """
        Sets the reason for the current classification of the node identified by class_id.

        @type class_id: str
        @param class_id:
        @param self:
        @param reason: the reason for the classification
        """
        self.nodes[class_id]["reason"] = reason
