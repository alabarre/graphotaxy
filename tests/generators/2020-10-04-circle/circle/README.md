# Circle

Circle will output the circle graphs on `n` vertices to `Stdout` encoded with [Graph6](https://users.cecs.anu.edu.au/~bdm/data/formats.txt) encoding. 


## Usage

An executable can be built with `go build circle.go`, or the code can be run directly with `go run circle.go`.

- The flag `-n` must be specified with the value of `n`. 
- The flag `-numWorkers` may be specified to split the calculation across multiple goroutine with the aim of running the enumeration in parallel.

The following snippet generates all circle graphs on 10 vertices using 2 goroutines outputs them to standard out.

```
go run circle.go -numWorkers 2 -n 10
```

## Number of circle graphs and approximate file sizes

|  n | Number of graphs | File size |
|---:|-----------------:|----------:|
|  1 |                1 |       12B |
|  2 |                2 |       22B |
|  3 |                4 |       38B |
|  4 |               11 |       94B |
|  5 |               34 |      346B |
|  6 |              154 |    1.81KB |
|  7 |              978 |    13.3KB |
|  8 |             9497 |     148KB |
|  9 |           127954 |    2.19MB |
| 10 |          2165291 |   20.65MB |
| 11 |         42609994 |   487.6MB |
| 12 |        937233306 |    11.3GB |
| 13 |      22576188846 |           |