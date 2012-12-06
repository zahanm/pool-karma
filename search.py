
def exhaustive(data, states, state_cost_fn):
  min_cost = float("inf")
  min_state = None
  for state in states:
    cost = state_cost_fn(data, state, min_cost)
    if cost < min_cost:
      min_cost = cost
      min_state = state
  return min_cost, min_state
