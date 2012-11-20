
import networkx as nx

class Mapping:
  """
  Stores the weights from the problem in a distances matrix
  """

  def __init__(self):
    self.G = nx.Graph()

  def add_distance(self, origin, dest, dist):
    """
    Connects 'origin' to 'dest' over distance 'dist'
    """
    self.G.add_edge(origin, dest, weight=dist)

  def is_connected(self, origin, dest):
    """
    Checks if 'origin' is connected to 'dest'
    """
    return self.G.has_edge(origin, dest)

  def get_distance(self, origin, dest):
    """
    Get distance
    """
    return self.G[origin][dest]
