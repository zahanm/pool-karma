
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
        return None
      priority, s = heappop(self.frontier)
      if self.goal(s):
        return priority, s
      self.explored.add(s)
      for t, cost in self.actions(s):
        if t in self.explored:
          continue
        heappush(self.frontier, (priority + cost, t))

class DFS:
  """
  Depth first search for optimal path cost
  """

  def __init__(self, actions, goal):
    self.actions = actions
    self.goal = goal
    self.gmin_cost = float("inf")
    # no need, I know the graph is acyclic
    # self.explored = set()

  def __call__(self, start):
    # recursive inner function
    def dfs(s, path_cost):
      if self.goal(s):
        return path_cost, s
      min_cost = float("inf")
      min_state = None
      for t, cost in self.actions(s):
        if path_cost + cost > self.gmin_cost:
          continue
        final_cost, final_state = dfs(t, path_cost + cost)
        if final_cost < min_cost:
          min_cost = final_cost
          min_state = final_state
      if min_cost < self.gmin_cost:
        self.gmin_cost = min_cost
      return min_cost, min_state
    # start algorithm
    return dfs( start, 0.0 )
