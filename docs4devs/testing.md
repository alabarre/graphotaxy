---
title: Testing recognizers
author: Anthony Labarre
date: 2024-2026
---

# Running tests

Tests are located in the `./tests/` subdirectory. To run all tests, go to the project's root and run:

```commandline
python3 -m unittest
```

If you only want to run tests contained in a specific file, run:

```commandline
python3 -m unittest tests/SOME_TEST_FILE.py 
```

# ~~Writing~~ Generating tests

Testing recognizers is difficult because relatively few datasets exist (compared to the sheer and ever-growing number of classes in ISGCI), and tests are tedious to write. We bypass those difficulties using a script that generates tests automatically from each dataset we have. We need "positive" tests (to verify that members of a graph class are correctly identified as such) and "negative" tests (to verify that graphs that do not belong to a graph class are not identified as such). More explanations follow, but if you just want to generate all those tests, simply go to the `./src/` directory and type:

```commandline
python3 generate_tests.py
```

All generated tests will be written to the `./tests/` directory.

Of course, you can also write your own tests manually, but you really don't have to. If you decide to do that anyway, following the structure of tests in the automatically generated test files will be helpful. You will need to:

1. write them in the `./tests/` directory;
2. name them anything you want except `test_*_and_related.py`: this naming scheme is used by `generate_tests.py`, which when run erases all files following this naming convention before generating new tests to avoid mixups between different runs.


## Positive tests

A dataset for a class `dummy_id` contains graphs for which the corresponding recognizer `is_dummy` should return `True`. By inclusion, a member of class `dummy_id` is also a member of all classes that contain it; therefore, a dataset for class `dummy_id` allows us to generate positive tests not only for the function `is_dummy`, but for all available recognizers for classes that contain `dummy_id`.

### Negative tests

Datasets also allow us to generate negative tests, but for this we need an *exclusion graph*, which summarizes separation relationships between graph classes (e.g., the fact that if a graph is a tree, then it cannot be a cubic graph). The exclusion graph is stored in `./src/isgci/exclusion-graph.dot` . 

Again, a dataset for a class `dummy_id` contains graphs for which the corresponding recognizer `is_dummy` should return `True`. The exclusion relationships tell us for which classes the corresponding recognizer should return `False` for the same dataset. Therefore, for every positive dataset for class `dummy_id`, we also generate negative tests for recognizers for classes that are known not to contain graphs from the dataset for `dummy_id`.


# Datasets

Never be afraid to add missing datasets, even if the classes seem "trivial". Each dataset can reveal problems in the software, which can then be fixed.

# Test outcomes

A failed test can mean:

1. that a recognizer is flawed;
1. that an inclusion relationship is wrong;
1. that an exclusion relationship is wrong;
1. that the dataset is wrong.

Keep an open mind and don't refrain from investigating any option. To help you detect which is which:

- if the outcome of a test contains "AssertionError: True is not false", then this means the test expected a negative answer, which happens when a class is excluded by another class. The lines following the FAIL message are helpful, for instance:

    FAIL: test_ZZZ (tests.test_XXX_and_related.Test_XXX_and_related.test_ZZZ)
    Tests negative instances for class ZZZ. ZZZ is a descendant of excluded class YYY.
    
  This **might** mean that the exclusion relationship XXX -> YYY is wrong and should be deleted from `./isgci/exclusion_graph.dot`.

- if the outcome of a test contains "AssertionError: False is not true", then this means the test expected a positive answer, which happens when a class is included in another class. The lines following the FAIL message are helpful, for instance:
