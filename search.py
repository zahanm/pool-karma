import itertools

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
