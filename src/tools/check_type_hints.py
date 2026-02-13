"""
Anthony Labarre © 2024

Simple scripts that lists all Python files in a project which have functions or methods with
incomplete type hints. Search is recursive, and virtual environment files are ignored.

Usage:  check_type_hints.py FILE_OR_DIRECTORY

"""
# Imports ---------------------------------------------------------------------
import ast
import os
from typing import LiteralString, Iterable
from _ast import AST


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


def print_missing_type_hints(files: Iterable[LiteralString | str | bytes]) -> None:
    """
    for each file, check that all functions have type hints

    @param files:
    @return:
    """
    # go through each input file
    for source in sorted(files):
        print(source)
        with open(source) as file:
            ast_tree = ast.parse(file.read())
        for node in ast.walk(ast_tree):
            if isinstance(node, ast.FunctionDef) and has_incomplete_type_hints(node):
                print("    ", node.name, "has incomplete type hints")


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

    files = project_files(argv[1]) if os.path.isdir(argv[1]) else [argv[1]]
    print_missing_type_hints(files)


if __name__ == "__main__":
    main()
