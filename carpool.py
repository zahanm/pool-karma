
import re
import sys
import numpy as np
import os
import os.path as path

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
      cost, passenger_assignment[driver] = ex.pickup_cost(driver, passenger_assignment[driver])
      total_cost += cost
    if total_cost < min_cost:
      min_cost = total_cost
      min_assignment = passenger_assignment
  return (min_cost, min_assignment)

def agglomerative(ex):
  """
  @param ex: Explorer
  """
  row_names = []
  col_names = []

  people_with_cars = [i for i,x in enumerate(ex.capacity) if x>0]
  people_without_cars = [i for i,x in enumerate(ex.capacity) if x==0]
  # initiate matrix with non-car people on rows and car people on columns
  first_i = -1
  distance_matrix = np.matrix()
  assignments = {}
  # initialize dictionary of assignments
  for car_person in people_with_cars:
    assignments[car_person] = []
  
  #initialize matrix of distances between non-car people to car people
  for i in people_with_cars:
    person_dist = []
    row_names.append(i)
    if first_i == -1:
        first_i=i
    for j in people_without_cars:
      if (i==first_i):
        col_names.append(j)
      person_dist.append(ex.distances[i][j])
    np.append(distance_matrix,person_dist, axis=0)
  
  # while there is an unassigned non-car person, assign the person with minimum distance to a car with space. Then recenter the location of that car.
  while col_names.len > 0:
    min_row = np.unravel_index(np.argmin(distance_matrix), np.shape(distance_matrix))[0]
    min_col = np.unravel_index(np.argmin(distance_matrix), np.shape(distance_matrix))[1]

    assignments[row_names(min_row)].append(col_names(min_col))
    np.delete(distance_matrix, min_col,1)
    min_col.remove[col_names(min_col)]
    if assignments[row_names(min_row)].len >= (ex.capacity[row_names(min_row)] - 1):
      np.delete(distance_matrix, min_row,0)
      min_row.remove[row_names(min_row)]

  return (cost, assigment)

def projectionDistanceBased(ex):
  """
  @param ex: Explorer
  Algorithm based on projection distance
  """
  ### pick up passengers on the way ###
  # create matrix (passenger x driver)
  projection_matrix = ex.get_passenger_driver_projection_matrix(range(ex.num_people))
  index_matrix = ex.get_passenger_driver_index_matrix(range(ex.num_people))
  
  print projection_matrix
  print index_matrix
  
  # for each global minimum projection, assign passenger to the car
  # remove passenger row
  # once the car is filled, remove car column
  assignment = [ None ] * ex.num_people
  while np.size(projection_matrix) > 0 and not np.isnan(np.nanmin(projection_matrix)):

    (num_unassign_passengers, num_avail_cars) = projection_matrix.shape
    min_index = np.nanargmin(projection_matrix)
    min_index_0 = min_index / num_avail_cars
    min_index_1 = min_index % num_avail_cars
    (min_passenger_idx, min_car_idx) = index_matrix[min_index_0][min_index_1]

    print projection_matrix
    print 'min: %s at (%s, %s)' % (str(np.nanmin(projection_matrix)), str(min_index_0), str(min_index_1))

    # assign min passenger to min car
    list_min_car_passengers = assignment[min_car_idx]
    if (list_min_car_passengers == None):
      list_min_car_passengers = []
    list_min_car_passengers.append(min_passenger_idx)
    if len(list_min_car_passengers) <= ex.people_capacity[min_car_idx] - 1:
      assignment[min_car_idx] = list_min_car_passengers
      print 'assign passenger %s to driver %s' % (str(min_passenger_idx), str(min_car_idx))

    # remove car column if car is full after taking this passenger
    if (len(list_min_car_passengers) == ex.people_capacity[min_car_idx] - 1):
      projection_matrix = np.delete(projection_matrix, min_index_1, axis=1)
      index_matrix = np.delete(index_matrix, min_index_1, axis=1)

    # remove passenger
    projection_matrix = np.delete(projection_matrix, min_index_0, axis=0)
    index_matrix = np.delete(index_matrix, min_index_0, axis=0)

  ### for remaining passengers, assign to closest driver ###
  if np.size(projection_matrix) > 0:

    # get a list of people indices
    list_index_matrix = index_matrix.tolist()
    list_index_cars = [tuple[1] for tuple in list_index_matrix[0]]
    list_index_passengers = []
    for list_index in list_index_matrix:
      list_index_passengers.append(list_index[0][0])
    list_people = list_index_cars + list_index_passengers

    # get distance and index matrices
    distance_matrix = ex.get_passenger_driver_distance_matrix(list_people)
    index_matrix = ex.get_passenger_driver_index_matrix(list_people)

    # for each global minimum distance, assign passenger to car
    while np.size(distance_matrix) > 0 and not np.isnan(np.nanmin(distance_matrix)):

      (num_unassign_passengers, num_avail_cars) = distance_matrix.shape
      min_index = np.nanargmin(distance_matrix)
      min_index_0 = min_index / num_avail_cars
      min_index_1 = min_index % num_avail_cars
      (min_passenger_idx, min_car_idx) = index_matrix[min_index_0][min_index_1]

      # assign min passenger to min car
      list_min_car_passengers = assignment[min_car_idx]
      if (list_min_car_passengers == None):
        list_min_car_passengers = []
      list_min_car_passengers.append(min_passenger_idx)
      if len(list_min_car_passengers) <= ex.people_capacity[min_car_idx] - 1:
        assignment[min_car_idx] = list_min_car_passengers

      # remove car column if car is full after taking this passenger
      if (len(list_min_car_passengers) == ex.people_capacity[min_car_idx] - 1):
        distance_matrix = np.delete(distance_matrix, min_index_1, axis=1)
        index_matrix = np.delete(index_matrix, min_index_1, axis=1)

      # remove passenger
      distance_matrix = np.delete(distance_matrix, min_index_0, axis=0)
      index_matrix = np.delete(index_matrix, min_index_0, axis=0)

  print 'assignment:'
  print assignment

  # calculate cost
  total_cost = 0.0
  for driver in filter(lambda p: ex.people_capacity[p] > 0, range(ex.num_people)):
    if assignment[driver] == None:
      assignment[driver] = []
    total_cost += ex.pickup_cost(driver, assignment[driver])[0]
    assignment[driver] = ex.pickup_cost(driver, assignment[driver])[1]
    
  return (total_cost, assignment)
  
def projectionDistanceBasedVer2(ex):
  """
  @param ex: Explorer
  Algorithm based on projection distance
  """
  ### pick up passengers on the way ###
  # create matrix (passenger x driver)
  #projection_matrix = ex.get_passenger_driver_projection_matrix_ver2(range(ex.num_people))
  projection_matrix = ex.get_passenger_driver_distance_matrix(range(ex.num_people))
  index_matrix = ex.get_passenger_driver_index_matrix(range(ex.num_people))
  
  print projection_matrix
  print index_matrix
  
  # for each global minimum projection, assign passenger to the car
  # remove passenger row
  # once the car is filled, remove car column
  assignment = [ None ] * ex.num_people
  while np.size(projection_matrix) > 0 and not np.isnan(np.nanmin(projection_matrix)):

    (num_unassign_passengers, num_avail_cars) = projection_matrix.shape
    min_index = np.nanargmin(projection_matrix)
    min_index_0 = min_index / num_avail_cars
    min_index_1 = min_index % num_avail_cars
    (min_passenger_idx, min_car_idx) = index_matrix[min_index_0][min_index_1]

    print projection_matrix
    print 'min: %s at (%s, %s)' % (str(np.nanmin(projection_matrix)), str(min_index_0), str(min_index_1))

    # assign min passenger to min car
    list_min_car_passengers = assignment[min_car_idx]
    if (list_min_car_passengers == None):
      list_min_car_passengers = []
    list_min_car_passengers.append(min_passenger_idx)
    if len(list_min_car_passengers) <= ex.people_capacity[min_car_idx] - 1:
      assignment[min_car_idx] = list_min_car_passengers
      print 'assign passenger %s to driver %s' % (str(min_passenger_idx), str(min_car_idx))

    # remove car column if car is full after taking this passenger
    if (len(list_min_car_passengers) == ex.people_capacity[min_car_idx] - 1):
      projection_matrix = np.delete(projection_matrix, min_index_1, axis=1)
      index_matrix = np.delete(index_matrix, min_index_1, axis=1)

    # remove passenger
    projection_matrix = np.delete(projection_matrix, min_index_0, axis=0)
    index_matrix = np.delete(index_matrix, min_index_0, axis=0)

  ### for remaining passengers, assign to closest driver ###
  if np.size(projection_matrix) > 0:

    # get a list of people indices
    list_index_matrix = index_matrix.tolist()
    list_index_cars = [tuple[1] for tuple in list_index_matrix[0]]
    list_index_passengers = []
    for list_index in list_index_matrix:
      list_index_passengers.append(list_index[0][0])
    list_people = list_index_cars + list_index_passengers

    # get distance and index matrices
    distance_matrix = ex.get_passenger_driver_distance_matrix(list_people)
    index_matrix = ex.get_passenger_driver_index_matrix(list_people)

    # for each global minimum distance, assign passenger to car
    while np.size(distance_matrix) > 0 and not np.isnan(np.nanmin(distance_matrix)):

      (num_unassign_passengers, num_avail_cars) = distance_matrix.shape
      min_index = np.nanargmin(distance_matrix)
      min_index_0 = min_index / num_avail_cars
      min_index_1 = min_index % num_avail_cars
      (min_passenger_idx, min_car_idx) = index_matrix[min_index_0][min_index_1]

      # assign min passenger to min car
      list_min_car_passengers = assignment[min_car_idx]
      if (list_min_car_passengers == None):
        list_min_car_passengers = []
      list_min_car_passengers.append(min_passenger_idx)
      if len(list_min_car_passengers) <= ex.people_capacity[min_car_idx] - 1:
        assignment[min_car_idx] = list_min_car_passengers

      # remove car column if car is full after taking this passenger
      if (len(list_min_car_passengers) == ex.people_capacity[min_car_idx] - 1):
        distance_matrix = np.delete(distance_matrix, min_index_1, axis=1)
        index_matrix = np.delete(index_matrix, min_index_1, axis=1)

      # remove passenger
      distance_matrix = np.delete(distance_matrix, min_index_0, axis=0)
      index_matrix = np.delete(index_matrix, min_index_0, axis=0)

  print 'assignment:'
  print assignment

  # calculate cost
  total_cost = 0.0
  for driver in filter(lambda p: ex.people_capacity[p] > 0, range(ex.num_people)):
    if assignment[driver] == None:
      assignment[driver] = []
    total_cost += ex.pickup_cost(driver, assignment[driver])[0]
    assignment[driver] = ex.pickup_cost(driver, assignment[driver])[1]
    
  return (total_cost, assignment)

def output_results(ex, inp_fname, method, min_cost, assignment):
  print "---* {} results *---".format(method)
  cwd = path.dirname(path.abspath(__file__))
  output_folder = path.join(cwd, "output")
  if not path.exists(output_folder):
    os.mkdir(output_folder)
  output_fname = method + "_" + path.basename(inp_fname)
  with open(path.join(output_folder, output_fname), "w") as out:
    print "Minimum cost: {:.4}".format(min_cost)
    out.write(str(min_cost) + "\n")
    print 'Minimum assignment: '
    for i in range(len(assignment)):
      # is a driver
      if (assignment[i] != None):
        print "{} drives {}".format(i, assignment[i])
        out.write(str(assignment[i]) + "\n")
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

algorithms = {
  "baseline": baseline,
  "projection": projectionDistanceBased,
  "projection2": projectionDistanceBasedVer2,
  "agglomerative": agglomerative
}

def main():
  if len(sys.argv) != 3:
    print "usage: {} <method> <input filename>".format(__file__)
    sys.exit(1)
  inp_fname = sys.argv[2]
  ex = read_data(inp_fname)
  print "---* dataset *---"
  print ex
  print "Drivers: {}".format(filter(lambda p: ex.people_capacity[p] > 0, range(ex.num_people)))
  method = sys.argv[1]
  if method not in algorithms:
    print "Invalid method specified: {}".format(method)
    sys.exit(1)
  min_cost, assignment = algorithms[method](ex)
  output_results(ex, inp_fname, method, min_cost, assignment)

if __name__ == '__main__':
  main()
