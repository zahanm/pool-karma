
import random
import sys
import re
import itertools
import os
import os.path as path
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
    filename = "data/generated_{}_{}_{}_{}.txt".format(numPeople, numCars, int(width), int(height))
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

def graph(data_fname):
  colors = ["blue", "red", "green", "yellow", "black"]
  with open(data_fname) as f:
    cwd = path.dirname(path.abspath(__file__))
    output_fname = path.join(cwd, "output", path.basename(data_fname))
    with open(output_fname) as gen_output:
      num_locations = int(f.next().strip())
      xs = np.empty(num_locations, dtype=float)
      ys = np.empty(num_locations, dtype=float)
      cats = np.empty(num_locations, dtype='uint8')
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
      goal = num_locations - 1
      xs[goal] = float(m.group(1))
      ys[goal] = float(m.group(3))
      cats[goal] = 3
      print "Plotting: {}".format([-0.5, np.max(xs) + 0.5, -0.5, np.max(ys) + 0.5])
      plt.axis([-0.5, np.max(xs) + 0.5, -0.5, np.max(ys) + 0.5])
      for i, (x, y) in enumerate(itertools.izip(xs, ys)):
        if cats[i] == 1:
          color = colors[0]
        elif cats[i] == 2:
          color = colors[1]
        else:
          color = colors[2]
        plt.text(x, y, str(i), color=color)
      # plot paths of drivers
      for i, line in enumerate(gen_output):
        driver, passengers = line.split(":")
        driver = int(driver)
        passengers = [ int(p.group()) for p in re.finditer(r"\d+", passengers) ]
        route = [ driver ] + passengers + [ goal ]
        plt.plot(xs[route], ys[route], color=colors[ i % len(colors) ])
      # old plotting code
      # plt.plot(xs[ cats == 1 ], ys[ cats == 1 ], "bo")
      # plt.plot(xs[ cats == 2 ], ys[ cats == 2 ], "ro")
      # plt.plot(xs[ cats == 3 ], ys[ cats == 3 ], "yo")
      if sys.argv[1] == "show":
        plt.show()
      else:
        cwd = path.dirname(path.abspath(__file__))
        if not path.exists(path.join(cwd, 'plots')):
          os.mkdir(path.join(cwd, 'plots'))
        plt.savefig(path.join(cwd, 'plots', path.splitext(path.basename(data_fname))[0] + '.png'))

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
    print "usage: {} gen <numPeople> <numCars> <worldWidth> <worldHeight>".format(__file__)
    print "usage: {} show <data file> <generated output>".format(__file__)
    print "usage: {} graph <data file> <generated output>".format(__file__)
    sys.exit(1)
