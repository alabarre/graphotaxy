"""
Anthony Labarre © 2024-2026

Simple script that lists all Python files in a project which have functions or methods with
incomplete type hints. Search is recursive, and virtual environment files are ignored.

Usage:  check_type_hints.py FILE_OR_DIRECTORY

# TODO make the program also report "wrong" type hints, like set[str] instead of Set[str]

"""
# Imports -----------------------------------------------------------------------------------------
# Standard imports --------------------------------------------------------------------------------
import ast
import os
from _ast import AST
from sys import argv
from typing import LiteralString, Iterable


def has_incomplete_type_hints(ast_functiondef_node: AST) -> bool:
    """
    Returns True if ast_functiondef_node has arguments and at least one of them has no type hint,
    or if no return type hint is provided, and False otherwise. The parameter "self" in methods
    is ignored, since it never has a type hint.

    @param ast_functiondef_node:
    @return:
    """
    # check whether there's a type hint for the return value
    return not ast_functiondef_node.returns or any(
        arg.annotation is None for pos, arg in enumerate(ast_functiondef_node.args.args)
        # class methods have the self parameter in first position, which never has a type hint:
        # ignore
        if pos or arg.arg != "self"
    )


def functions_with_incomplete_type_hints(file: LiteralString | str | bytes) -> set[str]:
    """
    Returns the names of each function or method in the file with incomplete type hints.

    @param files:
    @return:
    """
    with open(file) as data:
        return {
            node.name for node in ast.walk(ast.parse(data.read()))
            if isinstance(node, ast.FunctionDef) and has_incomplete_type_hints(node)
        }


def project_files(directory: str) -> Iterable[LiteralString | str | bytes]:
    """
    Returns all relative paths to Python files in directory. Search is recursive. Virtual
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
    if len(argv) != 2:
        print(f"Usage: {os.path.basename(argv[0])} DIRECTORY_OR_FILE")
        exit(-1)

    # if only one file is provided, check it; otherwise, examine all files in the given directory
    input_files = project_files(argv[1]) if os.path.isdir(argv[1]) else [argv[1]]
    for file in input_files:
        result = functions_with_incomplete_type_hints(file)
        if result:  # no output, no problem
            print(file)
            for function in result:
                print("    ", function, "has incomplete type hints")


if __name__ == "__main__":
    main()
