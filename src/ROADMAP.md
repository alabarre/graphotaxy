# Plans

## Distribution packages

- [x] isgci (simpler)
- [x] graph_recognition
- [ ] graph_classification?
... ?

When all these are "mature", they will eventually become external packages on PiPY.

## Testing

Testing is easy:

1. use `python3 generate_tests.py` to generate the test suite;
2. use `python3 -m unittest` to run all tests

So once a new recognizer is written, make sure it passes all tests before committing.

Caveats:

- I only have *positive* tests
- I don't have enough datasets

# code

- [ ] use type hinting everywhere
- [ ] use black / tox for auto formatting

# smallgraphs

- [x] use hereditary classes
- [x] actually, move profitable hereditary classes to their respective modules

# modular decomposition

modular decomposition is useful in recognizing various classes, for instance (list should be much longer):

- [ ] p4-limited graphs https://sci-hub.ru/10.1142/S0129054199000083
- 


# exclusion relationships

So far we've only been using inclusion relationships between graphs, allowing us to say that:

- if G is in C, then G is in all superclasses of C
- if G is not in C, then G is not in any subclass of C

We want to push things further by introducing *exclusion* relationships: instead of inclusion relationships like "being in C -> being in D", we want to take advantage of:

- if G is in C, then G is not in some other class D
- if G is not in C, then G is in some other class D


TODO gather somewhere such exclusion relationships. Examples:

- [ ] [10.1002/jgt.3190150403] p. 351: Every unbreakable graph contains a P_4; therefore, unbreakable -> NOT P_4-free, and P_4-free -> NOT unbreakable

TODO eventually, switch to graph-tool which is more efficient. Right now I can't because:
- I'm installing everything with pip, and graph-tool is not pip-installable
- if I give up on pip, I need a higher version of networkx than I have on Debian, since we need girth
- even so, be careful and think about how to switch, carry out some preliminary tests first


SOMEDAY

- [ ] dependent recognizers
- [ ] "hard" classes