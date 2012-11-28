
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

  def verify_initialized(self):
    """
    Verifies that the data is initialized and valid
    """
    assert self.num_locations != None
    assert self.num_edges != None
    assert self.distances != None
    assert self.num_people != None
    assert self.people_locations != None
    for loc in self.people_locations:
      assert loc != None
    assert self.people_capacity != None
    for cap in self.people_capacity:
      assert cap != None

  def __str__(self):
    """
    To string
    """
    return "{} locations with {} edges and {} people".format(self.num_locations, self.num_edges, self.num_people)
