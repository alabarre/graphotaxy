from graph_recognition.recognizers_utils import assign_inherited_fisc---
title: Writing recognizers for `graphotaxy`
author: Anthony Labarre
date: 2024-2026
---

This document provides the information needed to be able to write recognizers.

# The basics

A *recognizer* is a function that takes a graph as input and returns `True` if the graph belongs to a specific graph
class, and `False` otherwise. The basic skeleton for writing a recognizer is therefore simply:

```python
def is_member(graph) -> bool:
    # recognition algorithm
```

This is sufficient for recognition purposes. `graphotaxy`, however, uses a `GraphAnalyzer` which needs to associate each recognizer to a specific graph class. A graph class is identified by a case-sensitive ISGCI id, which is a string formatted as
`"gc_number"` or `"AUTO_number"`. The above recognizer will be tied to the graph class with id `"gc_xxx"` using the custom `assign_class_id` decorator as follows:

```python
from graph_recognition.recognizers_utils import assign_class_id


@assign_class_id("gc_xxx")
def is_member(graph) -> bool:
    # recognition algorithm
```

In addition to associating recognizers with actual graph classes, this decorator also makes it easy for the system to identify and load recognizers using a 
`GraphAnalyzer` object. In order to achieve that, the file in which you write your recognizers, which the `GraphAnalyzer` object must be instructed 
to load, must provide a `RECOGNIZERS` dictionary. All you need to do is insert this code segment at the end of you file:

```python
RECOGNIZERS = current_module_recognizers(os.path.basename(__file__).strip(".py"))
```

Another advantage of this approach is the ability to easily enable or disable a specific recognizer, e.g. for debugging purposes: 
simply comment out the `@assign_class_id` decoration before your recognizer, and the `GraphAnalyzer` object will not load it, since the 
`RECOGNIZERS` dictionary will no longer contain it.

If you need to include third-party recognizers in your file, you will need to associate a class id to each of those recognizers as well. 
You don't have to decorate them with `@assign_class_id` to achieve this: you can simply update the `RECOGNIZERS` dictionary as follows:

```python
RECOGNIZERS.update(
   {
        "gc_1149": nx.is_regular,
        "gc_342": nx.is_tree,
        "gc_771": nx.is_biconnected,
    }
)
```

# Before adding a new recognizer

Make sure the system does not already know how to recognize your class, or a class equivalent to it. To do that, simply provide the ISGCI id of your class to the `--knows` option, like so:

```commandline
$ python3 main.py --knows gc_400
gc_400: found recognizer is_k_23_p_hole_free in graph_recognition.recognizers_n_5
$ python3 main.py --knows gc_SOME_MADE_UP_ID
gc_SOME_MADE_UP_ID: no recognizer available
```

# Organizing recognizers

Recognizers are roughly ordered by increasing worst-case complexity. They are scattered among three categories of files:

1. `fisc_based_recognizers`, which are recognizers for graph classes whose recognition is based on a *forbidden induced
   subgraph characterization* (hereafter FISC);
2. `recognizers_n`, `recognizers_n_2`, `recognizers_n_3`, ... files, which respectively contain recognizers with a
   running time of $O(m+n)$, $O(n^2)$, $O(n^3)$, ...;
3. `profitable_hereditary_constant`, `profitable_hereditary_n`, `profitable_hereditary_n_2`,
   `profitable_hereditary_n_3`, ... files, which follow the same approach as the previous category: the difference is
   that the recognizers they contain concern FISC-based recognizers with a better running time than the naïve approach.

When you write a recognizer, make sure you place it in the right file depending on its category as outlined above:

- if you are writing a naïve search for forbidden induced subgraphs (whether manually or by using external tools), your recognizer should appear in `fisc_based_recognizers.py`;
- if you are writing a more efficient recognizer for a FISC-based class, then it should appear in one of the `profitable_hereditary_*.py` files (the right one depends on the complexity of your recognizer).
- otherwise, select the right `recognizers_*.py` file according to the complexity of your recognizer.

A `GraphAnalyzer` will run recognizers by increasing complexity, hoping to avoid running the more costly ones. The first algorithms to be run are the profitable ones, then the fisc-based recognizers, and finally the other recognizers. Each recognizer is then run in the order in which it appears in its respective file.

If you are writing a recognizer for a FISC-based class, make sure you read [the relevant section of this document](#Forbidden-induced-subgraphs-characterizations).

# Efficiency

Here are several guidelines for writing efficient recognizers. 

## Caching 

A basic optimization that will be applied to all recognizers is the decoration with the `lru_cache` decorator from the standard `functools` module. It is recommended to use this decorator for all recognizers that you will write, so our basic running example becomes:

```python
from functools import lru_cache
from graph_recognition.recognizers_utils import assign_class_id


@assign_class_id("gc_xxx")
@lru_cache(maxsize=None)
def is_member(graph) -> bool:
    # recognition algorithm
```

The cache size is unlimited, and this does not seem to create memory usage issues thus far. In any case, `GraphAnalyzer` clears the cache of each recognizer that has actually been called before processing the next input graph, since the information that was cached is unlikely to be useful for a different input.

Make sure you also cache the functions you import from other sources if need be, as in the following example.

```python
# Cache imported functions that are not already cached --------------------------------------------
import networkx as nx
from graph_recognition.recognizers_utils import cached_function

__functions_to_cache = [
    # nx.biconnected_components,  # DON'T: it returns a generator
    nx.is_biconnected,
    nx.is_k_edge_connected,
    nx.is_regular,
    nx.non_neighbors,
]
for i, function in enumerate(__functions_to_cache):
    __functions_to_cache[i] = cached_function(function)
```

`cached_function` is the recommended tool for this: it returns the function decorated with `lru_cache` if it is safe to do so, i.e.:

- if the function is not a generator function and does not return a generator either;
- if the function has not already been cached --- otherwise the previous cache and all its benefits would be lost.

Otherwise, it returns the original function.

## Calling other recognizers

Since all recognizers are cached, it is recommended that you call other recognizers as part of your code rather than trying to rewrite some of their parts from scratch just to avoid function calls.

## Forbidden induced subgraphs characterizations

A graph class admits a *forbidden induced subgraph characterization* (hereafter FISC) when a graph belongs
to that class if and only if it contains no induced subgraph isomorphic to a graph in a prescribed forbidden
set of graphs S. That set may be finite (e.g., cographs are exactly the graphs that contain no induced $P_4$) or not
(e.g., bipartite graphs are exactly the graphs that contain no odd cycle).

### Naïve algorithms

<!--#### Finite FISCs with only smallgraphs from ISGCI-->

If your graph class admits a *finite* FISC based on smallgraphs from ISGCI (see https://www.graphclasses.org/smallgraphs.html), then writing a naïve recognizer for that class reduces to calling the `is_h_free` function. As an example, if a graph class could be characterized as the set of all graphs that are "frog"- and "gnu"-free, the code of your recognizer could be as simple as this:

```python
from functools import lru_cache
from graph_recognition.recognizers_utils import assign_class_id
from graph_recognition.subgraphs import is_h_free


@lru_cache(maxsize=None)
@assign_class_id("some_isgci_id")
def is_frog_gnu_free(graph):
    return is_h_free(graph, ["frog", "gnu"])
```

`is_h_free` performs a lot of tricks to avoid actually running the search for those subgraphs, the details of which appear in `graph_recognition.smallgraphs.py` (TODO: explain them here too). If there is no way around it, it ultimately calls the Glasgow Subgraph Solver to run the actual search.


If for any reason you would like to implement the naïve search yourself, you can. In that case, just make sure you decorate your recognizer with the decorator `assign_fisc`, whose parameter should be your FISC for that class. For instance: 



```python
from functools import lru_cache
from graph_recognition.recognizers_utils import assign_class_id, assign_fisc

@assign_fisc(["frog", "gnu"])
@assign_class_id("some_isgci_id")
@lru_cache(maxsize=None)
def is_frog_gnu_free(graph):
    # any algorithm for recognizing (frog, gnu)-free graph
```


### The `assign_fisc` decorator

The `assign_fisc` decorator allows the developer to assign a FISC to a recognizer. Doing so allows the system to propagate results: if recognizer `foo` has a FISC `F` and `foo(graph)` returns `True`, then 
no subgraph in `F` appears in `graph`, and those findings are propagated using the `_dispatch_findings` function.

Using `assign_fisc` is never mandatory, but always recommended: not only can the FISC be used by the `GraphAnalyzer` instance to propagate findings, but the analyzer also inspects the FISC to avoid running the recognizer in the first place if it already knows that one of the forbidden subgraphs appears in the target graph.

Note that by itself, `assign_fisc` does nothing more than adding a FISC as an attribute to your recognizer. The code in `subgraphs.py` takes advantage of that attribute.

### The `assign_inherited_fisc` decorator

Some recognizers rely on calls to other recognizers to which a FISC has been assigned using `assign_fisc`. However, the analyzer cannot take advantage of the FISCs of the constituent classes to avoid running a recognizer that relies on them, since those callees have not been run yet. The solution would be to copy and combine those FISCs into a new FISC to assign to the caller, but that would be tedious and a nightmare to maintain. Fortunately, the `assign_inherited_fisc` decorator handles that job for us.

For instance, consider the following recognizer:

```python
@assign_inherited_fisc()
@assign_class_id("gc_847")
@lru_cache(maxsize=None)
def is_binary_tree(graph: nx.Graph) -> bool:
    return is_maximum_degree_3(graph) and is_tree(graph)
```

Both `is_maximum_degree_3` and `is_tree` are decorated with `assign_fisc`. Thanks to `assign_inherited_fisc()`, `is_binary_tree` now also has a FISC which is the union of the FISCs of the two recognizers that are called in its code.

**Use `assign_inherited_fisc()` with caution:** 

1. the FISCs of **all** callees in the code of the decorated recognizer are gathered and used, and this might lead to errors. For example, the following function **must not** be decorated with `assign_inherited_fisc`:
   ```python
   @assign_class_id("gc_1361")
   @lru_cache(maxsize=None)
   def is_bipartite_or_co_bipartite_or_split(graph: nx.Graph) -> bool:
      return is_bipartite(graph) or is_co_bipartite(graph) or is_split(graph)
   ```
   If it were, then the FISC of bipartite graphs could be used to propagate findings even if the graph is not bipartite.
2. the decorator does not dig into your use cases: if your recognizer calls a FISC-based recognizer on a different graph than the one you gave as input, then the FISC of that recognizer will be associated to your input graph and will lead to wrong results too.


### Smarter algorithms

A *profitable* class is a class with a FISC for which there exists a (sometimes much) faster-than-naïve recognition algorithm. A widely known example is that of [cographs](https://www.graphclasses.org/classes/gc_151.html), which are equivalent to graphs without an induced path on 4 vertices, and which can be recognized in $O(m+n)$ time whereas a naïve algorithm would run in $O(n^4)$. If you want to implement such an algorithm, make sure you decorate your recognizer with `assign_fisc`, and place it in one of the `profitable_hereditary_*.py` files instead of the `fisc_based_recognizers.py` file.

### Profitable classes 

Some fiscky classes are *profitable* in the sense that they can be recognized with an algorithm that is (sometimes much) faster 
than the naïve algorithm., which means that there exists an algorithm more efficient than the
naïve algorithm to recognize them. In this case, we won't use is_h_free anymore, but we'd still like to communicate the findings of our algorithm TODO WHY? explain first that we cache all found / unfound subgraphs !
