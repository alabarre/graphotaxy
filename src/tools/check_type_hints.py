"""
Anthony Labarre © 2024

Simple scripts that lists all Python files in a project which have functions or methods with
incomplete type hints. Search is recursive, and virtual environment files are ignored.

Usage:  check_type_hints.py FILE_OR_DIRECTORY

"""
# Imports ---------------------------------------------------------------------
import ast
import os
from _ast import AST
from typing import LiteralString, Iterable


def has_incomplete_type_hints(ast_functiondef_node: AST) -> bool:
    """Returns True if ast_functiondef_node has arguments and at least one of them has no type
    hint, or if no return type hint is provided, and False otherwise.

    @param ast_functiondef_node:
    @return:
    """
    for pos, arg in enumerate(ast_functiondef_node.args.args):
        # class methods have the self parameter in first position, which never has a type hint
        if not pos and arg.arg == "self":
            continue
        if arg.annotation is None:
            return True

    # check whether there's a type hint for the returned value
    return not ast_functiondef_node.returns


def functions_with_incomplete_type_hints(file: str) -> set[str]:
    """
    Returns the names of each function or method in the file with incomplete type hints.

    @param files:
    @return:
    """
    result = set()

    with open(file) as data:
        ast_tree = ast.parse(data.read())

    for node in ast.walk(ast_tree):
        if isinstance(node, ast.FunctionDef) and has_incomplete_type_hints(node):
            result.add(node.name)

    return result


def project_files(directory: str) -> Iterable[LiteralString | str | bytes]:
    """Returns all relative paths to Python files in directory. Search is recursive. Virtual
    environment packages are ignored.

    @param directory:
    @return:
    """
    return [
        os.path.join(root, f)
        for root, _, f_names in os.walk(directory)
        for f in f_names
        if f.endswith(".py") and "site-packages" not in root
    ]


def main() -> None:
    """

    @return:
    """
    from sys import argv

    input_files = project_files(argv[1]) if os.path.isdir(argv[1]) else [argv[1]]
    for file in input_files:
        result = functions_with_incomplete_type_hints(file)
        if result:  # no output, no problem
            print(file)
            for function in result:
                print("    ", function, "has incomplete type hints")


if __name__ == "__main__":
    main()
