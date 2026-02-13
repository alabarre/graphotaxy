"""
Anthony Labarre © 2024

Lex-BFS implementation. This is merely an adaptation of David Eppstein's PADS
code: all credit goes to him.

"""
# Imports ---------------------------------------------------------------------
# ----- Standard imports ------------------------------------------------------
from typing import Generator, Iterable, Hashable, Iterator

# ----- Non-standard imports --------------------------------------------------
from networkx import Graph


# Helpful classes -------------------------------------------------------------
#
# PartitionRefinement.py
#
# Maintain and refine a partition of a set of items into subsets,
# as used e.g. in Hopcroft's DFA minimization algorithm,
# modular decomposition of graphs, etc.
#

class PartitionError(Exception):
    """A dummy error class."""


class PartitionRefinement:
    """Maintain and refine a partition of a set of items into subsets.
    Space usage for a partition of n items is O(n), and each refine
    operation takes time proportional to the size of its argument.
    """

    def __init__(self, items: Iterable) -> None:
        """Create a new partition refinement data structure for the given
        items.  Initially, all items belong to the same subset.
        """
        subset = set(items)
        self._sets = {id(subset): subset}
        self._partition = {x: subset for x in subset}

    def __getitem__(self, element: Hashable) -> set | frozenset:
        """Return the set that contains the given element."""
        return self._partition[element]

    def __iter__(self) -> Iterator:
        """Loop through the sets in the partition."""
        return iter(self._sets.values())

    def __len__(self) -> int:
        """Return the number of sets in the partition."""
        return len(self._sets)

    def add(self, element: Hashable, subset: set) -> None:
        """Add a new element to the given partition subset."""
        if id(subset) not in self._sets:
            raise PartitionError("Set does not belong to the partition")
        if element in self._partition:
            raise PartitionError("Element already belongs to the partition")
        subset.add(element)
        self._partition[element] = subset

    def remove(self, element: Hashable) -> None:
        """Remove the given element from its partition subset."""
        self._partition[element].remove(element)
        del self._partition[element]

    def refine(self, set_or_sequence: Iterable) -> list:
        """Refine each set A in the partition to the two sets A & S, A - S.
        Return a list of pairs (A & S, A - S) for each changed set.  Within
        each pair, A & S will be a newly created set, while A - S will be a
        modified version of an existing set in the partition. Not a generator
        because we need to perform the partition even if the caller doesn't
        iterate through the results.
        """
        hit = dict()
        output = list()
        for x in set_or_sequence:
            if x in self._partition:
                Ax = self._partition[x]
                hit.setdefault(id(Ax), set()).add(x)
        for A, AS in hit.items():
            A = self._sets[A]
            if AS != A:
                self._sets[id(AS)] = AS
                for x in AS:
                    self._partition[x] = AS
                A -= AS
                output.append((AS, A))
        return output

    def freeze(self) -> None:
        """Make all sets in S immutable."""
        for S in list(self._sets.values()):
            frozen_s = frozenset(S)
            for x in frozen_s:
                self._partition[x] = frozen_s
            self._sets[id(frozen_s)] = frozen_s
            del self._sets[id(S)]


# -----------------------------------------------------------------------------
#
# Sequence.py
#
# Doubly-linked circular list for maintaining a sequence of items
# subject to insertions and deletions.
#
class SequenceError(Exception):
    """A dummy error class."""


class Sequence:
    """Maintain a sequence of items subject to insertions and removals.
    All sequence operations take constant time except indexing, which
    takes time proportional to the index.
    """

    def __init__(self, iterable=None, key=None):
        """We represent the sequence as a doubly-linked circular linked list,
        stored in two dictionaries, self._next and self._prev.  We also store
        a pointer self._first to the first item in the sequence.  If key is
        supplied, key(x) is used in place of x to look up item positions;
        e.g. using key=id allows sequences of lists or sets.
        """
        self._key = key
        self._items = {}
        self._next = {}
        self._prev = {}
        self._first = None
        if iterable:
            for x in iterable:
                self.append(x)

    def __iter__(self):
        """Iterate through the objects in the sequence.
        May give unpredictable results if sequence changes mid-iteration.
        """
        item = self._first
        while self._next:
            yield self._items.get(item, item)
            item = self._next[item]
            if item == self._first:
                return

    def __getitem__(self, i):
        """Return the ith item in the sequence."""
        item = self._first
        while i:
            item = self._next[item]
            if item == self._first:
                raise IndexError("Index out of range")
            i -= 1
        return self._items.get(item, item)

    def __len__(self):
        """Number of items in the sequence."""
        return len(self._next)

    def __repr__(self):
        """Printable representation of the sequence."""
        output = []
        for x in self:
            output.append(repr(x))
        return 'Sequence([' + ','.join(output) + '])'

    def key(self, x):
        """Apply supplied key function."""
        if not self._key:
            return x
        key = self._key(x)
        self._items[key] = x
        return key

    def _insafter(self, x, y):
        """Unkeyed version of insertAfter."""
        if y in self._next:
            raise SequenceError("Item already in sequence: " + repr(y))
        self._next[y] = z = self._next[x]
        self._next[x] = self._prev[z] = y
        self._prev[y] = x

    def append(self, x):
        """Add x to the end of the sequence."""
        x = self.key(x)
        if not self._next:  # add to empty sequence
            self._next = {x: x}
            self._prev = {x: x}
            self._first = x
        else:
            self._insafter(self._prev[self._first], x)

    def remove(self, x):
        """Remove x from the sequence."""
        x = self.key(x)
        prev = self._prev[x]
        self._next[prev] = _next = self._next[x]
        self._prev[_next] = prev
        if x == self._first:
            self._first = _next
        del self._next[x], self._prev[x]

    def insert_after(self, x, y):
        """Add y after x in the sequence."""
        y = self.key(y)
        x = self.key(x)
        self._insafter(x, y)

    def insert_before(self, x, y):
        """Add y before x in the sequence."""
        y = self.key(y)
        x = self.key(x)
        self._insafter(self._prev[x], y)
        if self._first == x:
            self._first = y

    def predecessor(self, x):
        """Find the previous element in the sequence."""
        x = self.key(x)
        prev = self._prev[x]
        return self._items.get(prev, prev)

    def successor(self, x):
        """Find the next element in the sequence."""
        x = self.key(x)
        next_elem = self._next[x]
        return self._items.get(next_elem, next_elem)

#
# LexBFS.py
#
# Lexicographic breadth-first-search traversal of a graph, as described
# in Habib, McConnell, Paul, and Viennot, "Lex-BFS and Partition Refinement,
# with Applications to Transitive Orientation, Interval Graph Recognition,
# and Consecutive Ones Testing", Theor. Comput. Sci. 234:59-84 (2000),
# http://www.cs.colostate.edu/~rmm/lexbfs.ps
#


def arbitrary_item(S: set | Sequence) -> object:
    """
    Select an arbitrary item from set or sequence S.
    Avoids bugs caused by directly calling iter(S).next() and
    mysteriously terminating loops in callers' code when S is empty.
    """
    try:
        return next(iter(S))
    except StopIteration:
        raise IndexError("No items to select.")


def lex_bfs(graph: Graph) -> Generator[int, None, None]:
    """Find lexicographic breadth-first-search traversal order of a graph.
    G should be represented in such a way that "for v in G" loops through
    the vertices, and "G[v]" produces a sequence of the neighbors of v; for
    instance, G may be a dictionary mapping each vertex to its neighbor set.
    Running time is O(n+m) and additional space usage over G is O(n).
    """
    parts = PartitionRefinement(graph)
    seq = Sequence(parts, key=id)
    while seq:
        extracted_set = seq[0]
        v = arbitrary_item(extracted_set)
        yield v
        parts.remove(v)
        if not extracted_set:
            seq.remove(extracted_set)
        for new, old in parts.refine(graph[v]):
            seq.insert_before(old, new)
