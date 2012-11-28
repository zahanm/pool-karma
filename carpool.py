
import re
import sys

import networkx as nx

from search import Explorer

def read_data(fname):
  """
  Data format:
  <number of locations>
  <person1 location x-cood> <person1 location y-cood> <person1 car capacity>
  <person2 location x-cood> <person2 location y-cood> <person2 car capacity>
  ...
  <number of edges>
  <edge1 origin> <edge1 dest> <edge1 weight>
  <edge2 origin> <edge2 dest> <edge2 weight>
  ...

  note that person-id is the same as location-id
  goal state is (number of locations - 1)
  """
  with open(fname) as f:
    ex = Explorer()
    ex.num_locations = int(f.next().strip())
    ex.num_people = ex.num_locations - 1
    ex.people_locations = [ None ] * ex.num_people
    ex.people_capacity = [ None ] * ex.num_people
    ex.pickup_costs = [ {} ] * ex.num_people
    for i in xrange(ex.num_people):
      line = f.next().rstrip()
      m = re.search(r"(\d+(\.\d+)?)\s+(\d+(\.\d+)?)\s+(\d+)", line)
      ex.people_locations[i] = (m.group(1), m.group(3))
      ex.people_capacity[i] = m.group(5)
    ex.num_edges = int(f.next().strip())
    ex.distances = nx.Graph()
    for i in xrange(ex.num_edges):
      line = f.next().rstrip()
      m = re.search(r"(\d+)\s+(\d+)\s+(\d+(\.\d+)?)", line)
      origin = m.group(1)
      dest = m.group(2)
      wt = m.group(3)
      ex.distances.add_edge(origin, dest, weight=wt)
    ex.verify_initialized()
    print ex

def main():
  assert len(sys.argv) == 2
  read_data(sys.argv[1])

if __name__ == '__main__':
  main()
