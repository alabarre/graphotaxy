# Blocking TODOs for first release

The following TODOs are critical for first release.


---

# Other TODOs

The following TODOs are important but not critical for first release (check this! there are bugs, so code should be fixed or removed)

# Algorithms to improve

# fisc_based_recognizers

TODO whenever possible, have other recognizers call the optimized functions, including in fisc_based_recognizers, 
even when they admit no "official" improvements.


So: 

1. optimize every "basic" recognizer;
2. check where they can be used elsewhere

- [ ] make sure other files call recognizers instead of is_h_free
- [ ] maybe write something to detect that ... and how to optimize in the presence of multiple choices

## order $\le$ 2

no further improvement possible

## order $\le$ 3

- [x] there is a linear-time algo for P_3-free recognition: simply check if it is the disjoint union of cliques
- [ ] there is a linear-time algo for triangle-free recognition, and it is implemented in aegypti!
  - wait till paper is accepted and make sure algo is reliable, bad gut feeling
- [x] A graph is (3K1,P3)-free if it is the disjoint union of two complete graphs. -> linear time
- [x] (3K1,co(P3))-free = co max degree 1 
- [x] (P_3, triangle)-free = max degree 1
- [x] https://www.graphclasses.org/classes/gc_1246
- [ ] https://www.graphclasses.org/classes/gc_1271 = complete multipartite ... ?  

## order $\le$ 4

- improving the following recognizers requires implementing a fast matrix multiplication algorithm; I'm not interested in that at the moment, since we'd waste computing time to convert each graph to a matrix representation first ...
  - [ ] claw-free https://www.graphclasses.org/classes/gc_62
  - [ ] $K_4$-free: https://www.graphclasses.org/classes/gc_455
  - [ ] diamond free https://www.graphclasses.org/classes/gc_441
- [x] $P_4$-free: linear https://www.graphclasses.org/classes/gc_152 (using tralda)
- [x] https://www.graphclasses.org/classes/gc_357
- [x] https://www.graphclasses.org/classes/gc_343: linear because = quasi threshold
- [x] https://www.graphclasses.org/classes/gc_473 = weakly geodetic; can we do better than O(n^4)?
- [ ] https://www.graphclasses.org/classes/gc_1 linear
  - see https://doi.org/10.1016/0166-218X(94)00022-0
- [ ] https://www.graphclasses.org/classes/gc_1244 linear
  - = complete split, whose recognition is "trivial" (?) https://www.graphclasses.org/classes/gc_1242.html
  - well ok, probably not too hard to write ...
- [x] https://www.graphclasses.org/classes/gc_1312 linear
- [ ] https://www.graphclasses.org/classes/gc_171 linear 
  - otoh I have no idea what the algorithm is, ISGCI is not helpful in that regard
- [x] https://www.graphclasses.org/classes/gc_709 = line graphs of triangle-free graphs; nx has inverse line graph function, check what we can do
- [x] https://www.graphclasses.org/classes/gc_1310 linear
- [ ] https://www.graphclasses.org/classes/gc_329 
  - [x] quadratic: using equivalence with threshold graphs and nx's implementation of the test
  - [ ] apparently doable in linear time, see refs on https://www.graphclasses.org/classes/gc_328  
- [x] https://www.graphclasses.org/classes/gc_1309 O(1) !
- [x] https://www.graphclasses.org/classes/gc_1307
- [x] https://www.graphclasses.org/classes/gc_1313
- [x] https://www.graphclasses.org/classes/gc_1314

## order $\le$ 5

- [ ] https://www.graphclasses.org/classes/gc_354 room for improvement:
  - look for all potential centers (vertices of degree >= 4)
  - for all 4-tuples of neighbor, check if they induce a P_4
  - doable in quadratic time: for each v of degree >= 4, check if neighborhood is P_4-free; we get a O(n^2) algo once we have P_4-free recognition in linear time
- [ ] https://www.graphclasses.org/classes/gc_871 
  - room for improvement: neighbourhood of every vertex is (2k2,P4)-free, and there is a linear time algo for the latter (not implemented yet)
  - otoh I have no idea what the algorithm is, ISGCI is not helpful in that regard
  - oh, ok: it is co-interval and cograph, and O(n) algos exist for constituent classes
- [ ] https://www.graphclasses.org/classes/gc_566 linear!
  - need https://pure.tue.nl/ws/files/2079124/9411073.pdf (algo description)
  - need https://pure.tue.nl/ws/files/2013845/9306744.pdf (representatives)
- [ ] https://www.graphclasses.org/classes/gc_854 linear
- [x] https://www.graphclasses.org/classes/gc_313 linear
- [x] https://www.graphclasses.org/classes/gc_1301 linear
- [ ] https://www.graphclasses.org/classes/gc_308 linear
  - need modular decomposition
- [ ] https://www.graphclasses.org/classes/gc_180 linear
  - see paper on dominoes https://pure.tue.nl/ws/files/2013845/9306744.pdf
- [ ] https://www.graphclasses.org/classes/gc_662 linear
  - see https://www.ii.uib.no/~pinar/certifying-NJC.pdf
- [ ] https://www.graphclasses.org/classes/gc_684.html = 1-bounded-bipartite
- [ ] https://www.graphclasses.org/classes/gc_224 O(mn)
- [ ] https://www.graphclasses.org/classes/gc_189 linear
  - need modular decomposition https://pdf.sciencedirectassets.com/271538/1-s2.0-S0304397500X00606/1-s2.0-S0304397596002204/main.pdf?X-Amz-Security-Token=IQoJb3JpZ2luX2VjEB0aCXVzLWVhc3QtMSJHMEUCIQCkWUuC7isO2mBDyo2YNbnNtZr%2FPwt9VdA%2Bl%2FmBnqcI5gIgI3UQRhZM%2FqCmilVVdzQNnbwoysz%2BWWVx8UNZdmBPZukqvAUI9v%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAFGgwwNTkwMDM1NDY4NjUiDAp6QoR4uZD%2F1AtaSCqQBbx51JhV7vUdydziOfsEL8mYA1RbD75e67v9k6To2YKJprrBfkyRNs5wEXmKct5oCigeXtfk7RkWjFzqIbjLF6v740Ce%2Faf8UWdzTfhDw7BvH5GpFCZi4TG2g8zeTmt4wFso3EejQ1ASr3ULcLMwZ6P2QMi%2FHhB9vrDtUbQ6pFlMG731KoBo3RC6mDwz%2FVYDExAjT5wGv%2FY7ujhewzWzD6biAUtEHmxyzJpGQBVLV%2B1n1nKowz28niyFT3VdrdAkpgDd2yjxiP775wqcFq9rVPF0HwpUcmSo0r4kBxmdpHo7O2QSRlvYWgENIiJqLL6TGkbWUL%2FOzxbcTJic8hRw7ZrgUSZgYP0djJEwh0oI6VWn4gM9oGrkbG04fJwIqjt8nm3gtKRP048j8udQe4kCTeWxiLTtDg2Unkfo6JJLJldV3hvoFcoNSmLeZO6Ek9vgH%2BQAHCxxtUt%2BiQzHf%2FfL4SROhgXtJyC5n8G8g28Iy%2BYx5s%2B7HgxsrhRI5yU9AQB9chBanS%2FTfrLEl0Ceb1vgL%2Fwr110UAO1leDmqd2IBXwoYBDuQzZ46BSkPZQS%2F2e9OKCFKxzQtb%2FPPzQaMwlGUEl0CDeaGOo2DeX0GKlx35WjUkY3ufdQiz5q61Wst2aMvipwtorJcYipN3pOZuVHCWKIH96R0HHj4tGdC2mtRMFFJnivCgU9rP%2FGF82is6T%2Fh9p3lf1TGT1a5WsMZu%2Bx1bXb72FpSftbKLKqj8jFflSKuLRuA1hs5Wnn%2B5DutJtfwLZbfoJl3YNQKiA3oTylme%2BsWqzIaiOQtDeiCYjs81LVZ18gDrhqCw7kQtXjPj28g6gLV0KtIRIPKPe2v%2FyeBtvpy3vuwdjlQfIi%2FJO3cpwDCMJ61lbUGOrEBjqX2YJgjOwXJ8uBTalJ5YuAgURPg9QaFiL8AEkLZUhCSU96WS4goB4%2F0Ray0CDBv2HuJDM6vQVZ3cBkjIOxLGzlQn2kK%2FMpRji3c6%2BSdW34qoKoqJNrilcEf3pGpxYVf%2BA6y3yJ5U0Ivxa4p%2Fb%2BW3G81%2FX1YCgiD7p7kfXeRJjcc8wNq1Q4VH1qjC%2FwEScDvderqt%2BMbGHFLySNBw6u0hl%2B1fBe%2Bh3J93xzI1JnBuUHB&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20240727T205129Z&X-Amz-SignedHeaders=host&X-Amz-Expires=300&X-Amz-Credential=ASIAQ3PHCVTYYKAWSE7D%2F20240727%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Signature=43689722b126ea03b9dce29974567fc355c387d45c98f9e8f5d0ff3cee16e841&hash=ca9678d7d6c9187ba00d16a8b9dd7b000979c620d836e58a5462702fb917d735&host=68042c943591013ac2b2430a89b270f6af2c76d8dfd086a07176afe7c76c2c61&pii=S0304397596002204&tid=spdf-fca79a82-838e-4e95-95f0-0fb949416058&sid=68fad72494c7874f696a5848b571b6c71519gxrqb&type=client&tsoh=d3d3LnNjaWVuY2VkaXJlY3QuY29t&ua=040b58035e015f5f0302&rr=8a9f81fef83c83e1&cc=be
- [ ] https://www.graphclasses.org/classes/gc_24 linear
  - need modular decomposition https://pdf.sciencedirectassets.com/271538/1-s2.0-S0304397500X00606/1-s2.0-S0304397596002204/main.pdf?X-Amz-Security-Token=IQoJb3JpZ2luX2VjEB0aCXVzLWVhc3QtMSJHMEUCIQCkWUuC7isO2mBDyo2YNbnNtZr%2FPwt9VdA%2Bl%2FmBnqcI5gIgI3UQRhZM%2FqCmilVVdzQNnbwoysz%2BWWVx8UNZdmBPZukqvAUI9v%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAFGgwwNTkwMDM1NDY4NjUiDAp6QoR4uZD%2F1AtaSCqQBbx51JhV7vUdydziOfsEL8mYA1RbD75e67v9k6To2YKJprrBfkyRNs5wEXmKct5oCigeXtfk7RkWjFzqIbjLF6v740Ce%2Faf8UWdzTfhDw7BvH5GpFCZi4TG2g8zeTmt4wFso3EejQ1ASr3ULcLMwZ6P2QMi%2FHhB9vrDtUbQ6pFlMG731KoBo3RC6mDwz%2FVYDExAjT5wGv%2FY7ujhewzWzD6biAUtEHmxyzJpGQBVLV%2B1n1nKowz28niyFT3VdrdAkpgDd2yjxiP775wqcFq9rVPF0HwpUcmSo0r4kBxmdpHo7O2QSRlvYWgENIiJqLL6TGkbWUL%2FOzxbcTJic8hRw7ZrgUSZgYP0djJEwh0oI6VWn4gM9oGrkbG04fJwIqjt8nm3gtKRP048j8udQe4kCTeWxiLTtDg2Unkfo6JJLJldV3hvoFcoNSmLeZO6Ek9vgH%2BQAHCxxtUt%2BiQzHf%2FfL4SROhgXtJyC5n8G8g28Iy%2BYx5s%2B7HgxsrhRI5yU9AQB9chBanS%2FTfrLEl0Ceb1vgL%2Fwr110UAO1leDmqd2IBXwoYBDuQzZ46BSkPZQS%2F2e9OKCFKxzQtb%2FPPzQaMwlGUEl0CDeaGOo2DeX0GKlx35WjUkY3ufdQiz5q61Wst2aMvipwtorJcYipN3pOZuVHCWKIH96R0HHj4tGdC2mtRMFFJnivCgU9rP%2FGF82is6T%2Fh9p3lf1TGT1a5WsMZu%2Bx1bXb72FpSftbKLKqj8jFflSKuLRuA1hs5Wnn%2B5DutJtfwLZbfoJl3YNQKiA3oTylme%2BsWqzIaiOQtDeiCYjs81LVZ18gDrhqCw7kQtXjPj28g6gLV0KtIRIPKPe2v%2FyeBtvpy3vuwdjlQfIi%2FJO3cpwDCMJ61lbUGOrEBjqX2YJgjOwXJ8uBTalJ5YuAgURPg9QaFiL8AEkLZUhCSU96WS4goB4%2F0Ray0CDBv2HuJDM6vQVZ3cBkjIOxLGzlQn2kK%2FMpRji3c6%2BSdW34qoKoqJNrilcEf3pGpxYVf%2BA6y3yJ5U0Ivxa4p%2Fb%2BW3G81%2FX1YCgiD7p7kfXeRJjcc8wNq1Q4VH1qjC%2FwEScDvderqt%2BMbGHFLySNBw6u0hl%2B1fBe%2Bh3J93xzI1JnBuUHB&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20240727T205129Z&X-Amz-SignedHeaders=host&X-Amz-Expires=300&X-Amz-Credential=ASIAQ3PHCVTYYKAWSE7D%2F20240727%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Signature=43689722b126ea03b9dce29974567fc355c387d45c98f9e8f5d0ff3cee16e841&hash=ca9678d7d6c9187ba00d16a8b9dd7b000979c620d836e58a5462702fb917d735&host=68042c943591013ac2b2430a89b270f6af2c76d8dfd086a07176afe7c76c2c61&pii=S0304397596002204&tid=spdf-fca79a82-838e-4e95-95f0-0fb949416058&sid=68fad72494c7874f696a5848b571b6c71519gxrqb&type=client&tsoh=d3d3LnNjaWVuY2VkaXJlY3QuY29t&ua=040b58035e015f5f0302&rr=8a9f81fef83c83e1&cc=be
- [ ] https://www.graphclasses.org/classes/gc_502 linear
  - https://link.springer.com/content/pdf/10.1007/BF01082602.pdf 

## order $\le$ 6

- [x] https://www.graphclasses.org/classes/gc_921 = triangle-free AND max degree 4 -> easy to improve
- [ ] https://www.graphclasses.org/classes/AUTO_2153 maybe? complement of gc_921
- [ ] https://www.graphclasses.org/classes/gc_1074 maybe? = linear cliquewidth 2
- [x] https://www.graphclasses.org/classes/gc_625 = locally split
- [ ] https://www.graphclasses.org/classes/AUTO_2102.html = co locally split
- [ ] https://www.graphclasses.org/classes/gc_748
- [ ] https://www.graphclasses.org/classes/gc_260
- [ ] https://www.graphclasses.org/classes/gc_627
  - https://pdf.sciencedirectassets.com/271536/1-s2.0-S0012365X00X04268/1-s2.0-0012365X84900529/main.pdf?X-Amz-Security-Token=IQoJb3JpZ2luX2VjEIP%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJGMEQCIDb6Ao26m7h2Gd9oFnVbLnOOpyiGbDg8FpRsEogp1YiTAiBaca6V6ayw656o2ho%2Fso6wyIQy7dITPrwLgr6XhFrx2CqzBQh8EAUaDDA1OTAwMzU0Njg2NSIMbzuyv0unxyP%2FHmqqKpAFVVf7yKKbgAWuieZw0AmS6TZiw3kJO8m%2BFYIgjMNn8PrzeC8ivzqa7Kg13%2BFUXJ4aGAWoFj33QYjhxWMV40MPGm7hZV9V%2FSBY07ALFDr2IsxEcw7UEPhp74N9xEtb5W4mKknAwJ7jAS4IALkJ1F5ubfzmzdILrFZ6rOoBzQDqnaZW%2F%2F0F5lQ9MZ4feQ25jCWpNgvUejaOIw4Ud3qnACKbIQVJ2B7CxbLKRhtjfEuPXu6M1VVAQnnRAI3M%2BiQXDnChhu1AxlNx4zwEEzBSyUx4cQXNZoYesfSf2z0pZOB2Xg3s8HdtstQwn0fJpS%2FK%2F1z6YTMSJcLqiYhJzwzXbFdIPwKiJjWTiNsRUQAE5qvBvv6jgDQH6AjXI61PpLroZpiXv7Q2g%2BKXozGoCFYaF%2BoTMriovMIVBqMrXPeu3MJUqp2JmDf7PmcvT2AiSl246Ixh4DwocsaZa%2FbJkHQSRcfuVH0vOYsdOE3fsvw%2F9x1%2FqZGc7ecctOIfxPAd2hTbiqzwP7VqD2ihT2i75IYMu%2B0rXhp2i6YP378iFVchy8Ek2mZGuXQPACU%2BOYJyAZNo%2F8O%2FKxfziQi8q8EWu5JFJh52WtaG3RtYrDc8lv3mBAMvHewUoSegN7swYbIXobxMauUzTOhGL9wmnhrUIQogqOJF4Mu7RMz%2BxoG3Iw%2BjguQ8h6U4BNT75HCYVJyXDW74OmC%2BrRj0typEZa4Kam8FinOLkfUKQT2h4VJV3bIGQLFOlIFnTLYNZg1LJ5glthG8jO9l59E7LLBmhdFsvqfK4T1xw9TVI%2Fs31u0HlkbAVf7lMGmXogwp3Zud%2FoUnufZx%2FE6QEDKi%2BxSc3IzSBpuMgPxsrVqjzcDsaKCjCbGDB%2FWI%2FqYwi4nktQY6sgEu5%2BD8MCxkVyMJbzRG6bvNwChuSCgPSHejdT2k9S1snTwMFYuN99cJrTSdLNuBX1A8YQ4o3VTF6YFYRe1EeoCPLTChkvv9dbdsoYruFUkxZNJFwH0vszuoGBJL9M4PUE7JTAnNVQF4IJmZSPUR46mMlpi0izq2OKEqiTxP0hVtmBzwLSb%2BK9gZpUu7x%2FG55ucS9AxfV5qmTCRJx%2B8cZhiu2DSSDfhZFS4FeCdcmdSypmdz&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20240811T193611Z&X-Amz-SignedHeaders=host&X-Amz-Expires=300&X-Amz-Credential=ASIAQ3PHCVTYRKWKVXCV%2F20240811%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Signature=3a244eaa211f5da569f6a32a3d736343c781db272cc739cf9added385bb93910&hash=85591c28650ab0a5f37162b68e5997844c7f9a32c3573c41798f502aecb4a702&host=68042c943591013ac2b2430a89b270f6af2c76d8dfd086a07176afe7c76c2c61&pii=0012365X84900529&tid=spdf-1bf2a1fa-c10b-4f2a-9b08-79efdff5c27a&sid=a6887f2d4fb2f34b948b0ab1d8836f1690e0gxrqb&type=client&tsoh=d3d3LnNjaWVuY2VkaXJlY3QuY29t&ua=040b58005606060d5056&rr=8b1aac518ec1b70f&cc=be
  - looks reasonable to implement
- [ ] https://www.graphclasses.org/classes/AUTO_1765 linear
  - read https://sci-hub.ru/10.1016/0020-0190%2895%2900133-w
- [ ] https://www.graphclasses.org/classes/gc_188 linear
  - needs modular decomposition
- [ ] https://www.graphclasses.org/classes/gc_17 linear
  - https://digitalcommons.odu.edu/cgi/viewcontent.cgi?article=1116&context=computerscience_fac_pubs
  - resembles modular decomposition
- [ ] https://www.graphclasses.org/classes/AUTO_2073 = co-line: room for improvement (otoh, complement can be costly)
- [x] https://www.graphclasses.org/classes/gc_250 = line
- [ ] https://www.graphclasses.org/classes/gc_840 linear
  - need modular decomposition https://www.sciencedirect.com/science/article/abs/pii/S0020019096001342
- [ ] https://www.graphclasses.org/classes/gc_1108 linear
  - need modular decomposition https://www.sciencedirect.com/science/article/abs/pii/S0020019096001342

## order <= 7

- [ ] https://www.graphclasses.org/classes/gc_324 linear
- [ ] https://www.graphclasses.org/classes/gc_245 linear
  - [ ] quadratic time using permutation AND split
    - issue: return is_gc_313(graph) and is_permutation(graph)  # TODO circular import issues
- [x] https://www.graphclasses.org/classes/gc_686 = 2-bounded bipartite, room for improvement
- [ ] https://www.graphclasses.org/classes/gc_578 linear
  - [x] got a quadratic implementation using equivalence with dilworth 2

## order <= 8

- https://www.graphclasses.org/classes/gc_1022
  - see https://arxiv.org/abs/1103.1917: O(mn) time, O(n^2) space ... might cost too much for large graphs
- https://www.graphclasses.org/classes/gc_1225 use girth function in nx?
- https://www.graphclasses.org/classes/AUTO_744 linear
  - = probe-threshold AND split, so we need linear time algos for both (done for split already)
- [ ] https://www.graphclasses.org/classes/gc_806 linear, see Algorithm 5.3 in de Ridder's thesis whose code I tried to translate below:

```python
    # # WIP: equivalent to probe-threshold: https://www.graphclasses.org/classes/gc_799.html
    # # so recognizable in linear time
    # # order vertices by increasing degree
    # degrees = dict(graph.degree)
    # vertices = sorted(graph.nodes, key=degrees.get)
    # order = len(vertices)
    # lo, hi = min(vertices), max(vertices)
    # while lo <= hi:
    #     if degrees[lo] == order - hi:
    #         lo += 1
    #     elif degrees[hi] == order - lo:
    #         hi -= 1
    #     else:
    #         v_prime = {v for v in range(lo, hi + 1)}
    #         g_prime = graph.subgraph(v_prime)
    #         p_set = set(g_prime[hi])
    #         n_set = v_prime - p_set
    #         # P, N is a valid partition iff N is independent and ...? TODO
    #         if g_prime.subgr
    #         pass
    #
```

## order <= 9

- [ ] https://www.graphclasses.org/classes/gc_1035 linear
  - https://www.sciencedirect.com/science/article/pii/S0304397513008645; looks tedious

## order <= 10

nothing

## order <= 11

nothing

## order <= 13

- [ ] https://www.graphclasses.org/classes/gc_1031 linear
  - see https://sci-hub.ru/10.1137/110829222

## recognizers_n

TODO

- []

## recognizers_n_2

- [ ] is_unbreakable
- [ ] is_partial_cube

## recognizers_n_3

- [ ] nx.is_at_free
- [ ] explicit_independent_triplets
- [ ] is_maximal_planar: linear-time algo
- [ ] is_co_paw_odd_anti_hole_free
- [ ] is_median: subquadratic algorithm
- [ ] is_median_and_planar: linear time algo
- [ ] is_pseudo_modular
- [ ] is_interval_regular

## recognizers_n_5

- [ ] is_perfect_elimination_bipartite: O(n³)
- 


# Buggy recognizers (disabled for now)


## recognizers_n

- [ ] is_middle


## recognizers_n_3

- [ ] is_weakly_modular
- [ ] is_probe_co_bipartite: NOT disabled, so is it buggy or not?

## recognizers_n_6

- [x] check is_p4_tidy, since xc_unpacker was maybe buggy
- [x] implement recognizers based on p4-tidy
  - [x] https://www.graphclasses.org/classes/gc_961.html
  - [x] https://www.graphclasses.org/classes/AUTO_3683.html
  - [x] https://www.graphclasses.org/classes/gc_13.html

# Missing recognizers


## recognizers_n


- [ ] [5-leaf-power](https://www.graphclasses.org/classes/gc_825.html) : Chang and Ko [23] give a linear
time algorithm for the 3-Steiner root problem, so implying that the k-leaf power recognition
problem can be solved in linear time for k = 5.

M.-S. Chang and M.-T. Ko. The 3-steiner root problem. In A. Brandst ̈adt, D. Kratsch, and H. M ̈uller, editors,
WG, volume 4769 of Lecture Notes in Computer Science, pages 109–120. Springer, 2007

- [ ] is_co_connected
- [x] is_co_chordal in linear time
- [ ] is_probe_trivially_perfect (algo 5.1 p 93 in de Ridder's thesis)

## recognizers_n_2

- [ ] is_apex: linear-time algo (hard to implement?)
- [ ] is_line_graph_of_bipartite_graph: complement class

## recognizers_n_3

- [ ] helly circular arc graphs: cubic? linear?

## recognizers_n_5

- [ ] biclique-helly graphs


## recognizers_n_6

- [ ] friends of p4-tidy



## others


- [ ] implement https://inria.hal.science/hal-01196866/document (theorem on page 193) for probe diamond-free graphs (some smallgraphs not in isgci atm)
- [ ] now i have comparability and therefore permutation
  - [ ] implement every recognizer that relies on comparability TODO list
  - [ ] implement every recognizer that relies on co-comparability
    - [ ] C4-free ∩ co-comparability: definition is O(n^2), which beats the equivalent is_interval recognizer in O(n^3)
    - [ ] alternately orientable ∩ co-comparability
      - requires implementing is_alternately_orientable: https://www.graphclasses.org/classes/gc_25.html
    - [x] bipartite ∩ co-comparability = bipartite permutation
    - [x] chordal ∩ co-chordal ∩ co-comparability ∩ comparability = (2K2,C4,C5,S3,co-rising sun,net,rising sun)-free
    - [x] chordal ∩ co-comparability = interval 
    - [x] co-comparability
    - [x] co-comparability ∩ comparability = is_permutation
    - [ ] co-comparability ∩ tolerance: UNKNOWN
    - [x] co-comparability ∪ comparability
  - [ ] implement every recognizer that relies on permutation
    - [x] bipartite permutation https://www.graphclasses.org/classes/gc_81.html
            easy: bipartite AND permutation
    - [ ] circular permutation https://www.graphclasses.org/classes/gc_135.html
            easy (http://doi.wiley.com/10.1002/net.3230120407):
                take any vertex v, and let G' be the graph obtained from G by "switching" N(v); then
                G is CPG <=> G is comparability AND G' is a PG
    - [ ] permutation ∩ split
            easy; could replace equivalent class https://www.graphclasses.org/classes/gc_245.html
    - [ ] probe permutation: open


# Available recognizers in other packages

- [ ] is_perfect: https://doc.sagemath.org/html/en/reference/graphs/sage/graphs/graph.html#sage.graphs.graph.Graph.is_perfect
- they have a lot in sage: https://doc.sagemath.org/html/en/reference/graphs/sage/graphs/graph.html
- shouldn't be hard: https://www.graphclasses.org/classes/gc_966.html

- create is_block algo for https://www.graphclasses.org/classes/gc_93.html , should be faster than

- sage has a lot of recognition algos, but i might have many of them already or they're not efficient. check anyway

https://github.com/sagemath/sage/blob/b5c9cf037cbce672101725f269470135b9b2c5c4/src/sage/graphs/graph.py#L1751-L1805

their graph class has the following recognition methods (grep "def is_"):

- [x] def is_directed(self):                                      useless, we have networkx
- [x] def is_tree(self, certificate=False, output='vertex'):      useless, we have networkx
- [x] def is_forest(self, certificate=False, output='vertex'):    useless, we have networkx
- [x] def is_cactus(self):                                        adapted
- [x] def is_biconnected(self):                                   useless, we have networkx
- [ ] def is_block_graph(self):
        equivalent to chordal and diamond-free, which I have already, so not high priority (check their complexity first anyway)
- [ ] def is_cograph(self):
        equivalent to P_4-free, which I have already, so not high priority (check their complexity first anyway)
- [ ] def is_apex(self):
        TODO check if their algo is more efficient, but I have mine already

- [ ] def is_overfull(self):
        not found in ISGCI

- [ ] def is_even_hole_free(self, certificate=False):
        might be worth it, but I think their implementation is naive (search for all induced cycles of even length)

- [ ] def is_odd_hole_free(self, certificate=False):
        might be worth it, but I think their implementation is naive (search for all induced cycles of odd length)

- [ ] def is_triangle_free(self, algorithm='bitset'):
        TODO check if their algo is more efficient, but I have mine already

- [ ] def is_split(self):
        TODO check if their algo is more efficient, but I have mine already

- [ ] def is_perfect(self, certificate=False):
        TODO should be interesting
            boils down to testing whether G and complement are odd hole free, so we need an efficient algo for that

- [ ] def is_edge_transitive(self):
        not found in ISGCI

- [ ] def is_arc_transitive(self):
        not found in ISGCI

- [ ] def is_half_transitive(self):
        not found in ISGCI

- [ ] def is_semi_symmetric(self):
        not found in ISGCI

- [x] def is_polyhedral(self):        I use the same algo

- [ ] def is_circumscribable(self, solver="ppl", verbose=0):
        not found in ISGCI

- [ ] def is_inscribable(self, solver="ppl", verbose=0):
        not found in ISGCI

- [ ] def is_prime(self):
        not found in ISGCI




# Others

- sage has modular decomposition https://doc.sagemath.org/html/en/reference/graphs/sage/graphs/graph_decompositions/modular_decomposition.html
- actually, DO NOT USE MODULAR DECOMPOSITIONS: see what we can achieve with lexbfs instead
  - adapt Epstein's implementation to nx graphs
  - and then we can recognize: (according to https://www.researchgate.net/profile/Michel-Habib/publication/220532677_A_Simple_Linear_Time_LexBFS_Cograph_Recognition_Algorithm/links/02bfe510bf18e9e447000000/A-Simple-Linear-Time-LexBFS-Cograph-Recognition-Algorithm.pdf)
    - cographs
    - chordal graphs
    - interval graphs
    - unit interval graphs
    - bipartite permutation graphs,
    - ... ?
- but for some other classes, we'll need modular decomposition

# Recognizers or auxiliary functions in progress

## recognizers_n

- [ ] is_2_subdivision
- [ ] is_k_bounded_bipartite
- [ ] is_star_convex
- [ ]

## recognizers_n_4

- [ ] is_equimatchable

# Misc

FIND MORE POSITIVE DATASETS FOR TESTING!
FIND MORE NEGATIVE DATASETS FOR TESTING!

use the exclusion digraph for testing as well (check that if f(G) is true, then g(G) is False)

# Profitable hereditary classes

The following classes are profitable hereditary:

- https://www.graphclasses.org/classes/gc_539.html      O(n^2)
- https://www.graphclasses.org/classes/gc_14.html O(n^4) not sure
- https://www.graphclasses.org/classes/gc_90.html linear
- https://www.graphclasses.org/classes/gc_1273.html not sure
- https://www.graphclasses.org/classes/gc_371.html in theory we can do better than O(n^3), but ... (matrix mul)


## profitable_hereditary_n_4

- [ ] is_gc_394(graph: nx.Graph) -> bool:    # TODO: doable in linear time according to de Ridder's thesis
