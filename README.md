# graphotaxy

`graphotaxy` is a software for performing undirected graph classification. Its two main usages are:

1. single graph classification: given a graph G, compute all minimal classes to which G belongs and all maximal classes to which G does not belong;
1. multiple graph classification: given a collection of graphs, compute the percentage of graphs that belong to each minimal class.

"Minimal" is to be understood with respect to class inclusion relationships; in more accessible terms, the program will always try to be as precise as possible (e.g., if an input graph is a path, then it will be reported as such instead of as a tree or as a bipartite graph).  The classes that are taken into account are a subset of those classes in [ISGCI](https://www.graphclasses.org/) for which a polynomial-time recognition algorithm exists. 

---

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

---

# Usage

## Basic usage

The simplest way to use the software is to give it one or more input files. 

```
python3 main.py -i input_file(s) # wildcards are ok
```

The result depends on the number of graphs in the input file(s):

- if a single graph is analyzed, then the classes to which it belongs are listed, and the result of the classification is written to a `graphml` file for further manipulation or visualisation with external tools (e.g., Cytoscape);
- if several graphs are analyzed, then the output consists of a list of graph classes to which those graphs belong, sorted decreasingly by percentage of members. The classes are as restricted as possible (i.e., if all graphs can be identified to be trees, then the software will identify that class instead of the more general bipartite class that contains it).

## Supported file formats

- `g6` and `s6` files, whether plain or compressed in the following formats: `gz`, `bz2`, and `xz`
- `edges` and `mtx` files
- `dot` files (not recommended if they contain more than one graphs, as only the first one will be read)

## Options

The following options are available. Many of them require knowing the ISGCI id of the class you are interested in (e.g., don't write "bipartite", but "gc_69").

- info options: cause the program to display various information instead of performing an analysis.
    - `--capabilities`:        display various information about what the program can do
    - `--knows [ISGCI id list]`: tell user which of the input classes can be recognized

- input options: modify the information that is given as input to the program.
    - `--negative [ISGCI id list]`: 
                        classes to which all input graphs are known **not** to belong
    - `--positive [ISGCI id list]`:
                        classes to which all input graphs are known to belong
                        
- behavior options: modify the behavior of the program, i.e., which recognizers should be run or skipped.

    - `--exponential`: 
                        run exponential-time recognizers (default: `False`)
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
                        
                        
Additional options have been added with the sole purpose of running benchmarks. If you are curious, you can try them out, but they will only result in an (sometimes dramatically) increased running time:

- debug and benchmarking options:
  - `--disable-class-propagations`:
                        disables propagations that occur whenever a graph is recognized (default: False). WARNING: the classification results will be empty if you use this
                        option
  - `--disable-recognizer-caches`:
                        disables all recognizer caches (so the same result will be computed multiple times)
  - `--disable-smart-order`:
                        sorts recognizers by id instead of by complexity
  - `--disable-fisc-propagations`:
                        disables propagations that take place whenever an induced subgraph is found (not) to appear in an input graph (default: False)


---

# Credits

`graphotaxy` builds upon several excellent open-source projects:

* [`networkx`](https://github.com/networkx), for graph data structures and algorithms;
* the [Glasgow Subgraph Solver](https://github.com/ciaranm/glasgow-subgraph-solver), for efficient induced subgraph detection;
* [PADS](http://www.ics.uci.edu/~eppstein/PADS/) by David Eppstein (MIT License);
* [SageMath](https://github.com/sagemath), whose algorithms inspired parts of this implementation;
* [`tralda`](https://github.com/david-schaller/tralda) by David Schaller, for cograph recognition algorithms;
* [ISGCI](https://graphclasses.org/), for graph class data and relationships.

---


# License

This project is licensed under the MIT License.

---

# Code reuse and inspirations

## PADS (David Eppstein)

* License: MIT License
* Source: http://www.ics.uci.edu/~eppstein/PADS/

Some portions of code have been adapted and integrated.
Original license and copyright notices are preserved in the corresponding files.

## SageMath

* License: GPL-compatible
* Source: https://github.com/sagemath/sage

Some algorithms implemented in this project are inspired by SageMath.
This project does not include or redistribute SageMath code.

---

# Third-Party Software

## Glasgow Subgraph Solver

This software is NOT distributed with this repository.

A helper script (`./src/install_gss.sh`) downloads and builds it locally from:
https://github.com/ciaranm/glasgow-subgraph-solver

By default, it installs the solver in `~/.local/bin`. Make sure this directory is in your `PATH`.

The solver is licensed under its own terms (academic / non-commercial).
Users are responsible for complying with those terms.

## Python Dependencies

All Python dependencies are listed in `requirements.txt` and are subject to their respective licenses (MIT, BSD, Apache 2.0, and similar permissive licenses).

---

# Disclaimer

This project is provided "as is", without warranty of any kind.

The authors are not responsible for misuse of third-party software.

---

# Citation

A paper describing graphotaxy will be submitted soon.
A BibTeX entry will be added upon publication.

If you want to get a bird's eye view of the system in the meantime, you can [check out the slides](https://csd11.si/slides/02_05_Labarre.pdf) for the talk I gave at [Computers in Scientific Discovery 11](https://csd11.si/). 
