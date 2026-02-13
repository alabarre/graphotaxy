`graphotaxy` is a software for performing undirected graph classification. Its two main usages are:

1. single graph classification: given a graph G, compute all minimal classes to which G belongs and all maximal classes to which G does not belong;
1. multiple graph classification: given a collection of graphs, compute the percentage of graphs that belong to each minimal class.

The classes that are considered are a subset of those classes in [ISGCI](https://www.graphclasses.org/) for which 

# Installation

There is no binary package yet, so you are supposed to run the program from the sources, which requires the installation of a few dependencies.

After cloning this repository, create a virtual environment and activate it so you can install the necessary Python packages:

```
python3 -m venv .venv            # create the virtual environment
source .venv/bin/activate        # activate it
cd src                           # go to the source directory
pip install -r requirements.txt  # install the necessary Python packages
./install_gss.sh                 # download and build the Glasgow Subgraph Solver
```

The last step is independent of the rest.

# Basic usage

The simplest way to use the software is to give it one or more input files:

```
python3 main.py -i input_file(s) # wildcards are ok
```

The result depends on the number of graphs in the input file(s):

- if a single graph is analysed, then the classes to which it belongs are listed, and the result of the classification is written to a graphml file for visualisation with external tools (e.g., Cytoscape);
- if several graphs are analysed, then the output consists of a list of graph classes to which those graphs belong, sorted decreasingly by percentage of members. The classes are as restricted as possible (i.e., if all graphs can identified to be trees, then the software will identify that class instead of the more general bipartite class that contains it).


# Options

The following options are available. Many of them require knowing the ISGCI id of the class you are interested in (i.e, don't write "bipartite", but "gc_69").

- info options: cause the program to display various information instead of performing an analysis.
    - --capabilities:        display various information about what the program can do
    - --knows [ISGCI id list]: tell user which of the input classes can be recognised

- input options: modify the information that is given as input to the program.
    - --negative [ISGCI id list]: 
                        classes to which all input graphs are known **not** to belong
    - --positive [ISGCI id list]
                        classes to which all input graphs are known to belong
    - --only [ISGCI id list]
                        classes to which the classification must be restricted
    - --skip [ISGCI id list]
                        classes whose recognition should be skipped

- display options:  modify the information that is displayed by the program.

    - --disable-progress-bars: disables all progress bars; only the final result will appear
    - --print-unknown-descendants: 
                        in addition to each recognized class, print its descendants, if any, which have not been identified
    - --todo:                show the classes that have not been identified, although recognizable in polynomial time, due to the lack of an implemented
                        recognizer

- debug options: should be of no interest to the end user

    - --check-multiple:      show which classes, if any, have multiple recognizers

# Credit

TODO list and thank software / authors on which this is based


A paper describing graphotaxy is to be submitted. If graphotaxy is helpful to you in any way, please cite it and let me know about it. I'm always happy to learn that my work has been useful to someone.

