





BUG: don't use this yet. I get an error I don't quite understand on instance
cayley-graph-reversal-7.g6:

```
Classifying graphs   0%|                                                                                                                                        | 0/1 [00:00<?, 0.00 graphs/s]
  Running recognizers  72%|████████████████████████████████████████████████████████████████████████████████████▋                                 |  719/1002 [08:15<03:15, 1.45 recognizers/s]
    https://www.graphclasses.org/classes/gc_629 0 [00:00, 0.00/s]                                                                                                                             
Traceback (most recent call last):
  File "/home/anthony/Travail/recherche/software/cognos2/cognos/cognos/main.py", line 374, in <module>
    main()
  File "/home/anthony/Travail/recherche/software/cognos2/cognos/cognos/main.py", line 272, in main
    GA.run_classification(manager)
  File "/home/anthony/Travail/recherche/software/cognos2/cognos/cognos/graph_analyzer.py", line 177, in run_classification
    result = function(graph)
             ^^^^^^^^^^^^^^^
  File "/home/anthony/Travail/recherche/software/cognos2/cognos/cognos/recognizers_n_3.py", line 646, in is_quasi_median
    return is_gc_628(graph) and is_weakly_modular(graph)
                                ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/anthony/Travail/recherche/software/cognos2/cognos/cognos/recognizers_n_3.py", line 617, in is_weakly_modular
    distances = all_pairs_shortest_path_length(graph)
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/anthony/Travail/recherche/software/cognos2/cognos/cognos/misc_algo.py", line 47, in all_pairs_shortest_path_length
    graph, p.starmap(
           ^^^^^^^^^^
  File "/usr/lib/python3.11/multiprocessing/pool.py", line 375, in starmap
    return self._map_async(func, iterable, starmapstar, chunksize).get()
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.11/multiprocessing/pool.py", line 774, in get
    raise self._value
  File "/usr/lib/python3.11/multiprocessing/pool.py", line 540, in _handle_tasks
    put(task)
  File "/usr/lib/python3.11/multiprocessing/connection.py", line 205, in send
    self._send_bytes(_ForkingPickler.dumps(obj))
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.11/multiprocessing/reduction.py", line 51, in dumps
    cls(buf, protocol).dump(obj)
_pickle.PicklingError: Can't pickle <functools._lru_cache_wrapper object at 0x7fd83a739dd0>: it's not the same object as networkx.algorithms.shortest_paths.unweighted.single_source_shortest_path_length
```

it does work if I don't cache nx.single_source_shortest_path_length
so let's try again but with the right check on top of this file
if again it doesn't work, then it'd be an issue related to caching AND mp


@lru_cache(maxsize=None)  # compromise: parallel version but not cached
def all_pairs_shortest_path_length(graph, cutoff=None):
    """Computes the shortest path lengths between all nodes in `G`.

    Trivial parallel version of what's available in networkx 2.8.8.
    """
    return dict(nx.all_pairs_shortest_path_length(graph, cutoff))
    # TODO bug with what's below, .... ???? pickling error see above
    # length = nx.single_source_shortest_path_length
    # with mp.Pool() as p:
    #     return dict(
    #         zip(
    #             graph,
    #             p.starmap(func=length, iterable=((graph, n, cutoff) for n in graph)),
    #         )
    #     )

