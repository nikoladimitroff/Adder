# Adder
### An AI library in Python
---------
## Purpose
Adder is meant to be a developer-friendly and easy-to-learn library that provides implementations of many AI algorithms (and a few other that ease working with graphs and trees in general).

Take a look at the [wiki to get started][wiki].

## Development log
Here's where the library currently stands:

* Utilities for defining various models of problems (from graph, from a set of functions, etc.)
* Algorithms for classical searching:
 * BFS, DFS
 * Depth-limited search, Iterative Deepening Search
 * A\*
* Algorithms for nonclassical searching:
 * Hill climbing, Random-restart
 * Simulated Annealing
 * Genetics
* Classical Propositional Logic:
 * Parsing sentences into formulas in Conjunctive Normal Form (thus having a human-readable representation of the knowledge base)
 * Forward and backwards chaining on Definite Knowledge Bases
 * Theorem proving in random Propositional Knowledge Bases with several optimizations
* Classical First-Order Logic:
 * Backwards chaining for Definite Knowledge Bases
 * General theorem proving for First-Order Knowledge Bases
* Fuzzy Logic:
 * Inference
 * Standard fuzzy sets - triangles, shoulders.

## Demos
Currently, there are several demos you can play with. Run them with
```python
python main.py <demo-name> [<demo-args>]
```
where
```
<demo-name> = snake | picture | definitekb | resolutionkb
<demo-args> = <snake-field-size> <snake-obstacles-count> | one of the three - winnie toucan eagle | no args | no args
```

## Upcoming features

* Probabilistic Knowledge Bases
* Machine learning


[wiki]: https://github.com/NikolaDimitroff/Adder/wiki
