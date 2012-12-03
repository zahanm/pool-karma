
import random
import sys
import re
import itertools
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

# generate random locations for people and goal state
def gen(args):
    numPeople = int(args[1])
    numCars = int(args[2])
    width = float(args[3])
    height = float(args[4])

    #G=nx.Graph()
    nodes = []
    carNodes = random.sample(range(numPeople), numCars)
    filename = "data/generated_{}_{}_{}_{}.txt".format(numPeople, numCars, width, height)
    with open(filename, "w") as out:

        out.write("{}\n".format( numPeople + 1 ))
        for i in xrange(numPeople + 1):
            x = random.uniform(0, width)
            y = random.uniform(0, height)

            l = x, y
            nodes.append(l)
            #G.add_nodes(i)

            if i == numPeople:
                out.write ("{} {}\n".format(x, y))
                break
            if (i in carNodes):
                out.write ("{} {} {}\n".format(x, y, 4))
            else:
                out.write ("{} {} {}\n".format(x, y, 0))

        for i in range(len(nodes)):
            for j in range(len(nodes)):
                if i < j:
                    dist_i_j = dist(nodes[i], nodes[j])
                    #G.add_edge(i, j, weight=dist_i_j)
                    out.write("{} {} {}\n".format(i, j, dist_i_j))
    print "Written to: {}".format(filename)

def graph(fname):
  with open(fname) as f:
    num_locations = int(f.next().strip())
    xs = np.empty(num_locations, dtype=float)
    ys = np.empty(num_locations, dtype=float)
    cats = np.empty(num_locations, dtype='uint8')
    no_cars_xs, no_cars_ys, cars_xs, cars_ys = [], [], [], []
    for loc in xrange(num_locations - 1):
      # people locations
      line = f.next().rstrip()
      m = re.search(r"(\d+(\.\d+)?)\s+(\d+(\.\d+)?)\s+(\d+)", line)
      xs[loc] = float(m.group(1))
      ys[loc] = float(m.group(3))
      cats[loc] = 1 if int(m.group(5)) > 0 else 2
    # goal
    line = f.next().rstrip()
    m = re.search(r"(\d+(\.\d+)?)\s+(\d+(\.\d+)?)", line)
    loc = num_locations - 1
    xs[loc] = float(m.group(1))
    ys[loc] = float(m.group(3))
    cats[loc] = 3
    print "Plotting: {}".format([-0.5, np.max(xs) + 0.5, -0.5, np.max(ys) + 0.5])
    plt.axis([-0.5, np.max(xs) + 0.5, -0.5, np.max(ys) + 0.5])
    for i, (x, y) in enumerate(itertools.izip(xs, ys)):
      if cats[i] == 1:
        color = "blue"
      elif cats[i] == 2:
        color = "red"
      else:
        color = "green"
      plt.text(x, y, str(i), color=color)
    # plt.plot(xs[ cats == 1 ], ys[ cats == 1 ], "bo")
    # plt.plot(xs[ cats == 2 ], ys[ cats == 2 ], "ro")
    # plt.plot(xs[ cats == 3 ], ys[ cats == 3 ], "yo")
    plt.show()

def dist(a,b):
    dist = ((a[0]-b[0])**2 + (a[1]-b[1])**2)**0.5
    return dist

if __name__ == '__main__':
  if len(sys.argv) == 6:
    gen(sys.argv[1:])
  elif len(sys.argv) == 3:
    graph(sys.argv[2])
  else:
    print "usage {} <gen|graph>".format(__file__)
    print "usage gen: {} gen <numPeople> <numCars> <worldWidth> <worldHeight>".format(__file__)
    print "usage gen: {} graph <filename>".format(__file__)
    sys.exit(1)
