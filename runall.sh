#!/bin/bash

# 4 2 run 1
python gendata-graph.py gen uniform $1 $2
time python carpool.py astar data/generated_uniform_$1_$2.txt
time python carpool.py dfs data/generated_uniform_$1_$2.txt
time python carpool.py baseline data/generated_uniform_$1_$2.txt
time python carpool.py projection data/generated_uniform_$1_$2.txt
time python carpool.py knearest data/generated_uniform_$1_$2.txt
time python carpool.py agglomerative data/generated_uniform_$1_$2.txt
time python carpool.py ucs data/generated_uniform_$1_$2.txt
