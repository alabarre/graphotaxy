# General

- [ ] find a generic way to cache functions from submodules; for now, I just do it manually, like so:
- [ ] benchmark each "homemade" recognizer against GSS and tweak whatever needs to be tweaked, for instance:
    - decide that from a certain size we'd better switch to GSS or the other way around
    - ... ?
- [ ] add an option to disable fisc based recognizers, since they're time-consuming and user might "know that they're
  not interested" in those classes

```python
import networkx as nx
from functools import lru_cache

# check whether function has already been lru_cached
if not hasattr(nx.bipartite.sets, "cache_info"):
    setattr(nx.bipartite, "sets", lru_cache(maxsize=None)(nx.bipartite.sets))
```

- [x] ~~use the glasgow clique solver instead of the subgraph solver for K_4, ...~~
    - shouldn't be useful anymore, I wrote my function to do exhaustive search in a smarter way
- [ ] since tralda needs numpy anyway, see what benefits I can obtain using numpy
- [x] build a tool to compute a basis for forbidden induced subgraphs
- [ ] and then, build a tool to automatically deduce a minimal fisc for profitable recognizers

# Improvements to `networkx`

- [x] `nx.is_at_free` calls `find_asteroidal_triple` in `asteroidal.py`, which builds the complement of the graph. We
  should iterate on G's nonedges directly.
    - submitted on 2024-11-25 and accepted (https://github.com/networkx/networkx/pull/7736)

# Missing recognizers

## fisc_based_recognizers

- [x] `is_p4_tidy` allows us to implement the recognizer for
  subclass   https://www.graphclasses.org/classes/AUTO_3683.html
  and related (complement, etc)

## recognizers_n_2

- [ ] https://www.graphclasses.org/classes/gc_134.html but I need a recognizer for circular-arc
- [ ] TODO apparently helly circular arc graphs can be recognized in cubic time, see
  https://www.combinatorics.org/ojs/index.php/eljc/article/download/DS17/pdf/ page 12
  can be done in linear time too

## recognizers_n_4

- [ ] is_2_2_colorable; algo is pretty similar to is_2_1_colorable in recognizers_n_3

```python
from functools import lru_cache
import networkx as nx
from itertools import product


@lru_cache(maxsize=None)
def is_equimatchable(graph: nx.Graph) -> bool:
    """

    https://sci-hub.ru/10.1016/j.ipl.2013.08.002

    TODO WIP
    @type graph: nx.Graph
    @param graph:
    @return:
    """
    M = nx.max_weight_matching(graph, maxcardinality=True)
    saturated = set.union(*map(set, M))
    unsaturated = set(graph).difference(saturated)  # = Exp(M) in paper
    answer = True
    visited = set()
    while answer:
        # find a saturated, non visited x such that the set S_M(x) is not empty
        x, unsat_n_x, s_m_x = [None] * 3
        found = False
        for x in saturated.difference(visited):
            unsat_n_x = set(graph[x]) & unsaturated
            s_m_x = {
                        y
                        for y in saturated
                        if not graph.has_edge(x, y) and
                           # at most one unsaturated neighbor
                           len(set(graph[y]) & unsaturated) <= 1 and
                           # unsaturated neighbors of y are a strict subset of saturated neighbors of x
                           (set(graph[y]) & unsaturated) < unsat_n_x
                    } - {x}
            if s_m_x:
                found = True
                break

        # if no such x exists, stop
        if not found:
            break

        if len(unsat_n_x) == 1:
            # TODO
            for y in s_m_x:
                if answer:
                    s_m_x_y = {z for z in s_m_x if not graph.has_edge(z, y)}
                    # build graph H_M
                    h_m = graph.copy()
                    # add vertices A, B_1, B_2
                    b_nodes = ["B_" + str(i) for i in range(1, len(unsat_n_x) + 2)]
                    h_m.add_nodes_from(["A"] + b_nodes)
                    # removing Exp(M) \ {x′}  # NOTE: assuming they mean x, not x'
                    # TODO mailed author on 2024-06-19 for explanations
                    h_m.remove_nodes_from(unsaturated - {x})
                    # TODO add edges (x, A), (y, B_2)
                    # TODO add edges (z, B_1) for each z in s_m_x_y
                    # TODO remove edge (x, x')

            pass
        else:
            # build graph G_M
            g_m = graph.copy()
            # add vertices A, B_1, B_2, ..., B_{len(unsat_n_x) + 1}
            b_nodes = ["B_" + str(i) for i in range(1, len(unsat_n_x) + 2)]
            g_m.add_nodes_from(["A"] + b_nodes)
            # remove unsaturated vertices not adjacent to x
            g_m.remove_nodes_from(unsaturated - set(graph[x]))
            # connect x to "A" and y to all "B" nodes for each y in S_M(x)
            g_m.add_edge(x, "A")
            g_m.add_edges_from(product(s_m_x, b_nodes))
            # remove edges incident to x if the other endpoint is unsaturated
            g_m.remove_edges_from([(x, y) for y in set(graph[x]) & unsaturated])
            # if the resulting graph has a perfect matching, answer is False
            if nx.is_perfect_matching(
                    g_m, nx.max_weight_matching(g_m, maxcardinality=True)
            ):
                answer = False

    return answer
```

## recognizers_n_5

- [ ] https://www.combinatorics.org/ojs/index.php/eljc/article/download/DS17/pdf/ gives a polytime algo for recognizing
  biclique-helly graphs

# Faster algorithms and other improvements

## fisc_based_recognizers

- [x] https://github.com/david-schaller/tralda contains an implementation of a linear-time algo for cograph
  recognition (i.e. P_4-free graphs, i.e. currently is_gc_152)
    - find out "who" else can benefit from that
- [ ] in general, there are faster algorithms for finding cycles of a specific length, have a look
  at http://theory.stanford.edu/~virgi/cs267/papers/cycles-ayz.pdf; this would allow us to bypass quite a few calls to
  is_h_free
    - note : I haven't checked if there have been improvements to that 30-year-old paper

## misc_algo

```python
from functools import lru_cache
import networkx as nx


@lru_cache(maxsize=None)
def complement(graph: nx.Graph) -> nx.Graph:
    """Returns the complement of the graph. Only exists so the result can be
    cached.

    :param graph:
    :type graph: networkx.Graph
    :return:
    """
    # TODO dropping this for now, results are disappointing
    """

    # TODO nauty-complg is fast, but loading the result into memory is very
    #  slow; I think I'll need to implement my_read_sparse6 using nauty-showg ...
    with NamedTemporaryFile(delete=False) as graph_file:
        nx.write_sparse6(graph, graph_file, header=False)
        print("wrote orig to", graph_file.name)

    with NamedTemporaryFile(delete=False) as compl_file:
        subprocess.call(("nauty-complg", graph_file.name), stdout=compl_file)
        print("wrote compl to", compl_file.name)

    # info on timing: on a graph with 8! vertices:
    #   complg takes about 10 seconds
    #   showg  takes about 40 seconds
    #   but then memory issues as we're reading it all; can we process the output line by line?
    #   -l0 puts everythin on a single line, and not using it means I don't know where output is cut; so let's use -a (adj mat) instead
    # TODO still have massive memory issues even when piping and processing lines one by one
    #   should I write output to yet another file and read it line by line?
    current_graph = nx.empty_graph(graph.number_of_nodes())
    with subprocess.Popen(("nauty-showg", "-a", "-t", "-q", compl_file.name), stdout=subprocess.PIPE) as proc:#.decode('UTF-8').split("\n")
        v = -1
        for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):  # or another encoding
            if line.startswith(str(graph.number_of_nodes())):
                continue
            # find all positions where a 1 appears in current line
            neighbors = {pos for pos, elem in enumerate(line) if elem == "1"}
            current_graph.add_edges_from((v, w) for w in neighbors)
            v += 1
            print("wrote line", v)
            #print(line)

    return current_graph



    # TODO there must be something wrong in from_graph6_bytes; writing the complement with nauty-complg is very fast, so I don't know what's taking ages here ...
    return nx.read_sparse6(compl_file.name)
    """
    # former version:
    return nx.complement(graph)
```

## `profitable_hereditary_n_2`

- [x] `is_p4_co_cycle_free`: implement is_co_forest so we can avoid computing the complement; low priority, since it's
  the only place so far where this would be useful
- [ ] `is_co_chordal`:     # TODO on large graphs, computing the complement might not be the bottleneck: when I kill the
  # program, it's usually in is_chordal
  # for benchmarking purpose:
  # import time
  # start = time.perf_counter()
  # print("\ncomputing complement... ", end="")
  # end = time.perf_counter()
  # print("done in", end - start)

## `profitable_hereditary_n_3`

- [ ] is_co_p3_free:  would it be smarter to do: for each edge, check that neither u nor v has non-neighbors?
  """
  for u, v in graph.edges:
  if not nx.non_neighbors(graph, u) and not nx.non_neighbors(graph, v):
  return False

  return True
  """
- [ ] is_co_at_free: can we unpack further configurations for the FISC?

## `profitable_hereditary_n_4`

- [ ] ($C_4$, diamond)-free graphs can be recognized in $O(m\Delta)$ time or in
  time $O(m^{2/3}n)\le O(n^{7/3}$ $<O(n^4)$) according to https://doi.org/10.1016/j.dam.2010.04.015
    - implement less efficient algo first, it seems simple; and then, switch between both when I have both
    - low priority: it's only used by one other recognizer
- [ ] is_co_chordal_and_co_claw_free very slow, probably because of is_co_chordal

## `recognizers_n`

- [x] is_co_connected function; easy to implement, but OTOH it's only useful for gc_270 for now
- [ ] is there a partial fisc for 2-trees? no info in ISGCI or google
- [ ] is there a partial fisc for star convex? no info in ISGCI, ask google
- [ ] is_co_chordal:

```python
import networkx as nx
from graph_recognition.recognizers_utils import assign_class_id
from functools import lru_cache
from networkx import is_chordal, complement


@assign_class_id("gc_145")
@lru_cache(maxsize=None)
def is_co_chordal(graph: nx.Graph) -> bool:
    """
    Returns True iff graph is co-chordal.

    https://www.graphclasses.org/classes/gc_145.html

    Complexity: O(m+n).

    @param graph:
    @return:
    """
    return is_chordal(complement(graph))
    # TODO code below still buggy, reverting to the naive way for now
    # TODO I think it's because we're not supposed to use lex bfs, but rather
    #  the modification they describe on page 66
    # using Algorithm 5 in https://doi.org/10.1016/S0304-3975(97)00241-7
    pi = list(lex_bfs(graph))

    # invert pi so we can compute positions in O(1) time; I'm using a dict
    # instead of a list so the function doesn't crash on permutations of sets
    # other than {0, 1, ..., n-1} ("holes" may appear when running lex_bfs on
    # subgraphs for instance)
    position = dict()
    for i, elem in enumerate(pi):
        position[elem] = i

    right_neighbors = dict()
    parent = dict()
    tree = nx.DiGraph()
    for x in graph:
        # store all neighbors of x to its right (i.e., those "after" x in pi)
        right_neighbors[x] = {v for v in graph[x] if position[v] > position[x]}
        # store the first non-neighbor of x "after" x in pi
        parent[x] = None
        parents_of_x = sorted(nx.non_neighbors(graph, x), key=position.get)
        if parents_of_x:
            for y in parents_of_x:
                if position[y] > position[x]:
                    parent[x] = y
                    break

        if parent[x] is not None:
            tree.add_edge(parent[x], x)

    return all(
        right_neighbors[parent[x]] <= right_neighbors[x]
        for x in graph
        if parent[x] is not None
    )
```

## recognizers_n_2

- [ ] faster recognition of apex graphs: there is a linear time
  algorithm (http://research.nii.ac.jp/~k_keniti/focsfinal.pdf) but it seems hard to implement
- gc_277:
    - [ ] serious bottleneck for large graphs. I managed to avoid computing the complement, but this is still slow.
    - [ ] find other possibly helpful properties to avoid running the algo
- complement is a bottleneck for the following classes:
    - [ ] AUTO_2465
    - [ ] gc_744
    - [ ] gc_879; possible lead:  A graph is a quasi-line graph iff the closed neighbourhood of every vertex is the
      union of two cliques.
      yes but how do you check that it is the union of 2 cliques? the union is not disjoint! (
      see https://doi.org/10.1016/j.jctb.2012.07.005)
- [ ] there is a `empty_graph_by_removing_vertices_2` in this file, but there's also a
  `empty_graph_by_removing_vertices` in
  misc_algo.py. Find out which is better (I started doing that in the `main` function)
- [ ] AUTO_1745: co-girth computation would be useful, but for now only for this class, so this would be very low
  priority if I ever do it
- [ ] https://www.graphclasses.org/classes/gc_352:     the bottleneck is probably building the graph in the first place;
  I don't know of a faster available way to obtain all disjoint pairs; more_itertools doesn't seem to have one either
- [ ] comparability:    a linear-time algorithm exists: see Algorithm 8 page 73
  in https://doi.org/10.1016/S0304-3975(97)00241-7
- [ ] check if even a partial fisc exists for:
    - is_dilworth_3
    - is_dilworth_4
    - is_apex
    - is_edge_regular
    - is_mock_threshold
- [x] is_minimally_imperfect: write is_co_connected function so we can avoid building the complement
- [ ] is_co_b_chordal_and_perfect: this is a profitable O(n^2) class, move and add fisc; can't (yet?): this results in a
  circular import

## recognizers_n_3

- [ ] is_chordal_and_maximal_planar could be profitable, but a circular import issue will arise if moved
- [ ] is_median:  there is a much more efficient, subquadratic algo:
  https://doi.org/10.1016/S0304-3975(97)00136-9
  does not seem too hard to implement
- [ ] is_interval_regular: improvement?
- [ ] is_median_and_planar: exists linear time algo
- [ ] is_co_paw_odd_anti_hole_free: improvable? A graph G is paw-free ∩ perfect iff each component of G is bipartite or
  complete
  multipartite.
  so a graph is co(paw-free ∩ perfect) if each co-component of G is co-bipartite or
  co-complete-multipartite
  I know how to test co-bipartiteness, but what about co-complete-multipartiteness? doesn't that simply amount to
  testing P_3-freeness?

```python
from networkx import all_pairs_shortest_path_length
from itertools import combinations

# """
# NEW VERSION --- does not work for my Cayley graphs: all pairs are retrieved
# trying something else: since computing all intervals is expensive for
# large graphs, let us first gather nodes for which we will need to do
# that: if a vertex u (resp. v) has fewer neighbors than its distance to v
# (resp. u), then it cannot satisfy the other condition
distances = all_pairs_shortest_path_length(graph)
candidates = [
    (u, v)
    for u, v in combinations(graph, 2)
    if len(graph[u]) >= distances[u][v] and len(graph[v]) >= distances[u][v]
]

print(
    "retrieved", len(candidates), "pairs out of", len(list(combinations(graph, 2)))
)
# TODO giving up for now since we don't "win" anything for instances I'm interested in
return True
```

- [ ] is_maximal_planar:     there is a linear time algorithm: https://sci-hub.ru/10.1016/j.ipl.2003.11.011

## recognizers_n_4

- [ ] parallelize is_almost_claw_free (not obvious since communication has to take place between searchers)
- [ ] is_02_graph is there a partial fisc?
- [ ] is_p4_brittle: slow on cayley graphs (well, they're big)
    - the algorithm from which the paper comes mentions the class P4-stable, but I haven't found it in isgci

## recognizers_n_5

- [ ] is_perfect_elimination_bipartite:   the same paper describes a O(n^3) algo instead of the current O(n^5) approach

## recognizers_n_8

- [ ] is_wing_triangulated:
    - this function is very slow on large graphs due to the need to build an even larger wing graph; is there any way to
      avoid that?
    - additionally:
      # TODO the following criteria would be useful; unfortunately, exploiting them requires being
      # able to determine whether the graph is quasi-parity, which is open (gc_150)
      # see https://doi.org/10.1002/(SICI)1097-0118(199701)24:1%3C25::AID-JGT4%3E3.0.CO;2-L ,
      # claim 1: wing-triangulated-graphs with no even pairs are {F_1, F_2}-free
      # F_1 = ??? TODO
      # F_2 = X_{200}
      # if not is_h_free(graph,["X_{200}"]):
      # return False
      # claims 6, 7: wing-triangulated-graphs with no even pairs are {F_3, F_4, F_5}-free
      # F_3 = ??? TODO
      # F_4 = ??? TODO
      # F_5 = ??? TODO
    - it might be possible to rewrite the construction of the edge set with a comprehension, which might speed things up

---

# Parallel implementations

## recognizers_n_2

```python
from graph_recognition.recognizers_utils import assign_class_id
from functools import lru_cache
import networkx as nx
from networkx import is_planar


@assign_class_id("gc_1181")
@lru_cache(maxsize=None)
def is_apex(graph: nx.Graph) -> bool:
    """
    A graph G is an apex graph, if it contains a vertex v such that G−v is planar.

    TODO 

    :param graph:
    :return:
    """
    if is_planar(graph):
        return True
    # print("[DEBUG] graph's edges:", graph.edges)

    # a planar graph on n vertices has at most 3n - 6 edges; by definition, if
    # our graph is apex, then removing a vertex must leave a graph with at most
    # 3(n - 1) - 6 edges; since the degree of a vertex in our graph is < n,
    # if our graph has more than 3(n-1) - 6 + n - 1 = 4n - 10 edges, then it
    # cannot be apex
    n = graph.number_of_nodes()
    if graph.size() > 4 * n - 10:
        return False

    # the removal of a higher degree node has a better chance of yielding a
    # planar graph, so let's try those first (this was meant for the sequential
    # implementation, may not have any impact in the parallel setting)
    previous_nodes = set(graph.nodes)
    # sequential version, in case anyone's interested
    return any(
        is_planar(graph.subgraph(previous_nodes.difference({v})))
        for v in sorted(graph.nodes, key=graph.degree, reverse=True)
    )
    # NOTE: the parallel version is faster, but may crash due to too many open
    # processes
    """
    # sequential: 9.632s
    # parallel:   2.973s on same dataset
    with mp.Pool() as p:
        # TODO this is also slow because ALL jobs will be run; find a way to avoid that
        return any(
            p.map(
                func=is_planar,
                iterable=map(
                    lambda v: graph.subgraph(previous_nodes - {v}),
                    sorted(graph.nodes, key=graph.degree, reverse=True)
                )
            )
        )
    """

```

- I have a parallel version of `has_star_cutset`, but it does not run faster than the sequential version:

```python
from functools import lru_cache
import networkx as nx


@lru_cache(maxsize=None)
def has_star_cutset(graph, _complement=False):
    """Returns true if graph has a star-cutset, false otherwise. If _complement
    is True, checks the property on the complement of the graph instead.
  
    https://doi.org/10.1016/0095-8956(85)90049-8
  
    :type graph: nx.Graph
    @param graph:
    @param _complement:
    """


# See https://doi.org/10.1016/0095-8956(85)90049-8, Theorem 1 page 192: G
# has a star-cutset if and only if at least one of two properties hold

if _complement:
# testing property 1: G has a vertex w such that the set of all the
# vertices distinct from w and not adjacent to w induces a disconnected
# subgraph
# since we're in the complement, neighborhoods are in fact
# co-neighborhoods, and subgraphs are induced by non-edges; it shouldn't
# cost too much to compute complements here, so let's try
neighbourhoods = dict()
previous_nodes = set(graph.nodes)
for w in graph.nodes:
    neighbourhoods[w] = set(nx.non_neighbors(graph, w))
closed_N_w = neighbourhoods[w].union({w})
H = complement(graph.subgraph(previous_nodes.difference(closed_N_w)))
if not is_connected(H):
    return True

# testing property 2: complement has at least two nonadjacent vertices,
# which holds iff graph has at least one edge
if not graph.size():
    return False

# ... and it has adjacent vertices u, v such that v dominates u (i.e., each
# neighbor of u is either v or a neighbor of v)
for u, v in nx.non_edges(graph):
    if (
            neighbourhoods[u].difference({v}) <= neighbourhoods[v]
            or neighbourhoods[v].difference({u}) <= neighbourhoods[u]
    ):
        return True

return False

else:
# testing property 1: G has a vertex w such that the set of all the
# vertices distinct from w and not adjacent to w induces a disconnected
# subgraph
if any(
        not is_connected(graph.subgraph(nx.non_neighbors(graph, w))) for w in graph
):
    return True

# testing property 2: G has at least two nonadjacent vertices:
n = graph.number_of_nodes()
if graph.size() == (n * (n - 1)) // 2:
    return False

# ... and it has adjacent vertices u, v such that v dominates u (i.e., each
# neighbor of u is either v or a neighbor of v)

# caching neighbourhoods is more efficient than repeated calls to dominates
# or dominates_either_way
neighbourhoods = dict()
for u, v in graph.edges:
    if u not in neighbourhoods:
        neighbourhoods[u] = set(graph[u])

    if v not in neighbourhoods:
        neighbourhoods[v] = set(graph[v])

    if (
            neighbourhoods[u] - {v} <= neighbourhoods[v]
            or neighbourhoods[v] - {u} <= neighbourhoods[u]
    ):
        return True

return False
# parallel version of the above: same running time as sequential version,
# so I'm keeping the sequential version for now
"""
with mp.Pool() as p:
    return any(
        value is True for value in p.starmap(
            func=dominates_either_way, iterable=[(graph, u, v) for u, v in graph.edges]
        )
    )
"""

```

# BUGS

The following bugs are related to code that is not critical to the initial release, so the simplest option is to remove
it altogether.

## recognizers_n

is_middle:

```python
import networkx as nx
from collections import defaultdict
import heapq


# @assign_class_id("gc_551")  # TODO BUGGY
def is_middle(graph: nx.Graph) -> bool:
    """
    
        :param graph:
        :return:
        """
    # algo from https://www.sciencedirect.com/science/article/pii/0166218X84900672
    # steps 1 to 6
    # TODO function is buggy; after careful re-reading, I feel the mistakes must be in steps 1-6
    #  is the algorithm correct? I really can't see where I made a mistake ...
    W = set()
    L = defaultdict(set)
    H = graph.subgraph(graph)

    # TODO the authors recommend using radix sort; instead, I'm using a heap
    # store all nodes into a heap with minimum degree on top; we use triplets
    # (degree, count, node), where count keeps track of the "latest" version of
    # an inserted node: since we remove nodes from the graph as we go, degrees
    # change, and the smallest value for count reflects the latest version
    data = [(degree, 1, node) for node, degree in H.degree]
    c = count()
    next(c)
    heapq.heapify(data)
    while H:
        print("\n", "H.degree =", H.degree)
        print("data =", data)
        # u = None
        # extract a node with minimum degree; since we remove nodes as we go,
        # check that the extracted node is still in H
        # while u not in H:
        #     *_, u = heapq.heappop(data)
        u = min((degree, node) for node, degree in H.degree)[1]  # even this fails

        print("selected u =", u)

        # update W and L
        W.add(u)
        L[u].add(u)
        for w in H[u]:
            L[w].add(u)

        print("W =", W)
        print("L =", L)

        # remove subgraph induced by u and its neighbors
        neighbors_of_u = set(H[u])
        H = H.subgraph(set(H.nodes) - neighbors_of_u.union({u}))

        # update data by pushing all nodes whose degree have changed -- i.e.,
        # all nodes at distance 2 from u. The updated negative count forces the
        # heap to prioritize the latest version of each inserted node
        """
        for v in neighbors_of_u:
            if v in H:
                for w in graph[v]:
                    if w in H:
                        heapq.heappush(data, (H.degree[w], -next(c), w))
        """
        # note: the simple naive way is this, but function is still buggy
        data = [(degree, 1, node) for node, degree in H.degree]
        heapq.heapify(data)

    # step 7
    if any(
            not ((len(L[v]) == 1 and v in W) or (len(L[v]) == 2 and v not in W))
            for v in graph
    ):
        return False

    # step 8
    if any(len(L[u].intersection(L[v])) != 1 for u, v in graph.edges):
        return False

    # step 9: using the implementation on page 206
    for e in set(graph.nodes).difference(W):
        u, v = L[e]
        d_u, d_v = 0, 0
        for f in set(graph[e]).difference({u, v}):
            if u in L[f]:
                d_u += 1
            else:
                d_v += 1
        if d_u != graph.degree[u] - 1 or d_v != graph.degree[v] - 1:
            return False

    return True

```

## recognizers_n_3

- the following algorithm would be faster for recognizing weakly modular graphs, but it fails and I have no idea why

```python
from functools import lru_cache
import networkx as nx
from graph_recognition.misc_algo import all_pairs_shortest_path_length, is_connected
from itertools import combinations
from math import factorial
from networkx import is_bipartite


# @assign_class_id("gc_222")  # TODO buggy, can't find out why ... I'm following exactly the definition ... ???
@lru_cache(maxsize=None)
def is_weakly_modular(graph: nx.Graph) -> bool:
    """
    ISGCI gives two different characterizations of weakly modular graphs. Below
    is the one that yields a faster recognition algorithm.

    A graph is weakly modular if its distance metric fulfills the triangle and
    quadrangle conditions:

    The triangle condition: For every three vertices u, v, w with
    1 = d(v,w) < d(u,v) = d(u,w), there is a common neighbor x of v and w
    such that d(u,x) = d(u,v) + 1.

    The quadrangle condition: For every four vertices, u, v, w, z with
    d(v, z) = d(w, z) = 1 and d(u, v) = d(u, w) = d(u, z) - 1, there is a
    common neighbour x of v and w such that d(u,x) = d(u,v) - 1.

    https://www.graphclasses.org/classes/gc_222.html

    From https://doi.org/10.1016/0012-365X(95)00217-K: the graph must be
    connected.

    @param graph:
    @return:
    """
    # second method: use the triangle and quadrangle conditions
    # The triangle condition: For every three vertices u, v, w with 1 = d(v, w) < d(u, v) = d(u, w)
    # there is a common neighbor x of v and w such that d(u, x) = d(u, v) + 1.
    distances = all_pairs_shortest_path_length(graph)
    for v, w in graph.edges:  # d(v, w) = 1
        # since we want d(u, v) = d(u, w) > 1, we only need to examine vertices that are
        # adjacent to neither v nor w
        for u in set(nx.non_neighbors(graph, v)) & set(nx.non_neighbors(graph, w)):
            if distances[u][v] == distances[u][w]:
                if all(
                        distances[u][x] != distances[u][v] + 1
                        for x in nx.common_neighbors(graph, v, w)
                ):
                    return False

    # The quadrangle condition: For every four vertices, u, v, w, z with d(v, z) = d(w, z) = 1 and
    # d(u, v) = d(u, w) = d(u, z) - 1, there is a common neighbour x of v and w such that
    # d(u, x) = d(u, v) - 1.
    for v, z in graph.edges:  # d(v, z) = 1
        for w in set(graph[z]) - {v}:  # d(w, z) = 1; ensure w != v
            for u in set(graph) - {v, w, z}:  # make u distinct from v, w, z
                if distances[u][v] == distances[u][w] == (distances[u][z] - 1):
                    if all(
                            distances[u][x] != distances[u][v] - 1
                            for x in nx.common_neighbors(graph, v, w)
                    ):
                        return False

    return True


# @assign_class_id("gc_1159")  # TODO CHECK !!!
@lru_cache(maxsize=None)
def is_binary_hamming(graph: nx.Graph) -> bool:
    """
    Found in "Vdumc 11, number 1 INFORMATION PROCESSING LETTERS 29 August 1980
    QN THE COMPLEXITY OF TESTING A GRAPH FOR N.ClUBE"

    https://doi.org/10.1016/0020-0190(80)90025-3

    A connected graph
    G = (V, E) is an n-cube iff
    (i) G is bipartite,
    (ii) for each x, y E V., q(x, y) = d(x, y)!.

    (there are certainly faster algorithms, look up refs on isgci)

    https://www.graphclasses.org/classes/gc_1159.html

    @type graph: nx.Graph
    @param graph:
    @return:
    """
    # TODO this fails on a tree with edges [(0, 3), (1, 3), (2, 3)]
    #   the function returns False, but the function is right on that instance (checked by hand)
    #   we expected True because gc_1159 is an ancestor of gc_342=tree:
    #       gc_1159 -> gc_1172 -> gc_1170 -> gc_261 -> gc_210 -> gc_342 = gc_655
    #   so either the characterisation is wrong, or some inclusion relationship is ... find out!

    # TODO: I'm not sure anymore that n-cube = binary hamming; that could be the issue;
    #   I'm simply disabling this recognizer for now until I can check
    if not is_connected(graph) or not is_bipartite(graph):
        return False

    return all(
        sum(1 for _ in nx.all_shortest_paths(graph, x, y))
        == factorial(nx.shortest_path_length(graph, x, y))
        for x, y in combinations(graph, 2)
    )
```

# `graph_formats.py`

- [ ] `nx_graph_to_lad_string` can be slow for large graphs (eg: cayley-graph-block-interchange-8.s6)
- [ ] `nx_graph_to_gr_file`: cleaner way of doing things; for now, since we usually read from graph6 files, we assume
  vertices are in the range [0, n-1] so we just need to add 1; the format is only useful for an exact treewidth solver,
  so this is rather low priority until I enable hard recognizers
