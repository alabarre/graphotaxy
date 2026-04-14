"""
Anthony Labarre © 2025-2026

This implementation of a 2-SAT solver is a mere adaptation of David Eppstein's PADS library. The
only changes I made are minor and were mostly intended to remove dependencies on the rest of
the PADS library, since much of its code is irrelevant to my purposes or has been integrated into
networkx.

2-SAT is useful for recognizing the following graph classes:

    - [ ] https://www.graphclasses.org/classes/gc_452                       bisplit graphs
        see https://doi.org/10.1016/j.disc.2004.08.046, Theorem 14 p 29
    - [x] https://www.graphclasses.org/classes/gc_154                       cograph contraction
        see https://doi.org/10.1002/(SICI)1097-0118(199904)30:4%3C309::AID-JGT5%3E3.0.CO;2-5
        Theorem 3.1 p 312
    - [x] https://www.graphclasses.org/classes/gc_3                         P_{4}-brittle
        see  https://doi.org/10.1016/S0012-365X(99)00300-3 p 204

"""
from typing import Callable, Hashable

"""
Not.py

Symbolic negation operator.

For any Python value x, Not(x) is an object, with the properties that
    Not(x)==Not(y) iff x==y
    Not(Not(x))==x.
If x is hashable, so is Not(x).

The purpose of this is to use within TwoSatisfiability and similar code, to allow Python objects to
represent logical variables. If x is an object representing a variable, Not(x) can be used to 
represent its negation.

To determine whether a given object y is of the form Not(x), use isinstance(y, SymbolicNegation).  
If it is, you can recover x as Not(y).

D. Eppstein, April 2009.
"""
# Imports -----------------------------------------------------------------------------------------
# ----- Third-party imports -----------------------------------------------------------------------
from networkx import strongly_connected_components, DiGraph


class DoubleNegationError(Exception):
    pass


class SymbolicNegation:
    def __init__(self, x: Hashable) -> None:
        if isinstance(x, SymbolicNegation):
            raise DoubleNegationError(
                "Use Not(x) rather than instantiating SymbolicNegation directly"
            )
        self.negation = x

    def negate(self) -> Hashable:
        return self.negation

    def __repr__(self) -> str:
        return "Not(" + repr(self.negation) + ")"

    def __eq__(self, other: Hashable) -> bool:
        return isinstance(other, SymbolicNegation) and self.negation == other.negation

    def __hash__(self) -> int:
        return -hash(self.negation)


def Not(x: SymbolicNegation) -> SymbolicNegation:
    return x.negate() if isinstance(x, SymbolicNegation) else SymbolicNegation(x)


def copy_graph(graph: dict, adjacency_list_type: Callable = set) -> dict:
    """
    Make a copy of a graph G and return the copy. Any information stored in edges G[v][w] is
    discarded.

    Most of the time, copy.deepcopy will be preferable to this function; however, unlike deepcopy,
    this function can change the data type of the adjacency list of the given graph.

    The second argument should be a callable that turns a sequence of neighbors into an appropriate
    representation of the adjacency list. Note that, while Set, list, and tuple are appropriate
    values for adjacency_list_type, dict is not -- use Util.map_to_constant instead.
    """
    return {v: adjacency_list_type(iter(graph[v])) for v in graph}


def condensation(graph: DiGraph) -> dict:
    """Return a DAG with vertices equal to sets of vertices in SCCs of G.

    Note (Anthony Labarre): networkx also has a condensation function, but it replaces sets of
    vertices with integer labels. It cannot be used in the context of 2-SAT, since we will need
    to iterate over sets of vertices.
    """
    components = dict()
    graph_to_condensation = dict()
    for scc in map(frozenset, strongly_connected_components(graph)):
        for v in scc:
            graph_to_condensation[v] = scc
        components[scc] = set()
    for v in graph:
        for w in graph[v]:
            if graph_to_condensation[v] != graph_to_condensation[w]:
                components[graph_to_condensation[v]].add(graph_to_condensation[w])
    return components


"""
TwoSatisfiability.py

Algorithms for solving 2-satisfiability problems. For theory and references, see 
https://en.wikipedia.org/wiki/2-satisfiability

All instances should be represented as a directed implication graph in which the vertices represent
variables and (via Not.py) their negations. A variable may be represented by any hashable Python 
object, and its negation should be represented by the object Not(x). For instance, the implication 
graph

    {1:[2,3], 2:[Not(1),3]}
    
from the unit tests of this module represents the system of implications among three logical 
variables v1, v2, and v3:

    v1 => v2, v1 => v3;  v2 => ~v1, v2 => v3.
    
An instance is satisfiable if it is possible to assign the Boolean values True and False to these
variables in order to make all implications become logically correct. These problems have many 
applications involving problems in which variables may take on either of two values and pairs of 
variables are subject to arbitrary constraints; see the Wikipedia article for details.

If G is a graph of this type,
- Symmetrize(G) extends G by adding the contrapositive of each implication
- Satisfiable(G) returns True or False according to whether the
  2SAT instance can be satisfied. It takes linear time in the size of G.

D. Eppstein, April 2009.
"""


def symmetrize(graph: dict) -> DiGraph:
    """Expand implication graph to a larger symmetric form.

    If the 2SAT instance includes an implication A=>B, then it is also valid to conclude that
    ~B => ~A, and our 2SAT solver needs to have that second implication made explicit. But we do
    not want to force users to supply the contrapositives for each of the implications they
    include, so we use this routine to fill in any missing implications.
    """
    new_graph = copy_graph(graph)
    for v in graph:
        new_graph.setdefault(Not(v), set())  # make sure all negations are included
        for w in graph[v]:
            new_graph.setdefault(w, set())  # as well as all implicants
            new_graph.setdefault(Not(w), set())  # and negated implicants

    for v in graph:
        for w in graph[v]:
            new_graph[Not(w)].add(Not(v))

    return DiGraph(new_graph)


def symmetrize_in_place(graph: dict) -> DiGraph:
    """Expand implication graph to a larger symmetric form.

    If the 2SAT instance includes an implication A=>B, then it is also valid to conclude that
    ~B => ~A, and our 2SAT solver needs to have that second implication made explicit. But we do
    not want to force users to supply the contrapositives for each of the implications they
    include, so we use this routine to fill in any missing implications.

    This does the same thing as David Eppstein's original symmetrize function, but in place instead
    of returning a new copy.
    """
    for v in set(graph):
        graph.setdefault(Not(v), set())  # make sure all negations are included
        for w in set(graph[v]):
            graph.setdefault(w, set())  # as well as all implicants
            graph.setdefault(Not(w), set())  # and negated implicants

    for v in set(graph):
        for w in set(graph[v]):
            graph[Not(w)].add(Not(v))

    return DiGraph(graph)


def satisfiable(graph: dict) -> bool:
    """
    Does this 2SAT instance have a satisfying assignment?
    """
    if any(Not(v) in scc for scc in condensation(symmetrize_in_place(graph)) for v in scc):
        return False

    return True
