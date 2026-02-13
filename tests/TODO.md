I generated every class that nauty-geng can generate, but I can still generate the complements of some classes; do that

I'll keep names of the form co-X, it's easier to keep track of what remains to be done that way

v = done
sc = self-complementary
cu = complement unknown

- cu  biconnected=gc_771
- [x]   bipartite=gc_69
- [x]   block=gc_93                     co-block=AUTO_2774
- [x]   C4-free=gc_360                  co-C4-free=gc_394
- [x]   chordal=gc_32
- cu  circle=gc_132
- [x]   claw-free=gc_62                 co-claw-free=AUTO_79
- cu  cographs=gc_151
- [ ] critical h-free
- cu  distance-regular=gc_1148
- [x]   K4-free=gc_455                  co-K4-free=gc_674
- cu  perfect=gc_56
- sc  permutation=gc_23
- [x]   planar=gc_43
- cu  regular=gc_1149
- sc  split=gc_39
- sc  strongly_regular=gc_1185
- [x]   trees=gc_342 cotrees=AUTO_2103
- [x]   triangle-free=gc_371            co-triangle-free=AUTO_399


- convert data to the smallest format;
    try s6 instead of g6; so far no luck, so maybe convert all to g6

- gather everything i can from https://houseofgraphs.org/meta-directory
  note: many of these are in other formats than graph6, implement converters

Almost hypohamiltonian graphs
Alternating plane graphs
Block graphs
Cographs
Critical H-free graphs
Cubic graphs
Directed graphs
(Brendan McKay)
Fullerenes
Graphs with maximum spectral gap
(Theodore Kolokolnikov)
HIST-critical graphs
Hypohamiltonian graphs
Interval graphs
(Ryuhei Uehara)
K2-hypohamiltonian graphs
Largest degree-diameter graphs
(Universitat Politècnica De Catalunya)
Maximal triangle-free graphs
Minimal Cayley graphs
Minimal Ramsey graphs
Nut graphs
Perihamiltonian graphs
Planar graphs
Platypus graphs
Quartic graphs
Ramsey numbers
Regular graphs
(Markus Meringer)
Simple graphs
(Brendan McKay)
Snarks
Strongly regular graphs
(Ted Spence)
Strongly regular graphs (continued)
(Ferdinand Ihringer)
Trees
Triangle-free k-chromatic graphs
Uniquely hamiltonian graphs
Vertex-transitive cubic graphs
(Krystal Guo)
Vertex-transitive graphs
(Gordon Royle)

see what nauty can do

nauty-genbg:
nauty-genbgL:
nauty-geng:

 Generate all graphs of a specified class.

      n    : the number of vertices
 mine:maxe : a range for the number of edges
              #:0 means '# or more' except in the case 0:0
   res/mod : only generate subset res out of subsets 0..mod-1

     -c    : only write connected graphs
     -C    : only write biconnected graphs
     -t    : only generate triangle-free graphs
     -f    : only generate 4-cycle-free graphs
     -b    : only generate bipartite graphs
                (-t, -f and -b can be used in any combination)
     -m    : save memory at the expense of time (only makes a
                difference in the absence of -b, -t, -f and n <= 28).
     -d#   : a lower bound for the minimum degree
     -D#   : an upper bound for the maximum degree
     -v    : display counts by number of edges
     -l    : canonically label output graphs

     -u    : do not output any graphs, just generate and count them
     -g    : use graph6 output (default)
     -s    : use sparse6 output
     -h    : for graph6 or sparse6 format, write a header too

     -q    : suppress auxiliary output (except from -v)

  See program text for much more information.


$ nauty-genquarticg -help

Usage: genquarticg [-ugs -h -c -l] n [res/mod] [file]

  generate all non-isomorphic quartic graphs of a given order

n     : the number of the vertices
file  : the name of the output file (default stdout)
-u    : do not output any graphs, just generate and count them
-g    : use graph6 format for output (default)
-s    : use sparse6 format for output
-h      write a header (only with -g or -s).
-c    : only write connected graphs
-C    : only write biconnected graphs
res/mod : only generate subset res out of subsets 0..mod-1
-l    : canonically label output graphs.

$ nauty-genspecialg -help

Usage: genspecialg [-s|-g|-z|-d|-v] [-q] [-p#|-c#|-e#|-k#|-b#,#[,#]| -Q#|-f#|-J#,#|-P#,#|C#,#...|G#,#...|T#,#...]* [outfile]

 Generate special graphs.

Options:
General Options:
    -s : Write in sparse6 format (default)
    -g : Write in graph6 format
    -z : Make digraph versions and write in digraph6 format
    -d : Write in dreadnaut format (can be used with -z)
    -v : For each graph, report the size to stderr
    -q : Suppress summary

Special Options:
 If defined, the digraph version is shown in parentheses;
 # size parameter called n in the descriptions.

    -p#   : path (directed path) on n vertices.
    -c#   : cycle (directed cycle) on n vertices.
    -e#   : empty graph (digraph with loops only) on n vertices.
    -k#   : complete graph (with loops) on n vertices
    -b#,#[,#] : complete bipartite graph (directed l->r) on n vertices
	           minus a matching of given size if present
    -f#   : flower snark on 4*# vertices
    -P#,# : generalized Petersen graph; usual one is -P5,2
    -Q#   : hypercube on 2^n vertices and degree n.
    -J#,# : Johnson graph J(n,k), args are n and k.
    -C#[,#] : circulant (di)graph.
    -T#[,#] : theta (di)graph Theta(#,#,...), give path lengths.
    -G#[,#] : (directed) grid, use negative values for open directions

    Any number of graphs can be generated at once.

