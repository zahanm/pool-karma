
from collections import defaultdict

class Mapping:
  """
  Stores the weights from the problem in a distances matrix
  """

  def __init__(self):
    self.distances = dict()

  def add_dist(self, origin, dest, dist):
    """
    Connects 'origin' to 'dest' over distance 'dist'
    """
    if origin < dest:
      self.distances[ (origin, dest) ] = dist
    else:
      self.distances[ (dest, origin) ] = dist

  def is_connected(self, loc1, loc2):
    """
    Checks if 'loc1' is conencted to 'loc2'
    """
    return (loc1, loc2) in self.distances or (loc2, loc1) in self.distances

  def get_dist(self, origin, dest):
    """
    Get distance
    """
    if origin > dest:
      route = (dest, origin)
    else:
      route = (origin, dest)
    if route in self.distances:
      return self.distances[ route ]
    else:
      return None
