# OPEN



- [ ] I should be able to use "unknown" ids, right now I can't:
```pycon

>>> from classification_digraph import ClassificationDigraph
>>> classification = ClassificationDigraph()
>>> classification.label_and_propagate("gc_69", True, "see Godsil and Royle")
---------------------------------------------------------------------------
KeyError                                  Traceback (most recent call last)
Cell In [11], line 1
----> 1 classification.label_and_propagate("gc_69", True, "see Godsil and Royle")

File ~/Travail/recherche/software/cognos2/cognos/src/classification_digraph.py:95, in ClassificationDigraph.label_and_propagate(self, class_id, bool_val, reason)
     93 # set label and associated color
     94 val = [self.negative, self.positive][bool_val]
---> 95 self.nodes[class_id]["category"] = val
     96 self.nodes[class_id]["color"] = self.node_colors[val]
     97 self.nodes[class_id]["reason"] = reason

File ~/Travail/recherche/software/cognos2/cognos/src/.venv/lib/python3.11/site-packages/networkx/classes/reportviews.py:196, in NodeView.__getitem__(self, n)
    191 if isinstance(n, slice):
    192     raise nx.NetworkXError(
    193         f"{type(self).__name__} does not support slicing, "
    194         f"try list(G.nodes)[{n.start}:{n.stop}:{n.step}]"
    195     )
--> 196 return self._nodes[n]

KeyError: 'gc_69'
```

User is not supposed to know which equivalent id has been stored in the classification digraph. Check what I do in GraphAnalyzer

- [ ] dubious results to investigate: 
 
```commandline
pypy3 main.py -i ../../data/cographConnected7.g6

100.00 % are (K_{4,4},P_{5})-free --- https://www.graphclasses.org/classes/gc_432
    class has 0 unidentified children
    class has 6 further unidentified descendants
         (K_{3,3},co(C_{n+4}))-free --- https://www.graphclasses.org/classes/AUTO_2107 Polynomial
         (co(C_{n+3} U K_{1}),co-diamond,co-paw)-free --- https://www.graphclasses.org/classes/AUTO_2276 Unknown to ISGCI
         co-2-subdivision --- https://www.graphclasses.org/classes/gc_1078 Polynomial
         almost CIS --- https://www.graphclasses.org/classes/gc_833 Open
         hamiltonian ∩ split --- https://www.graphclasses.org/classes/gc_1095 Unknown to ISGCI
         boxicity 2 ∩ co-bipartite --- https://www.graphclasses.org/classes/gc_1180 Unknown to ISGCI
```

"class has 0 unidentified children" means that we've classified all maximal subclasses;
        but what is their status? if they're negative, then the graphs cannot be (K_{4,4},P_{5})-free
            -> no, this argument is wrong: bipartite contains tree, but all bipartite graphs are not trees
        alright, so they must be negative; but then how are we not rid of all their descendants?



- many more subgraph matchers objects are created than what I expected; for

time python3 main.py -i ~/Travail/recherche/software/cayley-graphs/cayley-graphs-all-transposition-trees-5.g6

which contains 3 graphs, I get 363 files ... ??? I should only get 3

well, must be because many functions call is_h_free on subgraphs ...



- crash with --positive gc_441:

```commandline
Traceback (most recent call last):
  File "/home/anthony/Travail/recherche/software/cognos2/cognos/cognos/main.py", line 374, in <module>
    main()
  File "/home/anthony/Travail/recherche/software/cognos2/cognos/cognos/main.py", line 265, in main
    GA.acknowledge_positive_classes(args.positive)
  File "/home/anthony/Travail/recherche/software/cognos2/cognos/cognos/graph_analyzer.py", line 233, in acknowledge_positive_classes
    self.validate_and_remove_ancestors(
  File "/home/anthony/Travail/recherche/software/cognos2/cognos/cognos/graph_analyzer.py", line 208, in validate_and_remove_ancestors
    graph.nodes[class_id]["category"] = "+"
    ~~~~~~~~~~~^^^^^^^^^^
  File "/usr/lib/python3/dist-packages/networkx/classes/reportviews.py", line 194, in __getitem__
    return self._nodes[n]
           ~~~~~~~~~~~^^^
KeyError: 'gc_441'
```


SOLUTION: generated recognizers (and optimized ones) must receive class ids!!!!

no, I did that and it's not the problem. --positive gc_1045, which is equivalent, works, so there's something wrong in the way
I handle provided positive and negative classes



# PARTIALLY FIXED

- co(C_{4}) LAD file does not exist. I created it but it should have been done automatically, find out where the flaw is (its complement exists and is 2K_{2})
    ok but that's not enough, I have to rebuild the smallgraph inclusion graph afterwards
    I don't want to remember to do that, find a way to detect that it's outdated (ls smallgraphs I guess, then compare names with keys)
    nope, still crashes:

      File "/home/anthony/Travail/recherche/software/cognos2/cognos/cognos/subgraphs.py", line 145, in no_match
    raise ValueError("names", missing_names, "are unknown")
ValueError: ('names', {'co(C_{4})'}, 'are unknown')

ok, found the problem: I need to add this to smallgraphs.missing_smallgraphs
THEN I need to rebuild the smallgraph inclusion graph:

python3 smallgraphs.py --build-inclusion-graph


# FIXED

- [x] $ python3 main.py -i cayley-graph-prefix-reversal-7.g6 --print-unknown-descendants --positive gc_359 

Classifying graphs:   0%|                                                                                                    | 0/1 [00:01<?, ? graph/s]
Traceback (most recent call last):
  File "/home/anthony/Travail/recherche/software/cognos2/cognos/src/main.py", line 243, in <module>
    main()
  File "/home/anthony/Travail/recherche/software/cognos2/cognos/src/main.py", line 219, in main
    analyzer.run_classification(args.input)
  File "/home/anthony/Travail/recherche/software/cognos2/cognos/src/graph_analyzer.py", line 164, in run_classification
    self._get_stored_class_id(class_id),
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/anthony/Travail/recherche/software/cognos2/cognos/src/graph_analyzer.py", line 293, in _get_stored_class_id
    eq_class_id = other_ids.intersection(self.isgci_graph.nodes).pop()
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'pop from an empty set'

`GraphAnalyzer._get_stored_class_id` was buggy

- [x] provided positive classes are ignored; my fault, I changed the way I initialized classifications, and was iterating over an empty set
- [x] `--capabilities`: tries to connect to the smallgraphs page. the program must be able to work offline
    I downloaded the file manually and changed the code in all_smallgraphs_by_order
- [x] time python3 cognos.py -i ../data/g09-class2.g6 -----> OSError: [Errno 24] Too many open files
    -> fixed: i was opening a NamedTemporaryFile in SubgraphMatcher.__init__ but never closing it
- [x] networkx.exception.NetworkXPointlessConcept: ('Connectivity is undefined ', 'for the null graph.')
    I fixed it by providing my own version of is_connected and deciding that a null graph is disconnected
- [x] graph_formats.py:lad_file_to_nx_graph disregarded the order of the graph,
    thereby failing to create vertices even when there were no edges
- [x] fixed flawed recognizers in fisc_based_recognizers: I was setting and
    propagating the wrong values (remember that if G is bla-free, then we must
    set_and_propagate(False), since we're setting the
- [x] time python3 cognos.py -i ../data/g09-class2.g6 -----> OSError: [Errno 24] Too many open files
    -> fixed: i was opening a NamedTemporaryFile in SubgraphMatcher.__init__ but never closing it

# DISAPPEARED

20250514: time python3 main.py -i ../../data/selfcomp12.g6 --print-unknown-descendants --todo

Classifying graphs: 100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████| 720/720 [02:52<00:00,  4.17 graph/s]
                                                                                                                                                                             
Summary of findings
-------------------
100.00% are K_{7}-free --- https://www.graphclasses.org/classes/gc_1343
    class has 1 unidentified maximal subclasses
         CPG --- https://www.graphclasses.org/classes/gc_1336 NP-complete

    class has 9 further unidentified descendants
Traceback (most recent call last):
  File "/home/anthony/Travail/recherche/software/cognos2/cognos/cognos/main.py", line 269, in <module>
    main()
  File "/home/anthony/Travail/recherche/software/cognos2/cognos/cognos/main.py", line 246, in main
    analyzer.print_summary_of_findings(args.print_unknown_descendants, args.todo)
  File "/home/anthony/Travail/recherche/software/cognos2/cognos/cognos/graph_analyzer.py", line 424, in print_summary_of_findings
    ids_to_names[child],
    ~~~~~~~~~~~~^^^^^^^
KeyError: 'AUTO_136'

older:

I'm getting another weird bug:

networkx.exception.NetworkXError: The node co(T_{3}) is not in the digraph.
networkx.exception.NetworkXError: The node co(X_{81}) is not in the digraph.

even though the LAD files exist and I've rebuilt the smallgraph_inclusion_graph ...

yeah but how do i reproduce that bug?






20250704: apex:

``` 
$ pypy3 main.py -i ../../data/cographConnected7.g6 
... 
OSError: [Errno 24] Too many open files: '/tmp/tmpkzhgkm_m'
```

bug seems to be in /home/anthony/Travail/recherche/software/cognos2/cognos/cognos/recognizers_n_2.py: is_apex
    probably due to multiprocessing

This no longer happens with python3; I can't use pypy3 at the moment because its latest version does not feature the match syntax



20250704: time pypy3 main.py -i cayley-graph-reversal-8.g6 : crash. Error seems to stem from is_AUTO_1442:

```commandline
  File "/home/anthony/Travail/recherche/software/cognos2/cognos/cognos/main.py", line 306, in <module>
    main()
  File "/home/anthony/Travail/recherche/software/cognos2/cognos/cognos/main.py", line 288, in main
    analyzer.run_classification()
  File "/home/anthony/Travail/recherche/software/cognos2/cognos/cognos/graph_analyzer.py", line 119, in run_classification
    result = function(graph)
  File "/usr/lib/pypy3.9/functools.py", line 564, in wrapper
    result = user_function(*args, **kwds)
  File "/home/anthony/Travail/recherche/software/cognos2/cognos/cognos/graph_recognition/generated_recognizers.py", line 3227, in is_AUTO_1442
    return is_h_free(graph, ['K_{4}', 'S_{3}'])
  File "/home/anthony/Travail/recherche/software/cognos2/cognos/cognos/graph_recognition/generated_recognizers.py", line 40, in is_h_free
    return MATCHERS[graph].no_match(subgraphs)
  File "/home/anthony/Travail/recherche/software/cognos2/cognos/cognos/graph_recognition/subgraphs.py", line 267, in no_match
    self.set_and_propagate([pattern], self.find_induced(pattern))
  File "/home/anthony/Travail/recherche/software/cognos2/cognos/cognos/graph_recognition/subgraphs.py", line 134, in find_induced
    [subpattern], self.find_induced(subpattern)
  File "/home/anthony/Travail/recherche/software/cognos2/cognos/cognos/graph_recognition/subgraphs.py", line 221, in find_induced
    output = subprocess.check_output(glasgow_command).decode()
  File "/usr/lib/pypy3.9/subprocess.py", line 424, in check_output
    return run(*popenargs, stdout=PIPE, timeout=timeout, check=True,
  File "/usr/lib/pypy3.9/subprocess.py", line 528, in run
    raise CalledProcessError(retcode, process.args,
subprocess.CalledProcessError: Command '['/home/anthony/Travail/recherche/software/cognos2/cognos/cognos/graph_recognition/./glasgow_subgraph_solver', '--format', 'lad', '--induced', '/home/anthony/Travail/recherche/software/cognos2/cognos/cognos/graph_recognition/smallgraphs/triangle', '/tmp/tmp750zcpo_/r7bmrkw6']' returned non-zero exit status 1.
```

We get a "Error: std::bad_array_new_length" in the output
also for cayley-graph-block-interchange-8.s6
are our graphs too large for GSS?
n = 7 is fine

20250704 python3 main.py -i ../../data/trees10.g6 reports among others that

100.00 % are (4K_{1},K_{4})-free --- https://www.graphclasses.org/classes/gc_515

but that can't be right: it is easy to build trees on fewer vertices that contain a 4K_1;
in fact, with n vertices there's always K_{1, n-1} which contains a (n-1)K_1

does not seem to occur anymore, not sure what was wrong

