
import itertools
import numpy as np
import math

def pickup_cost(ex, driver, passengers):
  """
  Calculate pickup costs
  """
  pass_key = tuple(sorted(passengers))
  if pass_key in ex.pickup_costs[driver]:
    # memorization
    return ex.pickup_costs[driver][pass_key]

  # calculate shortest path that passes all these nodes
  if ex.verbose: print "Driver: {}, Assignment: {} -- ".format(driver, passengers),

  # get all possible paths starting from driver to goal
  list_paths = []
  for permutation in itertools.permutations(passengers, len(passengers)):
    path = [ driver ] + list(permutation) + [ ex.num_locations - 1 ]
    list_paths.append(path)

  # find minimum path
  min_path = None
  min_path_cost = float("inf")
  for path in list_paths:
    path_cost = 0.0
    for origin, dest in itertools.izip(path[:-1], path[1:]):
      if path_cost >= min_path_cost:
        break
      path_cost += ex.distances[origin][dest]["weight"]
    if path_cost < min_path_cost:
      min_path_cost = path_cost
      min_path = path
  if ex.verbose: print "=> Cost: {:.4}".format(min_path_cost)
  ex.pickup_costs[driver][pass_key] = (min_path_cost, min_path)
  return (min_path_cost, min_path)

def get_passenger_driver_projection_matrix(ex, list_people):
  """
  get numpy matrix of passenger x driver
  each (passenger, driver) value is projection of passenger to driver toward goal
  """
  passengers = filter(lambda p: ex.people_capacity[p] <= 0, list_people)
  drivers = filter(lambda p: ex.people_capacity[p] > 0, list_people)
  passenger_driver_matrix = []
  list_driver_vectors = [(ex.locations[i][0] - ex.goal[0], ex.locations[i][1] - ex.goal[1]) for i in drivers]

  # for each passenger, calculate a list of projection distance to each driver
  # as a row in passenger x driver matrix
  for i in range(len(passengers)):
    passenger_vector = (ex.locations[passengers[i]][0] - ex.goal[0], ex.locations[passengers[i]][1] - ex.goal[1])
    list_distances = [ vertical_distance(passenger_vector, driver_vector) for driver_vector in list_driver_vectors ]
    list_projections = [ projection(passenger_vector, driver_vector) for driver_vector in list_driver_vectors ]
    for j in range(len(list_driver_vectors)):
      if (list_projections[j] < 0 or list_projections[j] > vlength(list_driver_vectors[j]) or list_distances[j] < 0):
        list_distances[j] = np.nan
    passenger_driver_matrix.append(list_distances)
  return np.array(passenger_driver_matrix)

def get_passenger_driver_projection_matrix_ver2(ex, list_people):
  """
  get numpy matrix of passenger x driver
  each (passenger, driver) value is projection of passenger to driver toward goal
  """
  passengers = filter(lambda p: ex.people_capacity[p] <= 0, list_people)
  drivers = filter(lambda p: ex.people_capacity[p] > 0, list_people)
  passenger_driver_matrix = []
  list_driver_vectors = [(ex.locations[i][0] - ex.goal[0], ex.locations[i][1] - ex.goal[1]) for i in drivers]

  # for each passenger, calculate a list of projection distance to each driver
  # as a row in passenger x driver matrix
  for i in range(len(passengers)):
    passenger_vector = (ex.locations[passengers[i]][0] - ex.goal[0], ex.locations[passengers[i]][1] - ex.goal[1])
    list_distances = [ vertical_distance(passenger_vector, driver_vector) for driver_vector in list_driver_vectors ]
    list_projections = [projection(passenger_vector, driver_vector) for driver_vector in list_driver_vectors]
    for j in range(len(list_driver_vectors)):
      if (list_projections[j] < 0):
        list_distances[j] *= -1
    passenger_driver_matrix.append(list_distances)
  return np.array(passenger_driver_matrix)

def get_passenger_driver_index_matrix(ex, list_people):
  """
  get numpy matrix of passenger x driver *index*
  each (passenger, driver) value is (index_passenger, index_car)
  """
  passengers = filter(lambda p: ex.people_capacity[p] <= 0, list_people)
  drivers = filter(lambda p: ex.people_capacity[p] > 0, list_people)
  index_matrix = []
  # for each passenger, make each cell (index_passenger, index_car) for lookup
  for i in range(len(passengers)):
    list_index_tuple = [(passengers[i], drivers[j]) for j in range(len(drivers))]
    index_matrix.append(list_index_tuple)

  return np.array(index_matrix)

def get_passenger_driver_distance_matrix(ex, list_people):
  """
  get numpy matrix of passenger x driver
  each (passenger, driver) value is projection of passenger to driver toward goal
  """
  passengers = filter(lambda p: ex.people_capacity[p] <= 0, list_people)
  drivers = filter(lambda p: ex.people_capacity[p] > 0, list_people)
  passenger_driver_matrix = []

  # for each passenger, calculate a list of projection distance to each driver
  # as a row in passenger x driver matrix
  for i in passengers:
    list_distances = [ euclidean_distance(ex.locations[i], ex.locations[j]) for j in drivers ]
    passenger_driver_matrix.append(list_distances)

  return np.array(passenger_driver_matrix)

def euclidean_distance(p1, p2):
  """
  Euclidean distance between two points
  """
  return math.sqrt(sum(math.pow((a - b), 2) for a, b in zip(p1, p2)))

def projection(v1, v2):
  """
  projection of v1 onto v2
  """
  return float(vlength(v1) * math.cos(angle(v1, v2)))

def vertical_distance(v1, v2):
  """
  vertical distance from v1 onto v2
  """
  return float(vlength(v1) * math.sin(angle(v1, v2)))

def dotproduct(v1, v2):
  return sum((a*b) for a, b in zip(v1, v2))

def vlength(v):
  return math.sqrt(dotproduct(v, v))

def angle(v1, v2):
  return math.acos(dotproduct(v1, v2) / (vlength(v1) * vlength(v2)))
