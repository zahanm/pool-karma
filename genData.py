
import random
import sys
import re
import networkx as nx
import matplotlib.pyplot as plt

# generate random locations for people and goal state
def gen(args):
    # numPeople = 5
    # numCars = 2
    # width = 10
    # height = 10
    numPeople = int(args[1])
    numCars = int(args[2])
    width = float(args[3])
    height = float(args[4])

    #G=nx.Graph()
    nodes = []
    carNodes = random.sample(range(numPeople), numCars)
    filename = "data/generated_"+sys.argv[1]+"_"+sys.argv[2]+"_"+sys.argv[3]+"_"+sys.argv[4]+".txt"
    with open(filename, "w") as out:
        out.write("{}\n".format(numPeople+1))
        for i in range(numPeople+1):
            x = random.randint(0, width)
            y = random.randint(0, height)

            l = x, y
            nodes.append(l)
            #G.add_nodes(i)

            if i==numPeople:
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
    no_cars_xs, no_cars_ys, cars_xs, cars_ys = [], [], [], []
    for loc in xrange(num_locations - 1):
      # people locations
      line = f.next().rstrip()
      m = re.search(r"(\d+(\.\d+)?)\s+(\d+(\.\d+)?)\s+(\d+)", line)
      if int(m.group(5)) > 0:
        cars_xs.append(float(m.group(1)))
        cars_ys.append(float(m.group(3)))
      else:
        no_cars_xs.append(float(m.group(1)))
        no_cars_ys.append(float(m.group(3)))
    # goal
    line = f.next().rstrip()
    m = re.search(r"(\d+(\.\d+)?)\s+(\d+(\.\d+)?)", line)
    goal = (float(m.group(1)), float(m.group(3)))
    plt.plot(no_cars_xs, no_cars_ys, "bo")
    plt.plot(cars_xs, cars_ys, "ro")
    plt.plot([ goal[0] ], [ goal[1] ], "go")
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
