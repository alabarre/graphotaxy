# Perm

Perm will output the permutation graphs on `n` vertices to `Stdout` encoded with [Graph6](https://users.cecs.anu.edu.au/~bdm/data/formats.txt) encoding. 


## Usage

An executable can be built with `go build perm.go`, or the code can be run directly with `go run perm.go`.

- The flag `-n` must be specified with the value of `n`. 
- The flag `-numWorkers` may be specified to split the calculation across multiple goroutine with the aim of running the enumeration in parallel.

The following snippet generates all permutation graphs on 10 vertices using 2 goroutines outputs them to standard out.

```
go run perm.go -numWorkers 2 -n 10
```

## Number of circle graphs and approximate file sizes

|  n | Number of graphs | File size |
|---:|-----------------:|----------:|
|  1 |                1 |        2B |
|  2 |                2 |        6B |
|  3 |                4 |       12B |
|  4 |               11 |       33B |
|  5 |               33 |      132B |
|  6 |              142 |      710B |
|  7 |              776 |    4.54KB |
|  8 |             5699 |    38.9KB |
|  9 |            50723 |     396KB |
| 10 |           524572 |    5.00MB |
| 11 |          6037518 |    69.1MB |
| 12 |         75912033 |     941MB |
| 13 |       1029974969 |    14.4GB |
| 14 |      14974215412 |           |