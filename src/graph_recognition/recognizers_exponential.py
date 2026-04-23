"""
Anthony Labarre © 2026

This file contains recognizers with an exponential running time.

"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
import os
from functools import lru_cache

# ----- Third-party imports -----------------------------------------------------------------------
import networkx as nx

# ----- My imports --------------------------------------------------------------------------------
from graph_recognition.fisc_based_recognizers import is_bull_free, is_diamond_free
from graph_recognition.profitable_hereditary_n import is_planar, is_line, is_bipartite, is_cograph, is_chordal
from graph_recognition.profitable_hereditary_n_2 import is_comparability
from graph_recognition.profitable_hereditary_n_3 import is_paw_free
from graph_recognition.profitable_hereditary_n_4 import is_c4_free, is_k4_free, is_claw_free
from graph_recognition.recognizers_n_5 import is_split_neighbourhood
from graph_recognition.recognizers_utils import current_module_recognizers, assign_class_id, assign_inherited_fisc


# Recognizers -------------------------------------------------------------------------------------
# ----- Subclasses of perfect graphs --------------------------------------------------------------
@lru_cache(maxsize=None)
@assign_class_id("gc_56")
def is_perfect(graph: nx.Graph) -> bool:
    """
    A graph is perfect if for all induced subgraphs H: chi(H) = omega(H), where chi is the
    chromatic number and omega is the size of a maximum clique.

    https://www.graphclasses.org/classes/gc_56.html

    :param graph:
    :return:
    """
    # the following families are included in the class of perfect graphs and membership is much
    # cheaper to check; ordered by increasing complexity
    profitable_recognizers_for_subclasses = (
        is_bipartite, is_cograph, is_chordal, is_comparability
    )
    if any(recognizer(graph) for recognizer in profitable_recognizers_for_subclasses):
        return True

    # note: this algorithm runs in exponential time, but a polynomial-time algorithm exists for
    # recognizing perfect graph (check https://www.graphclasses.org/classes/gc_56.html for more
    # info); I haven't found an implementation of that algorithm
    return nx.is_perfect_graph(graph)  # noqa (pycharm can't find is_perfect_graph)


# The following recognizers all run in exponential time, because they call is_perfect. There may
# very well exist much more efficient recognition algorithms.
@assign_inherited_fisc()
@lru_cache(maxsize=None)
@assign_class_id("gc_283")
def is_perfect_and_planar(graph: nx.Graph) -> bool:
    """
    https://www.graphclasses.org/classes/gc_283.html

    :param graph:
    :return:
    """
    return is_planar(graph) and is_perfect(graph)


@lru_cache(maxsize=None)
@assign_class_id("gc_626")
def is_perfect_and_split_neighbourhood(graph: nx.Graph) -> bool:
    """
    https://www.graphclasses.org/classes/gc_626.html

    :param graph:
    :return:
    """
    return is_split_neighbourhood(graph) and is_perfect(graph)


@assign_inherited_fisc()
@lru_cache(maxsize=None)
@assign_class_id("gc_1250")
def is_c4_free_and_perfect(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_1250.html

    :param graph:
    :return:
    """
    return is_c4_free(graph) and is_perfect(graph)


@assign_inherited_fisc()
@lru_cache(maxsize=None)
@assign_class_id("gc_598")
def is_k4_free_and_perfect(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_598.html

    :param graph:
    :return:
    """
    return is_k4_free(graph) and is_perfect(graph)


@assign_inherited_fisc()
@lru_cache(maxsize=None)
@assign_class_id("gc_64")
def is_bull_free_and_perfect(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_64.html

    :param graph:
    :return:
    """
    return is_bull_free(graph) and is_perfect(graph)


@assign_inherited_fisc()
@lru_cache(maxsize=None)
@assign_class_id("gc_139")
def is_claw_free_and_perfect(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_139.html

    :param graph:
    :return:
    """
    return is_claw_free(graph) and is_perfect(graph)


@assign_inherited_fisc()
@lru_cache(maxsize=None)
@assign_class_id("gc_603")
def is_diamond_free_and_perfect(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_603.html

    :param graph:
    :return:
    """
    return is_diamond_free(graph) and is_perfect(graph)


@assign_inherited_fisc()
@lru_cache(maxsize=None)
@assign_class_id("gc_253")
def is_line_and_perfect(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_253.html

    :param graph:
    :return:
    """
    return is_line(graph) and is_perfect(graph)


@assign_inherited_fisc()
@lru_cache(maxsize=None)
@assign_class_id("gc_1358")
def is_line_and_perfect(graph: nx.Graph) -> bool:
    """
    A graph is line perfect if its line graph is perfect graph.

    https://www.graphclasses.org/classes/gc_1358.html

    :param graph:
    :return:
    """
    return is_perfect(nx.line_graph(graph))


@assign_inherited_fisc()
@lru_cache(maxsize=None)
@assign_class_id("gc_278")
def is_paw_free_and_perfect(graph: nx.Graph) -> bool:
    """

    https://www.graphclasses.org/classes/gc_278.html

    :param graph:
    :return:
    """
    return is_paw_free(graph) and is_perfect(graph)


# This code segment must always be at the END of a recognizer file --------------------------------
RECOGNIZERS = current_module_recognizers(
    ".".join(
        [
            os.path.basename(os.path.dirname(__file__)),
            os.path.basename(__file__).removesuffix(".py"),
        ]
    )
)
# -------------------------------------------------------------------------------------------------
