
import random
import re
import itertools
import os
import os.path as path
from glob import glob
import argparse

import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

def uniform(numPeople, numCars, width, height):
  """
  Uniform generation
  """
  #G=nx.Graph()
  people = []
  carNodes = random.sample(range(numPeople), numCars)

  for i in xrange(numPeople + 1):
    x = random.uniform(0, width)
    y = random.uniform(0, height)
    #G.add_nodes(i)
    if i == numPeople:
      # goal location
      goal = (x, y)
      break
    # people locations
    elif (i in carNodes):
      people.append( (x, y, ARGV.capacity) )
    else:
      people.append( (x, y, 0) )

  return people, goal

def clustered(numPeople, numCars, width, height):
  """
  Passengers clustered around each of the drivers
  """
  people = []
  drivers = [ None ] * numCars
  # pick drivers locations uniformly
  for i in xrange(numCars):
    x = random.uniform(0, width)
    y = random.uniform(0, height)
    drivers[i] = (x,y)
    people.append( (x, y, ARGV.capacity) )
  # cluster other people around drivers
  for i in xrange(numPeople - numCars):
    center = random.choice(drivers)
    x = random.gauss(center[0], ARGV.stddev)
    while x < 0 or x > 10:
      x = random.gauss(center[0], ARGV.stddev)
    y = random.gauss(center[1], ARGV.stddev)
    while y < 0 or y > 10:
      y = random.gauss(center[0], ARGV.stddev)
    people.append( (x, y, 0) )
  # goal
  x = random.uniform(0, width)
  y = random.uniform(0, height)
  goal = (x, y)
  return people, goal

def detours(numPeople, numCars, width, height):
  """
  Drivers, goal from uniform
  Passengers from points perturbed off path of driver to goal
  """
  people = []
  drivers = []
  for i in xrange(numCars):
    x = random.uniform(0, width)
    y = random.uniform(0, height)
    drivers.append( (x, y) )
    people.append( (x, y, ARGV.capacity) )
  x = random.uniform(0, width)
  y = random.uniform(0, height)
  goal = (x, y)
  for i in xrange(numPeople - numCars):
    chosen = random.choice(drivers)
    x = random.uniform(min(chosen[0], goal[0]), max(chosen[0], goal[0]))
    y = random.uniform(min(chosen[1], goal[1]), max(chosen[1], goal[1]))
    x += random.gauss(0, ARGV.stddev)
    if x < 0: x = 0.0
    if x > width: x = width
    y += random.gauss(0, ARGV.stddev)
    if y < 0: y = 0.0
    if y > width: y = width
    people.append( (x, y, 0) )
  return people, goal

def dense(numPeople, numCars, width, height):
  """
  Drivers, passengers and goal from gaussian
  """
  people = []
  midx, midy = 0.5 * width, 0.5 * height
  # drivers
  for i in xrange(numCars):
    x = random.gauss(midx, ARGV.stddev)
    y = random.gauss(midy, ARGV.stddev)
    people.append( (x, y, ARGV.capacity) )
  # passengers
  for i in xrange(numPeople - numCars):
    x = random.gauss(midx, ARGV.stddev)
    y = random.gauss(midy, ARGV.stddev)
    people.append( (x, y, 0) )
  # goal
  x = random.gauss(midx, ARGV.stddev)
  y = random.gauss(midy, ARGV.stddev)
  goal = (x, y)
  return people, goal

def write_out(out, people, goal):
  """
  Write out data in required format
  """
  # num people
  out.write("{}\n".format( len(people) + 1 ))
  # each person
  random.shuffle(people)
  for p in people:
    out.write("{} {} {}\n".format(*p))
  # goal
  out.write("{} {}\n".format(*goal))
  # edges
  locations = map(lambda p: (p[0], p[1]), people)
  locations.append( goal )
  for i, origin in enumerate(locations):
    for j, dest in enumerate(locations):
      if i < j:
        out.write("{} {} {}\n".format(i, j, dist(origin, dest)))

def dist(a,b):
  dist = ((a[0]-b[0])**2 + (a[1]-b[1])**2)**0.5
  return dist

algorithms = {
  "uniform": uniform,
  "clustered": clustered,
  "detours": detours,
  "dense": dense
}

# generate random locations for people and goal state
def gen():
  """
  Generate map using model, numPeople and numCars specified
  """
  model = ARGV.model
  numPeople = ARGV.numpeople
  numCars = ARGV.numcars
  width = 10.0
  height = 10.0

  filename = "data/generated_{}_{}_{}.txt".format(model, numPeople, numCars)
  people, goal = algorithms[model](numPeople, numCars, width, height)
  with open(filename, "w") as out:
    write_out(out, people, goal)

  print "Written to: {}".format(filename)

colors = ["red", "blue", "green", "yellow", "black"]

def plot_locations(xs, ys, cats):
  if ARGV.verbose: print "Limits: {}".format([-0.5, np.max(xs) + 0.5, -0.5, np.max(ys) + 0.5])
  plt.axis([-0.5, 10.5, -0.5, 10.5])
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

def graph():
  f = ARGV.datafile
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
  generated_fname_glob = "*_" + path.basename(f.name)
  data_gen_algorithm = path.basename(f.name).split("_")[0]
  data_gen_algorithm = data_gen_algorithm[:1].upper() + data_gen_algorithm[1:]
  if ARGV.verbose: print generated_fname_glob
  # plot just the data
  plot_locations(xs, ys, cats)
  plt.title("Data: " + data_gen_algorithm)
  if ARGV.show:
    plt.show()
  else:
    cwd = path.dirname(path.abspath(__file__))
    if not path.exists(path.join(cwd, 'plots')):
      os.mkdir(path.join(cwd, 'plots'))
    plt.savefig(path.join(cwd, 'plots', path.splitext(path.basename(f.name))[0] + '.png'))
    print "Plotted: " + path.splitext(path.basename(f.name))[0] + '.png'
  # now plot for algorithms
  for output in glob(path.join(output_folder, generated_fname_glob)):
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
      if ARGV.show:
        plt.show()
      else:
        cwd = path.dirname(path.abspath(__file__))
        if not path.exists(path.join(cwd, 'plots')):
          os.mkdir(path.join(cwd, 'plots'))
        plt.savefig(path.join(cwd, 'plots', path.splitext(path.basename(output))[0] + '.png'))
        print "Plotted: " + path.splitext(path.basename(output))[0] + '.png'
      plt.clf()
  # old plotting code
  # plt.plot(xs[ cats == 1 ], ys[ cats == 1 ], "bo")
  # plt.plot(xs[ cats == 2 ], ys[ cats == 2 ], "ro")
  # plt.plot(xs[ cats == 3 ], ys[ cats == 3 ], "yo")

parser = argparse.ArgumentParser(description='Carpooling')
parser.add_argument("-v", "--verbose", help="Include debug output", action="store_true")

subparsers = parser.add_subparsers(title='Sub commands')

# generation
parser_gen = subparsers.add_parser('gen', help='Generate a dataset')
parser_gen.add_argument("model", help="Model to use in generation", choices=algorithms.keys())
parser_gen.add_argument("numpeople", help="Number of people", type=int)
parser_gen.add_argument("numcars", help="Number of drivers", type=int)
parser_gen.add_argument("-c", "--capacity", help="Number of people per car", type=int, default=4)
parser_gen.add_argument("-s", "--stddev", help="Std dev for gaussian distributions", type=float, default=1.0)
parser_gen.set_defaults(func=gen)

# graphing
parser_graph = subparsers.add_parser('graph', help='Graph dataset and associated runs')
parser_graph.add_argument("datafile", help="Input file", type=argparse.FileType('r'))
parser_graph.add_argument("-s", "--show", help="Show graphs in window", action="store_true")
parser_graph.set_defaults(func=graph)

ARGV = parser.parse_args()

if __name__ == '__main__':
  ARGV.func()
