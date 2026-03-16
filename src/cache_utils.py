"""
Anthony Labarre © 2026

Some functions that are useful for dealing with objects decorated by functools.lru_cache.

"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
from importlib import import_module
from typing import Iterable, Callable, Set, Tuple


# Functions ---------------------------------------------------------------------------------------
def clear_function_caches(functions: Iterable[Callable]) -> Tuple[int, int]:
    """
    Clears the caches of all provided functions, and returns the total number of cache hits and
    cache misses they performed. Only functions decorated with lru_cache are allowed.

    :param functions: the functions whose cache must be cleared
    :return: nothing
    """
    hits, misses = 0, 0
    for func in functions:
        try:
            hits += func.cache_info().hits
            misses += func.cache_info().misses
            func.cache_clear()
        except AttributeError:
            # all provided functions are supposed to be cached, so we exit if something went wrong
            # to signal it has to be fixed
            print(f"no cache for function {func.__name__} from {func.__module__}")
            exit(-1)

    return hits, misses

def get_cached_non_recognizers(module_name: str, package: object = None) -> Set[Callable]:
    """
    Returns all functions from module_name that have been decorated with lru_cache.

    >>> sorted(map(lambda x: x.__name__, get_cached_non_recognizers("graph_recognition.misc_algo")))

    :param module_name:
    :param package:
    :return:
    """
    module = import_module(module_name, package)
    return {
        obj for obj in vars(module).values()
        if getattr(obj, "cache_info", None) is not None  # function is cached
           and getattr(obj, "class_id", None) is None  # but it is not a recognizer
    }
