
import re
import os
import os.path as path
import argparse

import numpy as np
import networkx as nx

from data import Explorer
from algos import algorithms

def read_data(f):
  """
  Data format:
  <number of locations>
  <person1 location x-cood> <person1 location y-cood> <person1 car capacity>
  <person2 location x-cood> <person2 location y-cood> <person2 car capacity>
  ...
  <goal location x-cood> <goal location y-cood>
  <edge1 origin id> <edge1 dest id> <edge1 weight>
  <edge2 origin id> <edge2 dest id> <edge2 weight>
  ...

  note that person-id is the same as location-id
  goal state is (number of locations - 1)
  """
  ex = Explorer(ARGV.verbose)
  # num locations
  ex.num_locations = int(f.next().strip())
  ex.num_people = ex.num_locations - 1
  ex.locations = [ None ] * ex.num_locations
  ex.people_capacity = [ None ] * ex.num_people
  ex.pickup_costs = [ {} for i in xrange(ex.num_people) ]
  for i in xrange(ex.num_people):
    # people location and capacities
    line = f.next().rstrip()
    m = re.search(r"(\d+(\.\d+)?)\s+(\d+(\.\d+)?)\s+(\d+)", line)
    ex.locations[i] = (float(m.group(1)), float(m.group(3)))
    ex.people_capacity[i] = int(m.group(5))
  # parse goal location
  line = f.next().rstrip()
  m = re.search(r"(\d+(\.\d+)?)\s+(\d+(\.\d+)?)", line)
  ex.goal = (float(m.group(1)), float(m.group(3)))
  ex.locations[-1] = ex.goal
  # num edges
  ex.num_edges = ((ex.num_locations - 1) * ex.num_locations) / 2
  ex.distances = nx.Graph()
  for i in xrange(ex.num_edges):
    # edge weights
    line = f.next().rstrip()
    m = re.search(r"(\d+)\s+(\d+)\s+(\d+(\.\d+)?)", line)
    origin = int(m.group(1))
    dest = int(m.group(2))
    wt = float(m.group(3))
    ex.distances.add_edge(origin, dest, weight=wt)
  ex.verify_initialized()
  return ex

def output_results(ex, input_f, method, min_cost, assignment):
  print "---* {} results *---".format(method)
  cwd = path.dirname(path.abspath(__file__))
  output_folder = path.join(cwd, "output")
  if not path.exists(output_folder):
    os.mkdir(output_folder)
  output_fname = method + "_" + path.basename(input_f.name)
  with open(path.join(output_folder, output_fname), "w") as out:
    print "Minimum cost: {:.2f}".format(min_cost)
    out.write(str(min_cost) + "\n")
    print 'Minimum assignment: '
    for i in range(len(assignment)):
      # is a driver
      if (assignment[i] != None):
        print "{} drives {}".format(i, assignment[i])
        out.write(str(assignment[i]) + "\n")
    if not ARGV.verbose:
      return
    print "Edge weights:"
    print "\t",
    print "\t".join([ str(item) for item in ex.distances.nodes() ])
    for origin in ex.distances.nodes():
      print "{}\t".format(origin),
      for dest in ex.distances.nodes():
        if ex.distances.has_edge(origin, dest):
          print "{:.2f}\t".format(ex.distances[origin][dest]["weight"]),
        else:
          print "0.0\t",
      print

def main():
  ex = read_data(ARGV.input)
  print "---* dataset *---"
  print ex
  print "Drivers: {}".format(filter(lambda p: ex.people_capacity[p] > 0, range(ex.num_people)))
  if ARGV.verbose: print "---* {} running *---".format(ARGV.method)
  min_cost, assignment = algorithms[ARGV.method](ex)
  output_results(ex, ARGV.input, ARGV.method, min_cost, assignment)

parser = argparse.ArgumentParser(description='Carpooling')
parser.add_argument("-v", "--verbose", help="Include debug output", action="store_true")
parser.add_argument("method", help="Algorithm to use for solving", choices=algorithms.keys())
parser.add_argument("input", help="Input filename", type=argparse.FileType('r'))
ARGV = parser.parse_args()

if __name__ == '__main__':
  main()
