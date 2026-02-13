# Possible applications

cognos will tell us which patterns are avoided / appear in our graphs, but they might be many. so if we can take the union of
everything that's avoided / matched and then run cognos on that, we might get interesting answers.

# Performance issues

- don't forget about weapons like sat solvers, for instance if I want to know whether a graph is hamiltonian ...
- give ring a try (https://pypi.org/project/ring/) : they have a caching mechanism similar to lru_cache but which allows
    for modifications to the cache by external functions.
    Use case: it is known that split graphs are chordal and co-chordal. So a positive answer to is_split may be
    propagated to chordal AND co-chordal without the need to run these functions.
        note: well, if I get a positive answer, then I won't run these anyway since they contain split graphs

    so ring might be interesting but maybe not for me right now ...
- ordering recognizers: gss is fast, but maybe I should first examine classes that allow me to rule out patterns
    - for instance: run is_bipartite first; if it's true, then

# Recognition algorithms

- I think I remember a few definitions mentioning metric triangles, and now I've implemented their search for is_weakly_modular
    find out which other classes i can now easily recognize


PADS (https://ics.uci.edu/~eppstein/PADS/) by David Eppstein has a number of algorithms, some of which are recognition algorithms.
I downloaded everything, as far as I can tell there are only two recognition algorithms:

- PartialCube.py:   isPartialCube   (O(n²) for https://www.graphclasses.org/classes/gc_1160.html)
- Halin.py:         isHalin         (https://www.graphclasses.org/classes/gc_198.html)

I included both, refinements will be needed but at least they work. I need more time and focus to refine them properly.

hey, he did lexbfs too! that'll open doors


- move higher complexity algos to lower complexity files. since i'm starting with all fiscky classes anyway,
 i can assume the complexity of a recognition algo that involves this is much lower, since the fiscky aspect is known already

# Features

- find a way to infer things from a classification. For instance, if I'm interested in studying boolean property X and
    I have datasets X-true and X-False, find out the differences between the classifications for both datasets automatically.
    Some ideas:
        - automatically remove properties that are always true for both datasets


- checking classifications: given a classification, check for contradictions;
    inconsistencies: for any two classes A >= B: if G in B, then G must be in A
    others?
    known info:
        if graphs are known to belong to a class, then cognos should have identified that class or at least one subclass
        if graphs are known NOT to belong to a class, then cognos should NOT identify that class or any subclass


- query module: I might want to ask the classification whether all my graphs are planar, which may not be obvious if they are scattered among various obscure subclasses of planar

- parallel processing of all my graphs by GA
    - well, let's rather parallelise recognition algorithms instead. that way I'll get improved performances even for a single graph

- warn user if demands are unrealistic (loading too many graphs into memory, or too large, or ...) instead of just crashing

# Classes whose recognition I can't implement

F_{n} grid --- https://www.graphclasses.org/classes/gc_526 Linear
    can't access the paper, so don't know the definition. haven't tried mailing the authors yet.


# Much later

        # TODO print possibly new findings?
        #   then I need to tell cognos what my graph class is so it can make guesses
        #   idea: for all classes to which 100% of the graphs have been found to belong,
        #       look up inclusions in isgci and report the ones that were not found

main:

use added knowledge (--positive, --negative) to obtain more results

TODO for instance, if I'm told that
    all input graphs are hamiltonian, which is hard to check, I'd like to narrow down the classification and check whether or not they are
    hamiltonian AND planar, etc.
    solution: have "dependent" recognizers ready. Example:

    def is_hamiltonian_and_planar(graph, classification):
        if [classification says not hamiltonian]:
            return False
        return check_planarity(graph)

        # TODO write classification to output file compatible with cytoscape (json's fine apparently);
        #   let's pickle for now; https://manual.cytoscape.org/en/stable/Supported_Network_File_Formats.html


    # TODO --hard parameter to include recognizers_hard in graph_analyzer


        # TODO print possibly new findings?
        #   then I need to tell cognos what my graph class is so it can make guesses
        #   idea: for all classes to which 100% of the graphs have been found to belong,
        #       look up inclusions in isgci and report the ones that were not found




smallgraphs:

    TODO generate TODOs when a faster algorithm exists: look either at
        "recognition" section, or at that section in equivalent classes


remove / reduce dependencies on other modules
    PADS: probably a lot of things ended up in networkx or can be made networkx compatible

Visualisation:
    - I'm exporting to GML now, can I bundle the style with the GML file for cytoscape?
    - hyperlinks on nodes
    - colors on nodes (this did not work: http://graphml.graphdrawing.org/primer/graphml-primer.html#Attributes
      or at least cytoscape ignores it)
    - readable node labels ... I think I should use prettify names when I create the classifications

Maybe we can get a more efficient representation of graphs by subclassing accordingly like we did for ClassificationDigraph. Read nx's doc.

hey: if cognos outputs classifications, I could have a helper program that just computes their "union" as algo 2 does in my manuscript.
that would be useful for different values of n

if i'm only interested in forbidden subgraphs, write a separate, dedicated tool.

choose a license https://choosealicense.com/

organize and package this properly

venv against pypy and regular python

requirements.txt

etc

[ ] remove all dependencies on enlighten

[ ] lots of logging

[ ] allow aborting current recognizer, so we can at least get partial results when some recognizers take too long


# README file

make sure you compile GSS