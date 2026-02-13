---
title: Writing recognizers for `cognos`
author: Anthony Labarre
date: 2024
---

[//]: # (# Writing recognizers)

This document provides the information needed to be able to write recognizers.

# The basics

A *recognizer* is a function that takes a graph as input and returns `True` if the graph belongs to a specific graph
class, and `False` otherwise. The basic skeleton for writing a recognizer is therefore simply:

```python
def is_member(graph) -> bool:
    # recognition algorithm
```

This is sufficient for recognition purposes, but a graph analyzer needs more information in order to associate the
recognizer to a relevant graph class. A graph class is identified by a case-sensitive ISGCI id, which is a string
formatted as
`"gc_number"` or `"AUTO_number"`. The above recognizer will be tied to the graph class using a specific
decorator, like so:

```python
from graph_recognition.recognizers_utils import assign_class_id


@assign_class_id("gc_xxx")
def is_member(graph) -> bool:
    # recognition algorithm
```

In addition to tying recognizers to actual graph classes, this decorator also makes it easy for the system to identify and load recognizers using a 
`GraphAnalyzer` object. In order to achieve that, the file in which you write your recognizers, which the `GraphAnalyzer` object must be instructed 
to load, must end with the following code segment:

```python
RECOGNIZERS = current_module_recognizers(
os.path.basename(__file__).strip(".py")
)
```

Another advantage of this approach is the ability to easily enable or disable a specific recognizer, e.g. for debugging purposes: 
simply comment out the `@assign_class_id` decoration before your recognizer, and the `GraphAnalyzer` object will not load it, since the 
`RECOGNIZERS` dictionary will no longer contain it.

If you need to include third-party recognizers in your file, you will need to associate a class id to each of those recognizers as well. 
You don't have to decorate them with `@assign_class_id` to achieve this: you can simply build a dictionary creating those 
associations and add them to the `RECOGNIZERS` dictionary, like so:

```python
# assign class id's to external recognizers that RECOGNIZERS must include
EXTERNAL_RECOGNIZERS = {
    "gc_1149": nx.is_regular,
    "gc_342": nx.is_tree,
    "gc_771": nx.is_biconnected,
}
RECOGNIZERS.update(EXTERNAL_RECOGNIZERS)
```


# Organizing recognizers

Recognizers are roughly ordered by increasing worst-case complexity. They are scattered among three categories of files:

1. `fisc_based_recognizers`, which are recognizers for graph classes whose recognition is based on a forbidden induced
   subgraph characterization;
2. `recognizers_n`, `recognizers_n_2`, `recognizers_n_3`, ... files, which respectively contain recognizers with a
   running time of $O(m+n)$, $O(n^2)$, $O(n^3)$, ...;
3. `profitable_hereditary_constant`, `profitable_hereditary_n`, `profitable_hereditary_n_2`,
   `profitable_hereditary_n_3`, ... files, which follow the same approach as the previous category: the difference is
   that the recognizers they contain concern FISC-based recognizers with a better running time than the naïve approach

When you write a recognizer, make sure you place it in the right file depending on its category as outlined above. The
graph analyzer will run recognizers by increasing complexity, hoping to avoid running the more costly ones.

# FISC-based recognizers


FISC-based graph classes (or *fiscky classes* for short) are *hereditary*, which means that they are
closed under vertex deletion: if $G$ belongs to such a class $C$, then so does $G-{v}$ for any $v\in V(G)$.

The file `fisc_based_recognizers.py` contains naïve FISC-based recognizers only: most of them call the
`subgraphs.is_h_free` function, but some of them might implement another approach. In that case, they need to call
`dispatch_findings` TODO explain this better


dispatchfindings is gone for user, but explain that either we do our magic by calling is_h_free or we need to assign_fisc

## Naïve FISC-based recognizers


also, sort recognizers by increasing complexity

also, think about fisc based recognizers

## Profitable FISC-based recognizers

# doc from recognizers utils . py

Miscellaneous utilities for recognizers. This is of no interest to users; if
you intend to write your own recognizers, read on.

To make the integration of new recognizers as seamless as possible, recognizer
functions are identified using a class_id. This class_id is any of the ISGCI ids
that the recognizer applies to. The assign_class_id decorator fulfills that
role: when declaring a new recognizer, use:

```python
@assign_class_id("gc_xxx")
def foo(graph):
    pass

```

The end of your recognizer file must contain a RECOGNIZERS dictionary, with
key / value pairs of the form

(class_id (str), corresponding_recognizer_function (function))

This dictionary can be built automatically using the current_module_recognizers
function; just use:

This will also identify decorated recognizers that your module imports and add
them to the dictionary.

Advantages:

+ this approach also makes it easy to exclude recognizers that are later
  found to be buggy: just comment out the @assign_class_id decoration,
  and the system will ignore the function.
+ refactoring by moving recognizers from one file to another is not an
  issue, since all recognizers are automatically detected and included

Downside: if you need to use external functions as recognizers, you need to add
them yourself to the RECOGNIZERS dictionary. In that case setting class_id is
not mandatory, just make sure you follow the structure of RECOGNIZERS.

# Efficiency

## Caching 

A basic optimization that will be applied to all recognizers is the decoration with the `@lru_cache` decorator from the standard `functools` module. It is recommended to use this decorator
for all recognizers
that you will write. 
Make sure you also cache the functions you import from other sources that have not been cached yet, but **do not apply them to generators or functions that return a generator expression**, as in the following example.

```python
import networkx as nx
from functools import lru_cache
from inspect import isgeneratorfunction

# Cache imported functions that are not already cached ------------------------
for function in (
    # nx.common_neighbors, # DON'T: this returns a generator expression
    nx.is_chordal,
    nx.is_forest,
):
    # WARNING: the following condition doesn't identify functions that return
    # a generator object (e.g. return (x for x in stuff)).
    if isgeneratorfunction(function):
        raise TypeError(
            function.__name__ + " is a generator function, decorating it with "
            "lru_cache will cause bugs"
        )

    # check whether function has already been lru_cached
    if not hasattr(function, "cache_info"):
        setattr(nx, function.__name__, lru_cache(maxsize=None)(function))
```

The cache size is unlimited, and this does not seem to create memory usage issues. In any case, the graph analyzer is 
able to flush the cache of each recognizer that has actually been called before processing the next input graph. 

## Calling other recognizers

Since all recognizers are cached, it is recommended that you call other recognizers as part of your code rather than trying to rewrite some of their parts from scratch.as well as to call previously written recognizers rather than trying to adapt their code: since
they have already been cached, only the first call to these functions will incur running time costs.

## Forbidden induced subgraphs characterizations

A graph class admits a *forbidden induced subgraph characterization* (hereafter FISC) when a graph belongs
to that class if and only if it contains no induced subgraph isomorphic to a graph in a prescribed forbidden
set of graphs S. That set may be finite (e.g., cographs are exactly the graphs that contain no induced $P_4$) or not
(e.g., bipartite graphs are exactly the graphs that contain no odd cycle).

### Naïve algorithms

#### Finite FISCs with only smallgraphs from ISGCI

If your graph class admits a *finite* FISC based on smallgraphs from ISGCI (see https://www.graphclasses.org/smallgraphs.html), then you should write your 
recognizer in the file `fisc_based_recognizers`. Recognizers in that file should be ordered by largest pattern size, then by increasing number of patterns. 
As an example, if a graph class could be characterized as the set of all graphs that are "frog"- and "gnu"-free, the code of your recognizer could be as simple as this:

```python
from functools import lru_cache
from graph_recognition.subgraphs import is_h_free


@lru_cache(maxsize=None)
@assign_class_id("some_isgci_id")
def is_frog_gnu_free(graph):
    return is_h_free(graph, ["frog", "gnu"])
```

TODO what if these are not known subgraphs? then we must add them as files in ..., but also recompute a few things EXPLAIN
TODO explain what is_h_free does

If you'd rather implement an algorithm yourself instead of relying on `is_h_free`, you should rely on the `dispatch_findings` function to share the conclusions of your recognizer.

For instance:

```python
from functools import lru_cache
from graph_recognition.subgraphs import _dispatch_findings
from graph_recognition.recognizers_utils import assign_class_id


@assign_class_id("gc_360")
@lru_cache(maxsize=None)
def is_c4_free(graph):
    """
    Returns True iff graph is C_{4}-free.

    See https://www.graphclasses.org/classes/gc_360

    Complexity of naïve matching: O(n^4)
    :type graph: networkx.Graph
    """
    # return is_h_free(graph, ["C_{4}"])
    # computing girth takes too long for large graphs, let's try the naive algo
    c4_deg_seq = [2, 2, 2, 2]
    # note: the following might contains sets of size 3, but it's probably
    # faster not to check their size
    is_free = all(
        degree_sequence(graph.subgraph(set(e + f))) != c4_deg_seq
        for e, f in combinations(graph.edges, 2)
    )

    _dispatch_findings(graph, ["C_{4}"], not is_free)

    return is_free
```

TODO other example where dispatch_findings is called ONLY IF ....
TODO explain dispatch_findings more and why it should be used
TODO is dispatch_findings still useful now that we have the assign_fisc decorator?
TODO actually no, so only talk about assign_fisc

### The `@assign_fisc` decorator

The `@assign_fisc` decorator allows the developer to assign a FISC to a recognizer. Doing so allows the system to propagate results: if recognizer `foo` has a FISC `F` and `foo(graph)` returns `True`, then 
no subgraph in `F` appears in `graph`, and those findings can be propagated using the `_dispatch_findings` function.

Using `@assign_fisc` is never mandatory. If the code of your recognizer boils down to calling `is_h_free`, then you do not need to bother 
with `@assign_fisc`, because `is_h_free` propagates the results of its findings through indirect calls to `_dispatch_findings`. The use of `@assign_fisc` is therefore only recommended if your code does not use `is_h_free` at all, or if your recognizer might return a value before it has a chance to call `is_h_free`.

Note that by itself, `@assign_fisc` does nothing more than adding a FISC as an attribute to your recognizer. Taking advantage of that FISC has to be done explicitly by a caller. 

### Profitable classes 

Some fiscky classes are *profitable* in the sense that they can be recognized with an algorithm that is (sometimes much) faster 
than the naïve algorithm., which means that there exists an algorithm more efficient than the
naïve algorithm to recognize them. In this case, we won't use is_h_free anymore, but we'd still like to communicate the findings of our algorithm TODO WHY? explain first that we cache all found / unfound subgraphs !


# IMPORTANT

Sometimes a naive Python algorithm will outperform GSS spectacularly. It's unclear to me when exactly this will happen, so
run tests and don't believe that just because it's true in situation X it will be true in very similar situation Y.


# BENCHMARKING

remember that we aim to use each recognizer at most once per graph, since subsequent calls will be cached. so if you bench with timeit, make sure you only bench one call, and use cache_clear on your recognizer if you have to run it again.
