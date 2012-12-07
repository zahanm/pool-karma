#!/bin/bash

mkdir -p "time"
mkdir -p "results"

# 4 2 run 1
python gendata-graph.py gen uniform $1 $2

echo "astar"
time (python carpool.py astar data/generated_uniform_$1_$2.txt > "results/astar_$1_$2.txt") 2> "time/astar_$1_$2.txt"
cat "time/astar_$1_$2.txt" | grep "user"
cat "results/astar_$1_$2.txt" | grep "Minimum cost"

echo "dfs"
time (python carpool.py dfs data/generated_uniform_$1_$2.txt > "results/dfs_$1_$2.txt") 2> "time/dfs_$1_$2.txt"
cat "time/dfs_$1_$2.txt" | grep "user"
cat "results/astar_$1_$2.txt" | grep "Minimum cost"

echo "baseline"
time (python carpool.py baseline data/generated_uniform_$1_$2.txt > "results/baseline_$1_$2.txt") 2> "time/baseline_$1_$2.txt"
cat "time/baseline_$1_$2.txt" | grep "user"
cat "results/astar_$1_$2.txt" | grep "Minimum cost"

echo "projection"
time (python carpool.py projection data/generated_uniform_$1_$2.txt > "results/projection_$1_$2.txt") 2> "time/projection_$1_$2.txt"
cat "time/projection_$1_$2.txt" | grep "user"
cat "results/astar_$1_$2.txt" | grep "Minimum cost"

echo "knearest"
time (python carpool.py knearest data/generated_uniform_$1_$2.txt > "results/knearest_$1_$2.txt") 2> "time/knearest_$1_$2.txt"
cat "time/knearest_$1_$2.txt" | grep "user"
cat "results/astar_$1_$2.txt" | grep "Minimum cost"

echo "agglomerative"
time (python carpool.py agglomerative data/generated_uniform_$1_$2.txt > "results/agglomerative_$1_$2.txt") 2> "time/agglomerative_$1_$2.txt"
cat "time/agglomerative_$1_$2.txt" | grep "user"
cat "results/astar_$1_$2.txt" | grep "Minimum cost"

echo "ucs"
time (python carpool.py ucs data/generated_uniform_$1_$2.txt > "results/ucs_$1_$2.txt") 2> "time/ucs_$1_$2.txt"
cat "time/ucs_$1_$2.txt" | grep "user"
cat "results/astar_$1_$2.txt" | grep "Minimum cost"
