"""
Anthony Labarre © 2023-2025

Miscellaneous utilities for recognizers. This is of no interest to users; if you intend to write
your own recognizers, read on.

To make the integration of new recognizers as seamless as possible, recognizer functions are
identified using a class_id. This class_id is any of the ISGCI ids that the recognizer applies to.
The assign_class_id decorator fulfills that role: when declaring a new recognizer, use:

@assign_class_id("gc_xxx")
def foo(graph):
    pass

The end of your recognizer file must contain a RECOGNIZERS dictionary, with key / value pairs of
the form:

(class_id (str), corresponding_recognizer_function (function))

This dictionary can be built automatically using the current_module_recognizers function; just use:

RECOGNIZERS = current_module_recognizers(os.path.basename(__file__).strip(".py"))

This will also identify decorated recognizers that your module imports and add them to the
dictionary.

Advantages:
    + this approach also makes it easy to exclude recognizers that are later found to be buggy:
        just comment out the @assign_class_id decoration, and the system will ignore the function.
    + refactoring by moving recognizers from one file to another is not an issue, since all
        recognizers are automatically detected and included

Downside: if you need to use external functions as recognizers, you need to add them yourself to
the RECOGNIZERS dictionary. In that case setting class_id is not mandatory, just make sure you
follow the structure of RECOGNIZERS.

"""
# Imports -----------------------------------------------------------------------------------------
import ast
import sys
from collections import OrderedDict
from functools import lru_cache
from importlib import import_module
from inspect import isgeneratorfunction, getsource
from typing import Callable, Iterable


# Decorators --------------------------------------------------------------------------------------
def assign_class_id(class_id: str) -> Callable:
    """
    This decorator adds a given class_id as an attribute of the decorated function. Its use is
    primarily to help automate the tedious process of registering the recognizers.

    @param class_id:
    @return:
    """

    def decorator(function: Callable) -> Callable:
        """
        This decorator adds a given class_id as an attribute of the decorated function. Its use
        is primarily to help automate the tedious process of registering the recognizers.
        """
        setattr(function, "class_id", class_id)
        return function

    return decorator


def assign_fisc(forbidden_subgraphs: Iterable[str]) -> Callable:
    """
    Assigns a forbidden induced subgraph characterization to a recognizer.

    @param forbidden_subgraphs:
    @return:
    """

    def decorator(function: Callable) -> Callable:
        """
        This decorator adds a list of forbidden subgraphs as an attribute of the decorated
        function, which corresponds to the forbidden induced subgraph characterization of the
        corresponding class. As a result, a recognizer R that recognizes a graph G can then be
        queried for its FISC, and when R(G) returns True, its caller then knows that no subgraph in
        R.FISC appears in G.
        """
        setattr(function, "fisc", forbidden_subgraphs)
        return function

    return decorator


# Functions ---------------------------------------------------------------------------------------
def current_module_recognizers(module_name: str, package: object = None) -> OrderedDict:
    """
    Returns an ordered dictionary containing all recognizer functions defined in the module on
    which this function is executed, whose key / value pairs are (class_id, function).

    The order of insertion is the order in which the functions were defined in the module, thus
    allowing the recognizers in the module to be run in that order.

    >>> current_module_recognizers("recognizers_hard")

    @param package:
    @rtype: dict
    @type module_name: str
    @return:
    """
    recognizers_dict = OrderedDict()
    module = import_module(module_name, package)
    # getmembers(module) sorts the results by name, so we use vars() instead, which returns the
    # objects in the order in which they are defined
    for obj in vars(module).values():
        class_id = getattr(obj, "class_id", None)
        # check that this is a recognizer and that it was defined in the given module
        if class_id and obj.__module__ == module_name:
            recognizers_dict[class_id] = obj

    return recognizers_dict


def my_isgeneratorfunction(function: Callable) -> bool:
    """
    Returns True if function is a generator function, False otherwise.

    This function is to be preferred over inspect.isgeneratorfunction, since the latter only works
    on user-defined functions, and we need to be able to detect generators in third-party modules.

    This function has the following limitations:

        - it does not detect functions that return a generator expression;
        - it does not detect functions that call generator functions;
        - it does not work on built-in functions, because it relies on inspect.getsource, which
            raises an exception when called on built-in functions.


    >>> from networkx import connected_components as concomp
    >>> isgeneratorfunction(concomp), my_isgeneratorfunction(concomp)
    (False, True)

    @param function:
    @return:
    """
    return any(
        isinstance(node, ast.Yield) for node in ast.walk(ast.parse(getsource(function)))
    )


def returns_generator(function: Callable) -> bool:
    """
    Returns True if function returns a generator, False otherwise.

    >>> from networkx import common_neighbors
    >>> returns_generator(common_neighbors)
    True

    @param function:
    @return:
    """
    return any(
        isinstance(node, ast.Return) and isinstance(node.value, ast.GeneratorExp)
        for node in ast.walk(ast.parse(getsource(function)))
    )


def cached_function(function: Callable) -> Callable:
    """
    Returns a copy of the function wrapped with lru_cache, after performing a few sanity checks to
    ensure caching the function will not raise issues.

    @param function:
    @return:
    """
    # check whether function yields values instead of returning them
    if my_isgeneratorfunction(function):
        raise TypeError(
            function.__name__
            + " is a generator function, decorating it with lru_cache will cause bugs"
        )

    # check whether function returns a generator expression
    if returns_generator(function):
        raise TypeError(
            function.__name__
            + " returns a generator, decorating it with lru_cache will cause bugs"
        )

    # check whether function has already been lru_cached: caching it an additional time would
    # hide the first cache, defeating its purposes and adding overhead
    # this solution follows from a helpful discussion: https://stackoverflow.com/a/79548654/
    if not hasattr(function, "cache_info"):
        wrapped_function = lru_cache(maxsize=None)(function)
        setattr(sys.modules[function.__module__], function.__name__, wrapped_function)
        return wrapped_function

    # otherwise, simply return the original function
    return function
