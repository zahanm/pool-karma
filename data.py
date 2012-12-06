
import itertools

class Explorer:
  """
  Stores the weights from the problem in a distances matrix
  """

  def __init__(self, verbose = False):
    self.num_locations = None
    self.num_edges = None
    self.distances = None
    self.num_people = None
    self.locations = None
    self.people_capacity = None
    self.pickup_costs = None
    self.goal = None
    self.verbose = verbose

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

  def starting_routes(self):
    routes = []
    for person in xrange(self.num_people):
      if self.people_capacity[person] > 0:
        # is driver, starts out at own location
        routes.append( (person, ) )
    return tuple(routes)

  def add_waypoints(self, routes):
    """
    All possible modifications to a routes 'state'
    yields ( modified routes, distance for modification )
    @param routes list of tuples
    """
    for i, route in enumerate(routes):
      if route[-1] == (self.num_locations - 1):
        continue
      if self.verbose: print "Adding to route {}".format(i)
      for dest in xrange(self.num_locations):
        if dest in route:
          continue
        origin = route[-1]
        modified = routes[:i] + ( route + (dest, ), ) + routes[i+1:]
        yield (modified, self.distances[origin][dest]["weight"])

  def routes_completed(self, routes):
    # everyone ends up at goal
    num_transported = -len(routes)
    for route in routes:
      if route[-1] != (self.num_locations - 1):
        # not at goal
        return False
      num_transported += len(route)
    return num_transported == self.num_people
