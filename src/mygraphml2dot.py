"""
Anthony Labarre © 2026

Small conversion script from graphml to graphviz format. graphml2gv ignores colors in my classifications.

"""
from sys import argv

import networkx as nx


def main():
    pass
    filepath = argv[1]
    graph = nx.read_graphml(filepath)
    print("digraph G {")
    for v, data in graph.nodes(data=True):
        print("    ", v, "[fillcolor=\"" + data["color"] + "\",style=filled]")
    for u, v in graph.edges:
        print(f"    {u} -> {v}")
    print("}")

if __name__ == "__main__":
    main()
