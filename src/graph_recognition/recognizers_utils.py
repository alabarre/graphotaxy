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
from functools import lru_cache, update_wrapper
from importlib import import_module
from inspect import isgeneratorfunction, getsource, getmodule
from types import ModuleType, SimpleNamespace
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
def module_path_to_ast(module_path: str) -> ast.AST:
    """
    Returns the AST corresponding to the given module path.

    :param module_path:
    :return:
    """
    with open(module_path, "r") as src:
        return ast.parse(src.read())


@lru_cache(maxsize=None)
def module_to_ast(mod: ModuleType) -> ast.AST:
    """
    Returns the AST for the given module.

    :param mod:
    :return:
    """
    return ast.parse(getsource(mod))


@lru_cache(maxsize=None)
def get_function_ast_def(module_path: str, function_name: str) -> ast.AST | None:
    """
    Returns the node in the AST of the function that corresponds to its definition.

    :param function_name:
    :param module_path:
    :return:
    """
    for node in ast.walk(module_path_to_ast(module_path)):  # noqa
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            return node


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
        node = get_function_ast_def(module_path, function_name)
        if node:
            for sub in ast.walk(node):
                if isinstance(sub, ast.Call) and hasattr(sub.func, "id") and sub.func.id == "assign_fisc":
                    # this is an instance of @assign_fisc, return its argument
                    return {elt.value for elt in sub.args[0].elts}

    return set()


__func_names_to_mods = dict()


@lru_cache(maxsize=None)
def update_func_names_to_mods(module: ModuleType) -> None:
    """
    Retrieves all functions f in module, and stores the mapping "f's name" -> "f's module name".

    :param module:
    :return:
    """
    for node in ast.walk(module_to_ast(module)):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                __func_names_to_mods[alias.name] = node.module


def assign_inherited_fisc(default_fisc: Iterable[str] | None = None) -> Callable:
    """
    Assigns a forbidden induced subgraph characterization to a recognizer. The FISC is obtained by
    computing the union of the FISCs of the recognizers intended to be called by the recognizer to
    decorate

    :return:
    """
    if default_fisc is None:
        default_fisc = set()

    def decorator(function: Callable) -> Callable:
        """
        This decorator behaves like the one in assign_fisc, except that the new attribute will be a
        set of forbidden subgraphs and that it will be automatically built from the FISCs of the
        callees.
        """
        union_of_fiscs = set(default_fisc)

        # examine all "from X import a, b, ..." nodes, and record mapping a -> X, b -> X, ...
        func_mod = getmodule(function)
        update_func_names_to_mods(func_mod)

        # retrieve all calls to other functions in the function's body
        for other in ast.walk(
                ast.Module(body=get_function_ast_def(get_module_path(func_mod.__name__), function.__name__).body)
        ):
            if isinstance(other, ast.Call):
                # found a function call, walk the AST of its source
                if hasattr(other.func, "id"):
                    func_name = other.func.id

                    # try to retrieve the module from our mapping
                    if func_name in __func_names_to_mods:
                        mod_name = __func_names_to_mods[func_name]
                    else:
                        # if not found, assume definition comes from the same module as the function
                        # to decorate
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


def disable_lru_cache(function: Callable):
    """
    Returns a version of func without caching but preserving the lru_cache API.

    :param function:
    :return:
    """
    try:
        original = undecorated_function(function)
    except AttributeError:
        return function

    update_wrapper(original, function)
    original.__dict__.update(function.__dict__)

    original.cache_clear = lambda: None
    original.cache_info = lambda: SimpleNamespace(
        hits=0,
        misses=0,
        maxsize=None,
        currsize=0,
    )
    original.cache_parameters = lambda: {
        "maxsize": None,
        "typed": False,
    }

    return original
