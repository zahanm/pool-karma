
from heapq import heappush, heappop

def exhaustive(data, states, state_cost_fn):
  min_cost = float("inf")
  min_state = None
  for state in states:
    cost = state_cost_fn(data, state, min_cost)
    if cost < min_cost:
      min_cost = cost
      min_state = state
  return min_cost, min_state

class Exhaustive:
  """
  TODO
  """
  pass

class UCS:
  """
  Uniform cost search
  """

  def __init__(self, actions, goal):
    self.actions = actions
    self.goal = goal
    self.explored = set()
    self.frontier = []

  def __call__(self, start):
    heappush(self.frontier, (0, start))
    while True:
      if len(self.frontier) == 0:
        if ex.VERBOSE: print "Failed to find the goal!"
        return None
      priority, s = heappop(self.frontier)
      if self.goal(s):
        return priority, s
      self.explored.add(s)
      for t, cost in self.actions(s):
        if t in self.explored:
          continue
        heappush(self.frontier, (priority + cost, t))
