import numpy as np

from . import utils


@utils._gmaps_check_decorator
def travelling_salesman_NN(start_location, end_location, destinations):
    """
    Very simple traveling salesman implementation
    Determines a route given a start point and end point by finding the nearest
    neighbor, switching back and forth between the start and end point.

    Uses n(n-1)/2 google maps directions API.
    """
    route = [start_location] + [None]*len(destinations) + [end_location]
    route, time = _find_NN_route(destinations, route, 0)
    # reverse if need be
    if route[0] != start_location:
        route.reverse()
    return route, time


def _find_NN_route(destinations, route, total_time):
    """Recursively builds the route between the start point and end point"""
    if len(destinations) == 0:
        return route, total_time
    # find previous point and index of point to add
    start = None
    for i, p in enumerate(route):
        if p is None:
            start = route[i-1]
            break
    closest, min_dist = find_closest(start, destinations)
    print("Found new point in route")
    route[i] = destinations[closest]
    total_time += min_dist
    # we start from other side of the path next iteration
    route.reverse()
    return _find_NN_route([p for (i, p) in enumerate(destinations) if i != closest], route, total_time)


def find_closest(start, destinations):
    min_dist = np.inf
    closest = None
    for i, p in enumerate(destinations):
        dist = utils.get_duration(start, p)
        if dist < min_dist:
            min_dist = dist
            closest = i
    return closest, min_dist


def _find_NN_route_forward(start_location, destinations, route, total_time):
    """
    Version of the routing algorithm using start point constraint only.
    (not used anymore)
    """
    if len(destinations) == 0:
        return route, total_time
    min_dist = np.inf
    closest = None
    for p in destinations:
        dist = utils.get_duration(start_location, p)
        if dist < min_dist:
            min_dist = dist
            closest = p
    print("Found new point in route")
    route.append(closest)
    total_time += min_dist
    return _find_NN_route_forward(closest, [p for p in destinations if p != closest], route, total_time)
