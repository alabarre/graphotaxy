"""
Anthony Labarre © 2023-2026

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
import os
import sys
from collections import OrderedDict
from functools import lru_cache
from importlib import import_module
from inspect import isgeneratorfunction, getsource, getmodule
from typing import Callable, Iterable, Set


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


@lru_cache(maxsize=None)
def get_module_path(module_name: str) -> str:
    """
    Returns the path to the module whose name is given as input.

    :param module_name:
    :return:
    """
    parts = module_name.split(".")
    for base in sys.path:
        pkg_path = os.path.join(base, *parts)
        py = pkg_path + ".py"
        if os.path.isfile(py):
            return py
        init = os.path.join(pkg_path, "__init__.py")
        if os.path.isfile(init):
            return init

    return ""



@lru_cache(maxsize=None)
def get_fisc(module_name: str, function_name: str) -> Set[str]:
    """
    Returns the FISC associated with the function defined in the given module, or an empty set
    otherwise.

    >>> sorted(get_fisc("graph_recognition.profitable_hereditary_n", "is_split"))
    ['2K_{2}', 'C_{4}', 'C_{5}']

    :param module_name:
    :param function_name:
    :return:
    """
    module_path = get_module_path(module_name)
    if module_path:
        # then load the file and walk its AST up to the function
        with open(module_path, "r") as src:
            for node in ast.walk(ast.parse(src.read())):
                if isinstance(node, ast.FunctionDef) and node.name == function_name:
                    for sub in ast.walk(node):
                        if (isinstance(sub, ast.Call) and hasattr(sub.func, "id")
                                and sub.func.id == "assign_fisc"):
                            # this is an instance of @assign_fisc, return its argument
                            return {elt.value for elt in sub.args[0].elts}

    return set()


def assign_inherited_fisc() -> Callable:
    """
    Assigns a forbidden induced subgraph characterization to a recognizer. The FISC is obtained by
    computing the union of the FISCs of the recognizers intended to be called by the recognizer to
    decorate

    :return:
    """

    def decorator(function: Callable) -> Callable:
        """
        This decorator behaves like the one in assign_fisc, except that the new attribute will be a
        set of forbidden subgraphs and that it will be automatically built from the FISCs of the
        functions called by the provided function.
        """
        union_of_fiscs = set()
        # we are going to walk the AST of a function object, but the calls we will detect only
        # provide us with the **names** of the called functions, which is not enough to access
        # their definitions; therefore, we first build a data structure that allows us to identify
        # the modules that define those functions so we can load them later. Since the function we
        # will decorate needs those functions in its definition, the function's module contains the
        # necessary imports.

        # examine all "from X import a, b, ..." nodes, and record mapping a -> X, b -> X, ...
        func_mod = getmodule(function)
        func_names_to_mods = dict()
        for node in ast.walk(ast.parse(getsource(func_mod))):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    func_names_to_mods[alias.name] = node.module

        # function may or may not be decorated, which is a problem because function calls detected
        # by walking the AST include those decorators; so we first skip to the actual definition of
        # the function
        for node in ast.walk(ast.parse(getsource(function))):
            if isinstance(node, ast.FunctionDef):
                # we're in the function's body, retrieve all calls to other functions
                for other in ast.walk(ast.Module(body=node.body)):
                    if isinstance(other, ast.Call):
                        # found a function call, walk the AST of its source
                        if hasattr(other.func, "id"):
                            func_name = other.func.id

                            # try to retrieve the module from our mapping
                            if func_name in func_names_to_mods:
                                mod_name = func_names_to_mods[func_name]
                            else:
                                # if not found, assume definition comes from the same module as the
                                # function to decorate
                                mod_name = func_mod.__name__

                            union_of_fiscs.update(get_fisc(mod_name, func_name))

        setattr(function, "fisc", union_of_fiscs)
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


    >>> from networkx import connected_components
    >>> isgeneratorfunction(connected_components), my_isgeneratorfunction(connected_components)
    (False, True)

    @param function:
    @return:
    """
    return any(isinstance(node, ast.Yield) for node in ast.walk(ast.parse(getsource(function))))


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


def undecorated_function(function: Callable) -> Callable:
    """
    Returns the original function from a function that has been decorated (possibly multiple times).

    :param function:
    :return:
    """
    func = function
    while hasattr(func, "__wrapped__"):
        func = func.__wrapped__
    return func
