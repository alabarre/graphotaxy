package main

import (
	"flag"
	"fmt"
	"math/bits"
	"os"
	"time"

	"github.com/Tom-Johnston/mamba/graph"
	"github.com/Tom-Johnston/mamba/graph/search"
)

func main() {

	start := time.Now()
	nPtr := flag.Int("n", -1, "the number of vertices in the generated circle graphs")
	numWorkersPtr := flag.Int("numWorkers", 1, "the number of goroutines used to generate the graphs")

	flag.Parse()

	fmt.Println(flag.Arg(0))

	n := *nPtr

	if n == -1 {
		panic("The option -n must be specified and a non-negative integer.")
	}

	numWorkers := *numWorkersPtr

	output := make(chan *graph.DenseGraph, 1)

	fmt.Fprintf(os.Stderr, "Enumerating permutation graphs on %v vertices.\n", n)
	go enumerateParallel(n, numWorkers, output)

	counter := 0
	for g := range output {
		s := graph.Graph6Encode(g)
		fmt.Println(s)
		counter++
	}

	fmt.Fprintln(os.Stderr, "Graphs: ", counter)
	fmt.Fprintf(os.Stderr, "Took %v\n", time.Since(start))
}

//enumerateParallel enumerates all circle graphs on n vertices using numWorkers goroutines and sends them to output.
func enumerateParallel(n int, numWorkers int, output chan *graph.DenseGraph) {
	counter := numWorkers
	count := make(chan bool)
	for i := 0; i < numWorkers; i++ {
		c := make(chan *graph.DenseGraph)
		tmp := i

		U := make([]uint, n)
		D := make([]uint, n)
		implicants := []intPair{}
		neighbours := make([]uint, n)

		go func() {
			go search.WithPruning(n, c, tmp, numWorkers, func(g *graph.DenseGraph) bool { return false }, func(g *graph.DenseGraph) bool { return !isPermutationGraph(g, U, D, neighbours, implicants) })
			for v := range c {
				output <- v
			}
			count <- false
		}()
	}
	for {
		<-count
		counter--
		if counter == 0 {
			close(output)
		}
	}
}

func isPermutationGraph(g *graph.DenseGraph, U, D, neighbours []uint, implicants []intPair) bool {

	n := g.NumberOfVertices

	neighbours = neighbours[:n]
	for i := range neighbours {
		neighbours[i] = 0
	}

	for i := 0; i < n; i++ {
		for j := i + 1; j < n; j++ {
			if g.IsEdge(i, j) {
				neighbours[i] |= (1 << uint(j))
				neighbours[j] |= (1 << uint(i))
			}
		}
	}

	if !isTransitive(neighbours, U, D, implicants) {
		return false
	}

	var mask uint = (1 << uint(n)) - 1
	for i := range neighbours {
		neighbours[i] = ^neighbours[i]
		neighbours[i] ^= (1 << uint(i))
		neighbours[i] &= mask
	}

	return isTransitive(neighbours, U, D, implicants)
}

type intPair struct {
	i int
	j int
}

func isTransitive(neighbours []uint, U, D []uint, implicants []intPair) bool {
	n := len(neighbours)
	U = U[:n]
	copy(U, neighbours)
	D = D[:n]

	var edge intPair
	implicants = implicants[:0]
algLoop:
	for {
		for i := range D {
			D[i] = 0
		}

		//Step A
		for i, v := range U {
			if v != 0 {
				j := bits.TrailingZeros(v)
				U[i] ^= (1 << uint(j))
				U[j] ^= (1 << uint(i))
				D[i] |= (1 << uint(j))
				implicants = append(implicants, intPair{i: i, j: j})
				break
			}
		}
		//Step B
		for len(implicants) > 0 {
			edge, implicants = implicants[len(implicants)-1], implicants[:len(implicants)-1]
			i, j := edge.i, edge.j
			//Get the i' which are neighbours of i but not neighbours of j. Note we
			c := U[i] & (^neighbours[j])
			//Iterate over all i' and direct the edge from i to i'
			for c != 0 {
				y := c & -c
				v := bits.TrailingZeros(c)
				c ^= y

				U[i] ^= (1 << uint(v))
				U[v] ^= (1 << uint(i))
				D[i] ^= (1 << uint(v))
				implicants = append(implicants, intPair{i: i, j: v})
			}

			//Get the j' which are neighbours of j but not neighbours of i.
			c = U[j] & (^neighbours[i])
			//Iterate over all j' and direct the edge from j' to j
			for c != 0 {
				y := c & -c
				v := bits.TrailingZeros(c)
				c ^= y

				U[j] ^= (1 << uint(v))
				U[v] ^= (1 << uint(j))
				D[v] ^= (1 << uint(j))
				implicants = append(implicants, intPair{i: v, j: j})
			}
		}

		//Step C
		//The TRD test

		for i, c := range D {
			var w uint
			for c != 0 {
				y := c & -c
				j := bits.TrailingZeros(c)
				c ^= y

				w |= D[j]
			}
			//Refresh c
			c = D[i]

			//Check if there are any bits in w which are not set in c
			if w&(^c) != 0 {
				return false
			}
		}

		//Step D
		//Check if there are any undirected edges left.
		for _, v := range U {
			if v != 0 {
				continue algLoop
			}
		}

		return true
	}
}
