
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
    return ex

def baseline(ex):
  """
  @param ex: Explorer
  """
  min_cost = float("inf")
  min_assignment = None
  for passenger_assignment in ex.iter_passenger_assignments():
    total_cost = 0.0
    for driver in filter(lambda p: return ex.people_capacity[p] > 0, range(ex.num_people)):
      if passenger_assignment[driver] == None:
        continue
      if total_cost >= min_cost:
        break
      total_cost += ex.pickup_cost(driver, passenger_assignment[driver])
    list_driver_cost = [(driver, ex.pickup_cost(driver, passenger_assignment[driver])) for driver in range(len(passenger_assignment)) if passenger_assignment[driver] != None]
    if total_cost < min_cost):
      min_cost = total_cost
      min_assignment = passenger_assignment

  print '---* baseline results *---'
  print 'Minimum cost: ' + str(min_cost)
  print 'Assignment: '
  for i in range(len(min_assignment)):
    # is a driver
    if (min_assignment[i] != None):
      print str(i) + ' drives ' + str(list(min_assignment[i]))

def main():
  assert len(sys.argv) == 2
  read_data(sys.argv[1])

if __name__ == '__main__':
  main()
