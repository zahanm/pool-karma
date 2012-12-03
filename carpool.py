
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
  <goal location x-cood> <goal location y-cood>
  <edge1 origin id> <edge1 dest id> <edge1 weight>
  <edge2 origin id> <edge2 dest id> <edge2 weight>
  ...

  note that person-id is the same as location-id
  goal state is (number of locations - 1)
  """
  with open(fname) as f:
    ex = Explorer()
    # num locations
    ex.num_locations = int(f.next().strip())
    ex.num_people = ex.num_locations - 1
    ex.locations = [ None ] * ex.num_locations
    ex.people_capacity = [ None ] * ex.num_people
    ex.pickup_costs = [ {} ] * ex.num_people
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

def baseline(ex):
  """
  @param ex: Explorer
  """
  min_cost = float("inf")
  min_assignment = None
  for passenger_assignment in ex.iter_passenger_assignments():
    total_cost = 0.0
    for driver in filter(lambda p: ex.people_capacity[p] > 0, range(ex.num_people)):
      if passenger_assignment[driver] == None:
        continue
      if total_cost >= min_cost:
        break
      total_cost += ex.pickup_cost(driver, passenger_assignment[driver])
    if total_cost < min_cost:
      min_cost = total_cost
      min_assignment = passenger_assignment
  return (min_cost, min_assignment)

algorithms = {
  "baseline": baseline
}

def main():
  assert len(sys.argv) == 2
  ex = read_data(sys.argv[1])
  print "---* dataset *---"
  print ex
  print "Drivers: {}".format(filter(lambda p: ex.people_capacity[p] > 0, range(ex.num_people)))
  method = "baseline"
  min_cost, assignment = algorithms[method](ex)
  print "---* {} results *---".format(method)
  print "Minimum cost: {:.4}".format(min_cost)
  print 'Minimum assignment: '
  for i in range(len(assignment)):
    # is a driver
    if (assignment[i] != None):
      print "{} drives {}".format(i, [i] + assignment[i])
  print "Edge weights:"
  print "\t",
  print "\t".join([ str(item) for item in ex.distances.nodes() ])
  for origin in ex.distances.nodes():
    print "{}\t".format(origin),
    for dest in ex.distances.nodes():
      if ex.distances.has_edge(origin, dest):
        print "{:.3}\t".format(ex.distances[origin][dest]["weight"]),
      else:
        print "0.0\t",
    print

if __name__ == '__main__':
  main()
