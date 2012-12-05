
import random
import sys
import re
import itertools
import os
import os.path as path
from glob import glob
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

def uniform(out, numPeople, numCars, width, height):
  """
  Uniform generation
  """
  #G=nx.Graph()
  nodes = []
  carNodes = random.sample(range(numPeople), numCars)

  out.write("{}\n".format( numPeople + 1 ))
  for i in xrange(numPeople + 1):
    x = random.uniform(0, width)
    y = random.uniform(0, height)
    l = (x, y)
    nodes.append(l)
    #G.add_nodes(i)
    if i == numPeople:
      # goal location
      out.write ("{} {}\n".format(x, y))
      break
    # people locations
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

def clustered(out, numPeople, numCars, width, height):
  """
  Passengers clustered around each of the drivers
  """
  nodes = []
  drivers = [ None ] * numCars
  out.write("{}\n".format( numPeople + 1 ))
  # pick drivers locations uniformly
  for i in xrange(numCars):
    x = random.uniform(0, width)
    y = random.uniform(0, height)
    drivers[i] = (x,y)
    nodes.append( drivers[i] )
    out.write("{} {} {}\n".format(x, y, 4))
  # cluster other people around drivers
  stddev = 1.0
  for i in xrange(numPeople - numCars):
    center = random.choice(drivers)
    x = random.gauss(center[0], stddev)
    while x < 0 or x > 10:
      x = random.gauss(center[0], stddev)
    y = random.gauss(center[1], stddev)
    while y < 0 or y > 10:
      y = random.gauss(center[0], stddev)
    nodes.append( (x,y) )
    out.write("{} {} {}\n".format(x, y, 0))
  # goal
  x = random.uniform(0, width)
  y = random.uniform(0, height)
  nodes.append( (x, y) )
  out.write("{} {}\n".format(x, y))
  # edges
  for i, origin in enumerate(nodes):
    for j, dest in enumerate(nodes):
      if i < j:
        out.write("{} {} {}\n".format(i, j, dist(origin, dest)))

def dist(a,b):
  dist = ((a[0]-b[0])**2 + (a[1]-b[1])**2)**0.5
  return dist

algorithms = {
  "uniform": uniform,
  "clustered": clustered
}

# generate random locations for people and goal state
def gen(args):
  """
  Generate map using model, numPeople and numCars specified
  """
  model = args[1]
  numPeople = int(args[2])
  numCars = int(args[3])
  width = 10.0
  height = 10.0

  if model not in algorithms:
    print "{} is not a valid model".format(model)
    sys.exit(1)

  filename = "data/generated_{}_{}_{}.txt".format(model, numPeople, numCars)
  with open(filename, "w") as out:
    algorithms[model](out, numPeople, numCars, width, height)

  print "Written to: {}".format(filename)

colors = ["blue", "red", "green", "yellow", "black"]

def plot_locations(xs, ys, cats):
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
  plt.xlabel("x (distance)")
  plt.ylabel("y (distance)")

def graph(data_fname):
  with open(data_fname) as f:
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

    # are there any output files?
    cwd = path.dirname(path.abspath(__file__))
    output_folder = path.join(cwd, "output")
    generated_fname_glob = "*_" + path.basename(data_fname)
    data_gen_algorithm = path.basename(data_fname).split("_")[0]
    data_gen_algorithm = data_gen_algorithm[:1].upper() + data_gen_algorithm[1:]
    print generated_fname_glob
    # plot just the data
    plot_locations(xs, ys, cats)
    plt.title("Data: " + data_gen_algorithm)
    if sys.argv[1] == "show":
      plt.show()
    else:
      cwd = path.dirname(path.abspath(__file__))
      if not path.exists(path.join(cwd, 'plots')):
        os.mkdir(path.join(cwd, 'plots'))
      plt.savefig(path.join(cwd, 'plots', path.splitext(path.basename(data_fname))[0] + '.png'))
    # now plot for algorithms
    for output in glob(path.join(output_folder, generated_fname_glob)):
      print path.basename(output)
      solver_algorithm = path.basename(output).split("_")[0]
      solver_algorithm = solver_algorithm[:1].upper() + solver_algorithm[1:]
      # plot paths of drivers
      with open(output) as generated_output:
        plot_locations(xs, ys, cats)
        min_cost = float(generated_output.next())
        title = "Data: " + data_gen_algorithm
        title += " | Algorithm: " + solver_algorithm
        title += " | Total cost: {:.4}".format(min_cost)
        plt.title(title)
        for i, line in enumerate(generated_output):
          stops = line.rstrip()
          route = [ int(p.group()) for p in re.finditer(r"\d+", stops) ]
          route += [ goal ]
          plt.plot(xs[route], ys[route], color=colors[ i % len(colors) ])
        if sys.argv[1] == "show":
          plt.show()
        else:
          cwd = path.dirname(path.abspath(__file__))
          if not path.exists(path.join(cwd, 'plots')):
            os.mkdir(path.join(cwd, 'plots'))
          plt.savefig(path.join(cwd, 'plots', path.splitext(path.basename(output))[0] + '.png'))
        plt.clf()
    # old plotting code
    # plt.plot(xs[ cats == 1 ], ys[ cats == 1 ], "bo")
    # plt.plot(xs[ cats == 2 ], ys[ cats == 2 ], "ro")
    # plt.plot(xs[ cats == 3 ], ys[ cats == 3 ], "yo")

if __name__ == '__main__':
  if len(sys.argv) == 5:
    gen(sys.argv[1:])
  elif len(sys.argv) == 3:
    graph(sys.argv[2])
  else:
    print "usage {} <gen|graph>".format(__file__)
    print "usage: {} gen <model> <numPeople> <numCars>".format(__file__)
    print "usage: {} show <data file>".format(__file__)
    print "usage: {} graph <data file>".format(__file__)
    sys.exit(1)
