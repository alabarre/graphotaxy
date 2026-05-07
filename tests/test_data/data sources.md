Anthony Labarre © 2023-2026

This file documents the origin of all datasets in the present directory. They are intended for testing purposes.

Some files have the extension .IGNORE. These are datasets that are problematic for some reason. Those reasons are explained in the README file in the same directory as those files.

# Generators

Generators are available for a few classes. The `nauty` suite has a few of them:

- `nauty-genbg`: various families of bipartite graphs
- `nauty-genbgL`: identical to `nauty-genbg`?
- `nauty-geng`: more general graph generator, can generate specific families by combining various options
- `nauty-gengL`: identical to `nauty-geng`?
- `nauty-genktreeg`:  Generate all k-trees on n vertices.
- `nauty-genposetg`: Generate the Hasse diagrams of the posets with n points (are they in ISGCI?)
- `nauty-genquarticg`: generate all non-isomorphic quartic graphs of a given order 
- `nauty-genrang`:  Generate random graphs.
- `nauty-genspecialg`:  Generate special graphs.
- `nauty-gentourng`:  Generate all tournaments of a specified class.
- `nauty-gentreeg`:   Generate (unrooted) trees.

Other generators I wrote are available in the `./tests/generators` directory. I'm not including software from other authors.

# Building new datasets

`nauty` has a few tools that can help generate new datasets from old datasets:

- `nauty-complg` builds the complement of a graph, so if you have a dataset for class C, you can obtain a dataset for its complement;
- `nauty-linegraphg` builds the line graph of a graph, so if you have a dataset for class C, you can obtain a dataset for the class "line graph of C";
- `nauty-pickg` selects graphs from a given dataset according to various criteria, so if you have a dataset for class C, you can obtain datasets for various subclasses of C, depending on the capabilities of `nauty-pickg`.

# Compressed formats

Since graphotaxy can read g6 and s6 files compressed with bzip2, gzip or xzip, some directories contain only compressed versions of the original files. For each file, only the smallest resulting archive was kept (all compressors were invoked with the `-9` option).

# Datasets

## 2-edge-connected=gc_1362

generated from the datasets in connected by my filter.py program

## 2-tree=gc_721

`for ((i=2; i<15; i++)); do nauty-genktreeg -k2 -l $i 2-trees-$i.g6; done`

## 3-tree=gc_983

`for ((i=3; i<15; i++)); do nauty-genktreeg -k3 -l $i 3-trees-$i.g6; done`


## biconnected=gc_771

`for ((i=1; i<11; i++)); do nauty-geng -C $i bi-vertex-connected-graphs-$i.g6; done`

## bipartite-cubic-planar=gc_1334

Generated from planar connected graphs using nauty-pickg:

`for file in $(ls *g6); do nauty-pickg -b -d3 -D3 $file > ../bipartite-cubic-planar\=gc_1334/bipartite-cubic-$file; done`

Unfortunately that yields only one such graph, for n=8.


## bipartite=gc_69

Generated with:

`for ((i=1; i<11; ++i)); do nauty-geng -blc $i connected-bipartite-$i.g6; done`

I restricted myself to connected bipartite graphs because I use them to generate line graphs afterwards, and the fact that a line graph is co-claw or co-diamond-free is not always true for disconnected graphs.

## block=gc_93

./block/BlockGraphs-*

From https://houseofgraphs.org/meta-directory/block-graphs

Tried converting to s6, but g6 takes up less space.

Removed graphs for size 18 and 19 because gitlab does not allow files with size > 100M

## (C4,C5)-free=gc_367

`for ((i=1; i<11; i++)); do nauty-geng -cfp $i C4-C5-free-graphs-connected-$i.g6; done`

## C4-free=gc_360

`for ((i=1; i<11; i++)); do nauty-geng -cf $i C4-free-graphs-connected-$i.g6; done`

## C5-free=gc_359

`for ((i=1; i<11; i++)); do nauty-geng -cp $i C5-free-graphs-connected-$i.g6; done`

## chordal=gc_32

Source: https://users.cecs.anu.edu.au/~bdm/data/graphs.html

## circle=gc_132

Generated using Tom Johnston's software: https://tomjohnston.co.uk/blog/2020-10-04-enumerating-circle-graphs.html

## claw-free=gc_62

`for ((i=1; i<11; i++)); do nauty-geng -cF $i claw-free-connected-$i.g6; done`

## cobipartite=gc_486

Generated from the datasets in bipartite with nauty.

Example: `nauty-complg -l bipartite-5.sparse6 cobipartite-5.s6`

Note: I then converted everything in that directory to g6, because it used less space.

## co-block=AUTO_2774

generated from block using nauty-complg

## co-C4-free=gc_394

generated from c4-free using nauty-complg

## cochordal=gc_145

Generated from the datasets in chordal with nauty.

`for file in $(ls *g6); do nauty-complg -l $file co$file; done`

## (co-claw,co-diamond)-free=AUTO_1467

`for file in $(ls *g6); do nauty-complg $file > ../\(co-claw\,co-diamond\)-free\=AUTO_1467/co-$file; done`

## co-claw-free=AUTO_79

generated from claw-free using nauty-complg

## cographs=gc_151

./cographs/cographConnected*

From https://houseofgraphs.org/meta-directory/cographs

Tried converting to s6, but g6 takes up less space.

Removed graphs for size 19 because gitlab does not allow files with size > 100M

## co-K4-free=gc_674

generated from k4-free using nauty-complg

## co-line=gc_970


generate from line graphs: for file in $(ls *g6); do nauty-complg $file > ../co-line\=gc_970/co-$file; done`


## co-line graphs of bipartite graphs=gc_744

from gc_251
for file in $(ls *g6); do nauty-complg $file > ../co-line\ graphs\ of\ bipartite\ graphs\=gc_744/co-$file; done`

## coplanar=gc_953

Generated from the datasets in planar with nauty-complg.

for file in $(ls *g6)
do
    nauty-complg -l $file co$file
done


## cotrees=AUTO_2103

Generated from the datasets in trees with nauty-complg

## co-triangle-free=gc_1378

generated from triangle-free using nauty-complg

## critical h-free'

## cubic-and-hamiltonian=gc_1316


## distance-regular=gc_1148

Source:  https://www.distanceregular.org/graphdata/

## halin=gc_198

Source: from https://cheddarmonk.org/maths/halin_graphs/










## K4-free-and-planar=gc_1367$ 

In planar=gc_43:

`for file in $(ls *g6); do nauty-pickg -k3 $file > ../K4-free-and-planar\=gc_1367/k4-free-$file; done`

## K4-free=gc_455

`for ((i=1; i<11; i++)); do nauty-geng -ck $i K4-free-connected-$i.g6; done`





# TODO

sort categories below according to ls output (done for sections above)


## line=gc_249

generate connected graphs with nauty: `for ((i=1; i<11; i++)); do nauty-geng -c $i connected-$i.g6; done`

then generate the line graphs of those graphs: for file in $(ls *g6); do nauty-linegraphg $file > line-$file; done`


## line graphs of bipartite graphs=gc_251

for file in $(ls *g6); do nauty-linegraphg $file > ../line\ graphs\ of\ bipartite\ graphs\=gc_251/line-$file; done`

## line graphs of planar cubic bipartite graphs=gc_1335

for file in $(ls *g6); do nauty-linegraphg $file > ../line\ graphs\ of\ planar\ cubic\ bipartite\ graphs\=gc_1335/line-$file; done

## line graphs of triangle-free graphs=gc_708

generate the line graphs of triangle-free graphs: for file in $(ls *g6); do nauty-linegraphg $file > line-$file; done`

## regular=gc_1149

./regular/

Source :  https://sites.flinders.edu.au/flinders-hamiltonian-cycle-project/graph-database/

./regular/cubic graphs/hamiltonian
./regular/cubic graphs/nonhamiltonian


## strongly_regular=gc_1185

Source: http://users.cecs.anu.edu.au/~bdm/data/graphs.html

- sr25832.g6          (1 graph)
- sr251256.g6         (15 graphs)
- sr261034.g6         (10 graphs)
- sr271015.g6         (1 graph)
- sr281264.g6         (4 graphs)
- sr291467.g6         (41 graphs)
- sr351668.g6         (3854 graphs)
- sr351899.g6         (227 graphs)
- sr361446.g6         (180 graphs)
- sr361566.g6.gz      (32548 graphs, gzipped). These come in 227 switching classes, one for each regular two-graph of order 36.
- sr361566rep.g6      (22T graphs, see previous line) We also provide one representative of each class.
- sr371889some.g6     (6760 graphs, maybe incomplete)
- sr401224.g6         (28 graphs)
- sr65321516some.g6   (32 graphs, maybe incomplete).


## trees=gc_342

Source: https://users.cecs.anu.edu.au/~bdm/data/graphs.html

## planar=gc_43

Source: https://houseofgraphs.org/data/planar/planar_graphs/

## permutation=gc_23 

Generated using Tom Johnston's software: https://tomjohnston.co.uk/blog/2020-10-25-enumerating-permutation-graphs.html

## self-complementary=gc_1059

Source: https://users.cecs.anu.edu.au/~bdm/data/graphs.html

## split=gc_39

`for ((i=1; i<11; i++)); do nauty-geng -cS $i split-graphs-connected-$i.g6; done`

## perfect=gc_56

`for ((i=1; i<11; i++)); do nauty-geng -cP $i perfect-graphs-connected-$i.g6; done`

## triangle-free=gc_371

`for ((i=1; i<11; i++)); do nauty-geng -ct $i triangle-free-graphs-connected-$i.g6; done`


## strict-2-threshold=gc_316

only two files with a single graph each, they are the examples shown in Figure 3 of this paper:
https://twiki.di.uniroma1.it/pub/Users/AndreaSterbini/Ricerca/11-IPL-1995.pdf (see also https://doi.org/10.1016/0020-0190(95)00030-G)

## ptolemaic=gc_95

Source: http://www.jaist.ac.jp/~uehara/graphs/#ptolemaic

converted to g6 format myself












## dismantlable=gc_49

from https://www.cambridge.org/core/services/aop-cambridge-core/content/view/957BD01D745EA977FD838B5F13EEF33F/S000843950001599Xa.pdf/dismantlability_revisited_for_ordered_sets_and_graphs_and_the_fixedclique_property.pdf

converted to g6 myself

## line and perfect=gc_253

generated from the datasets in perfect=gc_56 by my filter.py program

## line perfect=gc_1358

generated by my line_perfect.py program

## outerplanar=gc_110

generated from the datasets in planar=gc_43 by my filter.py program

## co-outerplanar

generated from the datasets in outerplanar=gc_110 by nauty-complg:

for file in $(ls); do nauty-complg -l $file co$file; done



## 2-strongly-regular=gc_1195

generated from the datasets in connected by my filter.py program

## K_{1,4}-free=gc_388

generated from the datasets in connected by my filter.py program

## mock threshold=gc_1289

generated using my program mock_threshold.py in generators. 

The program generates random nonisomorphic mock threshold graphs. Since I don't know how many there are, to (be fairly certain that I) obtain all of them for a fixed number of vertices, I set a timeout: we give up on the search for a new graph if no new graph was generated in the last T seconds.

For n <= 5, we have all mock threshold graphs since all of graphs on <= 5 vertices are mock threshold except C_5.

For n >= 6, to be more than "fairly certain", you can always increase the timeout, or check that the graphs not in those files are **not**. Until someone finds a formula the number of mock threshold graphs, if that is even feasible.

## unbreakable=gc_277

I encoded by hand the following graphs:

- from https://doi.org/10.1016/0095-8956(90)90028-X
    - graph L_8 p. 202 (proven to be unbreakable p. 232-233)
    - graph L_9 p. 202 (proven to be unbreakable p. 232-233)
    
Note 1: other instances (Fig 9 and Fig 10-11-12 (those last 3 are isomorphic)) are provided in the paper, but they are painful to encode by hand. I'll wait for Graph Harvester to be available again.

Note 2: my labels may not coincide with the labellings provided in Fig. 3 of the paper, because I only realised its existence afterwards.
    

## murky=gc_218

The following unbreakable graphs are also known to be murky:

- from https://doi.org/10.1016/0095-8956(90)90028-X
    - graph L_8 p. 202 (proven to be murky p. 232-233)
    - graph L_9 p. 202 (proven to be murky p. 232-233)
