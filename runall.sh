#!/bin/bash

# 4 2 run 1
python gendata-graph.py gen uniform $1 $2
echo "astar"
time python carpool.py astar data/generated_uniform_$1_$2.txt 2>&1 | grep "user"
echo "dfs"
time python carpool.py dfs data/generated_uniform_$1_$2.txt 2>&1 | grep "user"
echo "baseline"
time python carpool.py baseline data/generated_uniform_$1_$2.txt 2>&1 | grep "user"
echo "projection"
time python carpool.py projection data/generated_uniform_$1_$2.txt 2>&1 | grep "user"
echo "knearest"
time python carpool.py knearest data/generated_uniform_$1_$2.txt 2>&1 | grep "user"
echo "agglomerative"
time python carpool.py agglomerative data/generated_uniform_$1_$2.txt 2>&1 | grep "user"
echo "ucs"
time python carpool.py ucs data/generated_uniform_$1_$2.txt 2>&1 | grep "user"
