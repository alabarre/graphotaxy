"""
Anthony Labarre © 2023

Small program for converting the data from distanceregular.org to graph6 /
sparse6.
"""
import glob
import os

# Imports ---------------------------------------------------------------------
import networkx
import networkx as nx
import numpy


def main():
    # handle each csv file in the directory
    missed_data = list()
    for inpath in glob.glob('*.am.csv'):
        try:
            # read in data in numpy format
            indata = numpy.loadtxt(inpath, delimiter=',').astype(int)
            # convert to nx
            graph = nx.from_numpy_array(indata)
            # have nx write file as sparse6
            nx.write_sparse6(graph, inpath.removesuffix(".am.csv") + ".s6")

        except networkx.exception.NetworkXError as e:
            # failed for some reason, inform user when done with the rest
            missed_data.append(inpath)
            print(e)

        except ValueError:
            # failed for some reason, inform user when done with the rest
            missed_data.append(inpath)

    if missed_data:
        print("Failed to convert the following files:")
        for name in missed_data:
            print("    ", name)
    else:
        print("Successfully converted all files.")


if __name__ == "__main__":
    main()
