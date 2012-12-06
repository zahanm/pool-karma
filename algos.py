
import numpy as np

import heuristics
from search import exhaustive, UCS

#
# search algorithms
# ----------
#

def baseline(ex):
  """
  Exhaustive search over the goal states
  @param ex: Explorer
  """
  return exhaustive(ex, ex.iter_passenger_assignments(), heuristics.pickup_all_cost)

def search(ex):
  """
  Use state space model outlined in paper
  returns (min_cost, min_assignment)
  """
  searcher = UCS(ex.add_waypoints, ex.routes_completed)
  min_cost, state = searcher(ex.starting_routes())
  assignment = [ None ] * ex.num_people
  i = 0
  for person in xrange(ex.num_people):
    if ex.people_capacity[person] > 0:
      assignment[person] = list(state[i])
      i += 1
  return min_cost, assignment

#
# custom solutions
# ----------
#

def agglomerative(ex):
  """
  @param ex: Explorer
  """
  row_names = []
  col_names = []

  people_with_cars = [i for i,x in enumerate(ex.people_capacity) if x>0]
  people_without_cars = [i for i,x in enumerate(ex.people_capacity) if x==0]
  # initiate matrix with non-car people on rows and car people on columns
  first_i = -1
  distance_array = []
  assignments_dict = {}
  # initialize dictionary of assignments_dict
  #car_centroids = {}
  for car_person in people_with_cars:
    assignments_dict[car_person] = []
    #car_centroids[car_person] = ex.locations[car_person]
  #initialize matrix of distances between non-car people to car people
  for i in people_with_cars:
    person_dist = []
    row_names.append(i)
    if first_i == -1:
        first_i=i
    for j in people_without_cars:
      if (i==first_i):
        col_names.append(j)
      person_dist.append(ex.distances[i][j]['weight'])
    distance_array.append(person_dist)
  distance_matrix = np.matrix(distance_array)
  if ex.verbose:
    print "distance_matrix"
    print distance_matrix


  # while there is an unassigned non-car person, assign the person with minimum distance to a car with space. Then recenter the location of that car.
  while len(col_names) > 0:
    min_row = np.unravel_index(np.argmin(distance_matrix), np.shape(distance_matrix))[0]
    min_col = np.unravel_index(np.argmin(distance_matrix), np.shape(distance_matrix))[1]
    min_car = row_names[min_row]
    assignments_dict[min_car].append(col_names[min_col])
    distance_matrix = np.delete(distance_matrix, min_col,1)
    del col_names[min_col]
    if len(assignments_dict[min_car]) >= (ex.people_capacity[min_car] - 1):
      distance_matrix = np.delete(distance_matrix, min_row,0)
      del row_names[min_row]
    #change the location of the car to be centroid of all people assigned to it and recompute distances for that row
    else:
      centroid_x, centroid_y = ex.locations[min_car]
      for person in assignments_dict[min_car]:
        centroid_x += ex.locations[person][0]
        centroid_y += ex.locations[person][1]
      centroid_x = centroid_x/(len(assignments_dict[min_car])+1)
      centroid_y = centroid_y/(len(assignments_dict[min_car])+1)
      new_row_dist=[]
      for person in col_names:
        new_row_dist.append(((ex.locations[person][0]-centroid_x)**2+(ex.locations[person][1]-centroid_y)**2)**0.5)
      distance_matrix[min_row] = new_row_dist
  total_cost = 0.0
  assignment = [ None ] * ex.num_people
  for driver in filter(lambda p: ex.people_capacity[p] > 0, range(ex.num_people)):
    if assignments_dict[driver] == []:
      assignment[driver] = []
    total_cost += heuristics.pickup_cost(ex, driver, assignments_dict[driver])[0]
    assignment[driver] = heuristics.pickup_cost(ex, driver, assignments_dict[driver])[1]
  return (total_cost, assignment)


def projectionDistance(ex):
  """
  @param ex: Explorer
  Algorithm based on projection distance
  """
  ### pick up passengers on the way ###
  # create matrix (passenger x driver)
  projection_matrix = heuristics.get_passenger_driver_projection_matrix(ex, range(ex.num_people))
  index_matrix = heuristics.get_passenger_driver_index_matrix(ex, range(ex.num_people))

  if ex.verbose:
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

    if ex.verbose:
      print projection_matrix
      print 'min: %s at (%s, %s)' % (str(np.nanmin(projection_matrix)), str(min_index_0), str(min_index_1))

    # assign min passenger to min car
    list_min_car_passengers = assignment[min_car_idx]
    if (list_min_car_passengers == None):
      list_min_car_passengers = []
    list_min_car_passengers.append(min_passenger_idx)
    if len(list_min_car_passengers) <= ex.people_capacity[min_car_idx] - 1:
      assignment[min_car_idx] = list_min_car_passengers
      if ex.verbose: print 'assign passenger %s to driver %s' % (str(min_passenger_idx), str(min_car_idx))

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
    distance_matrix = heuristics.get_passenger_driver_distance_matrix(ex, list_people)
    index_matrix = heuristics.get_passenger_driver_index_matrix(ex, list_people)

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

  if ex.verbose:
    print 'assignment:'
    print assignment

  # calculate cost
  total_cost = 0.0
  for driver in filter(lambda p: ex.people_capacity[p] > 0, range(ex.num_people)):
    if assignment[driver] == None:
      assignment[driver] = []
    total_cost += heuristics.pickup_cost(ex, driver, assignment[driver])[0]
    assignment[driver] = heuristics.pickup_cost(ex, driver, assignment[driver])[1]

  return (total_cost, assignment)

def kNearestDistance(ex):
  """
  @param ex: Explorer
  Algorithm based on projection distance
  """
  ### pick up passengers on the way ###
  # create matrix (passenger x driver)
  #projection_matrix = heuristics.get_passenger_driver_projection_matrix_ver2(ex, range(ex.num_people))
  projection_matrix = heuristics.get_passenger_driver_distance_matrix(ex, range(ex.num_people))
  index_matrix = heuristics.get_passenger_driver_index_matrix(ex, range(ex.num_people))

  if ex.verbose:
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

    if ex.verbose:
      print projection_matrix
      print 'min: %s at (%s, %s)' % (str(np.nanmin(projection_matrix)), str(min_index_0), str(min_index_1))

    # assign min passenger to min car
    list_min_car_passengers = assignment[min_car_idx]
    if (list_min_car_passengers == None):
      list_min_car_passengers = []
    list_min_car_passengers.append(min_passenger_idx)
    if len(list_min_car_passengers) <= ex.people_capacity[min_car_idx] - 1:
      assignment[min_car_idx] = list_min_car_passengers
      if ex.verbose: print 'assign passenger %s to driver %s' % (str(min_passenger_idx), str(min_car_idx))

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
    distance_matrix = heuristics.get_passenger_driver_distance_matrix(ex, list_people)
    index_matrix = heuristics.get_passenger_driver_index_matrix(ex, list_people)

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

  if ex.verbose:
    print 'assignment:'
    print assignment

  # calculate cost
  total_cost = 0.0
  for driver in filter(lambda p: ex.people_capacity[p] > 0, range(ex.num_people)):
    if assignment[driver] == None:
      assignment[driver] = []
    total_cost += heuristics.pickup_cost(ex, driver, assignment[driver])[0]
    assignment[driver] = heuristics.pickup_cost(ex, driver, assignment[driver])[1]

  return (total_cost, assignment)

algorithms = {
  "baseline": baseline,
  "search": search,
  "projection": projectionDistance,
  "knearest": kNearestDistance,
  "agglomerative": agglomerative
}
