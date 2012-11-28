
class Explorer:
  """
  Stores the weights from the problem in a distances matrix
  """

  def __init__(self):
    self.num_locations = None
    self.num_edges = None
    self.distances = None
    self.num_people = None
    self.people_locations = None
    self.people_capacity = None
    self.pickup_costs = None

  def verify_initialized(self):
    """
    Verifies that the data is initialized and valid
    """
    assert self.num_locations != None
    assert self.num_edges != None
    assert self.distances != None
    assert self.num_people != None
    for loc in self.people_locations:
      assert loc != None
    assert self.people_capacity != None
    for cap in self.people_capacity:
      assert cap != None
    assert self.pickup_costs != None

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

  def pickup_cost(self, driver, passengers):
    """
    TODO
    Calculate pickup costs
    """
    pass_key = tuple(sorted(passengers))
    if pass_key in self.pickup_costs[driver]:
      # memorization
      return self.pickup_costs[driver][pass_key]
    # calculate shortest path that passes all these nodes
    goal = self.num_locations - 1
    cost = 1.0
    self.pickup_costs[driver][pass_key] = cost
    
    # get all possible paths starting from driver to goal
    list_paths = [[driver, passenger_1, passenger_2, passenger_3, goal] \
    for passenger_1 in passengers for passenger_2 in passengers for passenger_3 in passengers \
    if passenger_1 != passenger_2 and passenger_1 != passenger_3 and passenger_2 != passenger_3]
    
    # find minimum path
    min_path = None
    min_path_cost = None
    for path in list_paths:
      path_cost = sum([self.distances[path[i]][path[i+1]] for i in range(len(path) - 1)])
      if min_path_cost == None:
        min_path_cost = path_cost
      elif path_cost < min_path_cost:
        min_path_cost = path_cost
        min_path = path
        
    return min_path_cost
