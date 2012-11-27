
import networkx as nx

def main():
  locations = nx.Graph()
  locations.add_edge(1, 2, weight=1)
  locations.add_edge(3, 2, weight=1)
  print "is connected? {}".format(locations.has_edge(1, 2))
  print "dist: {}".format(locations[3][2])

if __name__ == '__main__':
  main()
