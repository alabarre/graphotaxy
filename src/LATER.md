# `graph_analyzer`

- [ ] using a `dict` for classifications forces me to keep all input graphs until the end of the analysis; if that is
  not useful, find a different way to proceed; for instance:
    - analyze graphs as we read them, but don't copy them to a dictionary: `self.classifications` then becomes a list,
      to which we append classifications as we go. And then we just feed the input file to the analyzer instead of a
      list of graphs
    - of course, it's nice to be able to know where we are with tqdm and this requires knowing how many graphs we have.
      So maybe we load them all into a deque, then keep popping left from it as we go? unless the format allows us to
      know how many graphs we have
        - well a simple `wc -l` on a file gives the answer, so I guess Python should be able to find out natively

# `main`

- [ ] option for enabling "hard" recognizers -- i.e., recognizers with an exponential running time.

# others

- [ ] find fisc for a given class: input = class id, output = basis of forbidden smallgraphs in ISGCI
    - WARNING: make sure user understands that it might be wrong to assume that the output is:
        - a complete fisc: e.g., we cannot have a finite fisc for bipartite graphs
        - a valid fisc at all: we don't know that the given class is indeed hereditary, so it's the responsibility of
          the user to know that