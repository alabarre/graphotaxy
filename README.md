graphotaxy
==========

`graphotaxy` is a software for performing undirected graph classification. Its two main usages are:

1. single graph classification: given a graph G, compute all minimal classes to which G belongs and all maximal classes to which G does not belong;
1. multiple graph classification: given a collection of graphs, compute the percentage of graphs that belong to each minimal class.

"Minimal" is to be understood with respect to class inclusion relationships; in more accessible terms, the program will always try to be as precise as possible (e.g., if an input graph is a path, then it will be reported as such instead of as a tree or as a bipartite graph).  The classes that are taken into account are a subset of those classes in [ISGCI](https://www.graphclasses.org/) for which a polynomial-time recognition algorithm exists. 

# Installation

There is no binary package yet, so you are supposed to run the program from the sources, which requires the installation of a few dependencies.

After cloning this repository, create a virtual environment and activate it so you can install the necessary Python packages:

```
python3 -m venv .venv            # create the virtual environment (anywhere)
source .venv/bin/activate        # activate it
cd src                           # go to the source subdirectory of graphotaxy
pip install -r requirements.txt  # install the necessary Python packages
./install_gss.sh                 # download and build the Glasgow Subgraph Solver
```

# Basic usage

The simplest way to use the software is to give it one or more input files. As of this writing, `graphotaxy` only accepts `graph6` and `sparse6` files. You can run it like this:

```
python3 main.py -i input_file(s) # wildcards are ok
```

The result depends on the number of graphs in the input file(s):

- if a single graph is analyzed, then the classes to which it belongs are listed, and the result of the classification is written to a `graphml` file for further manipulation or visualisation with external tools (e.g., Cytoscape);
- if several graphs are analyzed, then the output consists of a list of graph classes to which those graphs belong, sorted decreasingly by percentage of members. The classes are as restricted as possible (i.e., if all graphs can be identified to be trees, then the software will identify that class instead of the more general bipartite class that contains it).


# Options

The following options are available. Many of them require knowing the ISGCI id of the class you are interested in (i.e, don't write "bipartite", but "gc_69").

- info options: cause the program to display various information instead of performing an analysis.
    - `--capabilities`:        display various information about what the program can do
    - `--knows [ISGCI id list]`: tell user which of the input classes can be recognized

- input options: modify the information that is given as input to the program.
    - `--negative [ISGCI id list]`: 
                        classes to which all input graphs are known **not** to belong
    - `--positive [ISGCI id list]`:
                        classes to which all input graphs are known to belong
    - `--only [ISGCI id list]`:
                        classes to which the classification must be restricted
    - `--skip [ISGCI id list]`:
                        classes whose recognition should be skipped

- display options:  modify the information that is displayed by the program.
    - `--disable-progress-bars`: disables all progress bars; only the final result will appear
    - `--print-unknown-descendants`: 
                        in addition to each recognized class, print its descendants, if any, which have not been identified
    - `--todo`:                show the classes that have not been identified, although recognizable in polynomial time, due to the lack of an implemented
                        recognizer

- debug options: should be of no interest to the end user
    - `--check-multiple`:      show which classes, if any, have multiple recognizers

# Credits

`graphotaxy` uses many building blocks from other people. I am especially thankful for:

- [`networkx`](https://github.com/networkx), for their graph classes and the many algorithms they provide;
- the [Glasgow Subgraph Solver](https://github.com/ciaranm/glasgow-subgraph-solver) for providing an efficient way of looking for induced subgraphs;
- [PADS](http://www.ics.uci.edu/~eppstein/PADS/) by David Eppstein, portions of whose code I adapted for the purposes of this project;
- [SageMath](https://github.com/sagemath), which also provided some of the code I adapted and used;
- [`tralda`](https://github.com/david-schaller/tralda) by David Schaller, for the linear-time implementation of the recognition algorithm for cographs;
- [ISGCI](https://graphclasses.org/) for providing the necessary information for this project, and without whom `graphotaxy` simply would not exist.

# Citation and references

A paper describing graphotaxy will be submitted shortly, and an "official" bibtex entry will be included here for convenience once the paper is accepted. 
