
from mapping import Locations

def main():
  locationmap = Locations()
  locationmap.add_distance(1, 2, 1)
  locationmap.add_distance(3, 2, 1)
  print "is connected? " + locationmap.is_connected(1, 2)
  print "dist: " + locationmap.get_distance(3, 2)

if __name__ == '__main__':
  main()
