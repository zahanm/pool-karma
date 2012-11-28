
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
      # memoization
      return self.pickup_costs[driver][pass_key]
    # calculate
    cost = 1.0
    self.pickup_costs[driver][pass_key] = cost
