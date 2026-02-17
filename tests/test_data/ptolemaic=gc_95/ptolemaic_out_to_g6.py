"""
Anthony Labarre © 2025-2026
"""


def main() -> None:
    from sys import argv
    from networkx import Graph, to_graph6_bytes
    import os
    if len(argv) != 2:
        print(f"Usage: {argv[0]} file.out")
        exit(-1)

    output_filename = os.path.splitext(argv[1])[0] + ".g6"
    with open(argv[1]) as data, open(output_filename, "w") as output_g6:
        current_line = data.readline()
        while current_line != "":
            # line 1: num_vertices num_edges
            # num_edges subsequent lines: u v
            num_vertices, num_edges = map(int, current_line.split())
            graph = Graph()
            graph.add_nodes_from(range(num_vertices))
            for _ in range(num_edges):
                graph.add_edge(*map(int, data.readline().split()))
            output_g6.write(to_graph6_bytes(graph, header=False).decode() + "\n")
            current_line = data.readline()


if __name__ == "__main__":
    main()
