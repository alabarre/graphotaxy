"""
Anthony Labarre © 2025

TODO given classes C1, C2, ... as input, generate all graphs on n vertices that belong to that class

main motivation for now: I need datasets for various classes

"""
from typing import Callable, Iterable

from graph_analyzer import GraphAnalyzer


def generate_all_connected_graph_in_class(n, recognizers):
    pass # TODO


def get_recognizers(class_ids: Iterable[str]) -> Iterable[Callable]:
    """Checks whether the classes provided as class id's can be recognized, whether directly or by
    means of a recognizer for an equivalent class, and returns an iterable with the corresponding
    recognizers. Raises a ValueError exception if one of the classes has no available recognizer.
    """
    analyzer = GraphAnalyzer()
    retval = []
    for _id in class_ids:
        function = analyzer.get_recognizer(_id)
        if function is not None:
            retval.append(function)
            break

        else:
            raise ValueError("no recognizer available for class " + _id)

    return retval


def main():
    # TODO argparse to retrieve ONE recognizer for now -- later, multiple -- and a value of n or a range
    # TODO initialize GraphAnalyzer and find recognizer for wanted class or equivalent
    #   call get_recognizers
    # TODO filter out all connected graphs on n vertices that belong to the wanted class and write them to g6 file
    pass


if __name__ == "__main__":
    main()
