"""
Anthony Labarre © 2023

Partial classifications. The recognizers in this module provide partial answers
("yes" or "I don't know"; "no" or "I don't know"). They correspond to classes
that are hard to recognize: i.e., the recognition problem is open or
NP-complete, or there may exist an algorithm but no readily available
implementation.

"""
from graph_recognition.subgraphs import is_h_free


# Imports ----------------------------------------------------------------------

# Functions --------------------------------------------------------------------
def is_not_unit_disk(graph):
    """Returns True if graph is NOT a unit disk graph, None otherwise.

    :param graph:
    :return:
    """
    # a graph that contains one of the following induced subgraph is NOT a unit
    # disk graph (https://arxiv.org/abs/1602.08148)
    return not is_h_free(
        graph, [
            "K_{1,6}", "K_{2,3}",
            "co(X_{88}",    # their G_1
            # TODO what is their G_2?
            "twin-C_{5}",   # their G_3
            "X_{38}",       # their G_4
            "BW_{3}",       # their G_5
            'co(C_{8})'     # Theorem 7
        ]
    )
    # TODO there are others: thm 6 mentions co(K_{2} U C_{2k+1}) for all k >= 1
    #   it seems we have none of these in smallgraphs/
    # TODO there are others: thm 7 mentions co(C_k) for all even k >=8
    #   but how "far" are we willing to take this?


# TODO RECOGNIZERS STRUCTURE --- or NEGATIVE / POSITIVE RECOGNIZERS?
NEGATIVE_RECOGNIZERS = {
    "gc_389": is_not_unit_disk,     # no info on complement
}


def main():
    pass


if __name__ == "__main__":
    main()
