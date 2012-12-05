import itertools
import numpy as np
import math

class Explorer:
  """
  Stores the weights from the problem in a distances matrix
  """

  def __init__(self):
    self.num_locations = None
    self.num_edges = None
    self.distances = None
    self.num_people = None
    self.locations = None
    self.people_capacity = None
    self.pickup_costs = None
    self.goal = None

  def verify_initialized(self):
    """
    Verifies that the data is initialized and valid
    """
    assert self.num_locations != None
    assert self.num_edges != None
    assert self.distances != None
    assert self.num_people != None
    assert self.locations != None
    for loc in self.locations:
      assert loc != None
    assert self.people_capacity != None
    for cap in self.people_capacity:
      assert cap != None
    assert self.pickup_costs != None
    assert self.goal != None

  def __str__(self):
    """
    toString method
    """
    return "{} locations with {} edges and {} people".format(self.num_locations, self.num_edges, self.num_people)

  def iter_passengers(self, driver, n=3):
    """
    all possible passengers for given driver
    """
    other_people = range(driver) + range(driver + 1, self.num_people)
    for i in xrange(1, n + 1):
      for pass_group in itertools.combinations(other_people, i):
        yield pass_group

  def iter_passenger_assignments(self, maxn=4):
    """
    all possible passenger assignments, for all drivers
    @return iterable
    each iteration yields a list, num_people in length
    each element of the list is None if the person isn't driving, or a list of passengers
    that driver is taking with him / her
    """
    non_drivers = filter(lambda p: self.people_capacity[p] <= 0, range(self.num_people))
    drivers = filter(lambda p: self.people_capacity[p] > 0, range(self.num_people))
    driver_assignments = []
    for d in drivers:
      driver_assignments.extend( [d] * (self.people_capacity[d] - 1) )
    if len(driver_assignments) < len(non_drivers):
      raise RuntimeError("Not enough capacity to pickup and take everyone")
    for assignment in itertools.permutations(driver_assignments, r=len(non_drivers)):
      # partition
      p = [ None ] * self.num_people
      for i in xrange(len(non_drivers)):
        if p[assignment[i]] == None:
          p[assignment[i]] = []
        p[assignment[i]].append( non_drivers[i] )
      for d in drivers:
        if p[d] == None:
          p[d] = []
      yield p

  def pickup_cost(self, driver, passengers):
    """
    Calculate pickup costs
    """
    pass_key = tuple(sorted(passengers))
    if pass_key in self.pickup_costs[driver]:
      # memorization
      return self.pickup_costs[driver][pass_key]

    # calculate shortest path that passes all these nodes
    print "Driver: {}, Assignment: {} -- ".format(driver, passengers),

    # get all possible paths starting from driver to goal
    list_paths = []
    for permutation in itertools.permutations(passengers, len(passengers)):
      path = [ driver ] + list(permutation) + [ self.num_locations - 1 ]
      list_paths.append(path)

    # find minimum path
    min_path = None
    min_path_cost = float("inf")
    for path in list_paths:
      path_cost = 0.0
      for origin, dest in itertools.izip(path[:-1], path[1:]):
        if path_cost >= min_path_cost:
          break
        path_cost += self.distances[origin][dest]["weight"]
      if path_cost < min_path_cost:
        min_path_cost = path_cost
        min_path = path
    print "=> Cost: {:.4}".format(min_path_cost)

    self.pickup_costs[driver][pass_key] = (min_path_cost, min_path)
    return (min_path_cost, min_path)

  def get_passenger_driver_projection_matrix(self, list_people):
    """
    get numpy matrix of passenger x driver
    each (passenger, driver) value is projection of passenger to driver toward goal
    """
    passengers = filter(lambda p: self.people_capacity[p] <= 0, list_people)
    drivers = filter(lambda p: self.people_capacity[p] > 0, list_people)
    passenger_driver_matrix = []
    list_driver_vectors = [(self.locations[i][0] - self.goal[0], self.locations[i][1] - self.goal[1]) for i in drivers]
    
    # for each passenger, calculate a list of projection distance to each driver
    # as a row in passenger x driver matrix
    for i in range(len(passengers)):
      passenger_vector = (self.locations[passengers[i]][0] - self.goal[0], self.locations[passengers[i]][1] - self.goal[1])
      list_distances = [self.vertical_distance(passenger_vector, driver_vector) for driver_vector in list_driver_vectors]
      list_projections = [self.projection(passenger_vector, driver_vector) for driver_vector in list_driver_vectors]
      for j in range(len(list_driver_vectors)):
        if (list_projections[j] < 0 or list_projections[j] > self.length(list_driver_vectors[j]) or list_distances[j] < 0):
          list_distances[j] = np.nan
      passenger_driver_matrix.append(list_distances)
    
    return np.array(passenger_driver_matrix)      
    
  def get_passenger_driver_index_matrix(self, list_people):
    """
    get numpy matrix of passenger x driver *index*
    each (passenger, driver) value is (index_passenger, index_car)
    """  
    passengers = filter(lambda p: self.people_capacity[p] <= 0, list_people)
    drivers = filter(lambda p: self.people_capacity[p] > 0, list_people)
    index_matrix = []
    # for each passenger, make each cell (index_passenger, index_car) for lookup
    for i in range(len(passengers)):
      list_index_tuple = [(passengers[i], drivers[j]) for j in range(len(drivers))]
      index_matrix.append(list_index_tuple)
    
    return np.array(index_matrix)      

  def get_passenger_driver_distance_matrix(self, list_people):
    """
    get numpy matrix of passenger x driver
    each (passenger, driver) value is projection of passenger to driver toward goal
    """  
    passengers = filter(lambda p: self.people_capacity[p] <= 0, list_people)
    drivers = filter(lambda p: self.people_capacity[p] > 0, list_people)
    passenger_driver_matrix = []
    
    # for each passenger, calculate a list of projection distance to each driver
    # as a row in passenger x driver matrix
    for i in passengers:
      list_distances = [self.euclidean_distance(self.locations[i], self.locations[j]) for j in drivers]
      passenger_driver_matrix.append(list_distances)
    
    return np.array(passenger_driver_matrix)
  
  def euclidean_distance(self, p1, p2):
    """
    Euclidean distance between two points
    """
    return math.sqrt(sum(math.pow((a - b), 2) for a, b in zip(p1, p2)))
      
  def projection(self, v1, v2):
    """
    projection of v1 onto v2
    """
    return float(self.length(v1) * math.cos(self.angle(v1, v2)))
    
  def vertical_distance(self, v1, v2):
    """
    vertical distance from v1 onto v2
    """
    return float(self.length(v1) * math.sin(self.angle(v1, v2)))
    
  def dotproduct(self, v1, v2):
    return sum((a*b) for a, b in zip(v1, v2))

  def length(self, v):
    return math.sqrt(self.dotproduct(v, v))

  def angle(self, v1, v2):
    return math.acos(self.dotproduct(v1, v2) / (self.length(v1) * self.length(v2)))
