
import re
import sys

import networkx as nx

from search import Explorer

def read_data(fname):
  """
  Data format:
  <number of people>
  <person1 car capacity>
  <person2 car capacity>
  ...
  <number of edges>
  <edge1 origin> <edge1 dest> <edge1 weight>
  <edge2 origin> <edge2 dest> <edge2 weight>
  ...
  """
  with open(fname) as f:
    ex = Explorer()
    ex.num_locations = int(f.next().strip())
    ex.num_edges = int(f.next().strip())
    ex.distances = nx.Graph()
    for i in xrange(ex.num_edges):
      line = f.next().rstrip()
      m = re.search(r"(\d+)\s+(\d+)\s+(\d+(\.\d+)?)", line)
      origin = m.group(1)
      dest = m.group(2)
      wt = m.group(3)
      ex.distances.add_edge(origin, dest, weight=wt)
    ex.num_people = int(f.next().strip())
    ex.people_locations = [ None ] * ex.num_people
    ex.people_capacity = [ None ] * ex.num_people
    for i in xrange(ex.num_people):
       line = f.next().rstrip()
       m = re.search(r"(\d+)\s+(\d+)", line)
       person_location = m.group(1)
       person_capacity = m.group(2)
       ex.people_locations[i] = person_location
       ex.people_capacity[i] = person_capacity
    ex.verify_initialized()
    print ex

def main():
  assert len(sys.argv) == 2
  read_data(sys.argv[1])

if __name__ == '__main__':
  main()
