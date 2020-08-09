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

def exhaustive_Hamiltonian_cycle(dist_matrix, start):
    """
        Top-level function to exhaustively find (by calling DFS_TSP()) the shortest Hamiltonian cycle
        for a given distance matrix
        
        dist_matrix: a square matrix
        start: an integer corresponding to the index of the starting/ending node
    
    """
    end_dists = np.copy(dist_matrix[:, start])
    internal_dist_matrix = np.copy(dist_matrix)
    internal_dist_matrix[:,start] = np.inf
    tour_best, dist_best = DFS_Hamiltonian(start, internal_dist_matrix, end_dists)
    return tour_best, dist_best

def DFS_Hamiltonian (sub_start, sub_dist_matrix, end_dists, l_0 = 0.0, l_best = np.inf):
    """
        Implements an exhaustive, depth-first TSP search using a distance matrix (does not need to be symmetric)
        
        branch/bound used        
        
        sub_start: integer corresponding to index of starting node of (sub)-problem
        sub_dist_matrix: square numpy array corresponding to distance matrix for (sub)-problem
        end_dists: distance to final node
        
        Returns
        
        tour_best: list of indices in the order of the tour
        dist_best: shortest distance, corresponding to tour_best    
    """
    if np.all(sub_dist_matrix[sub_start,:] == np.inf):
        l_1 = l_0 + end_dists[sub_start]
        return [sub_start, 0], l_1
    else:
        dists = np.zeros(sub_dist_matrix.shape[0]) + np.inf
        tours = []
        for i in range(sub_dist_matrix.shape[0]):
            l_1 = l_0 + sub_dist_matrix[sub_start,i]
            tours.append([])
            # bound paths
            if l_1 <  l_best:
                sub_dist_matrix_copy = np.copy(sub_dist_matrix)
                sub_dist_matrix_copy[:,i] = np.inf # don't return to previously visited nodes
                
                tours[i], dists[i] = DFS_Hamiltonian(i, sub_dist_matrix_copy, end_dists, l_0 = l_1, l_best = l_best)
                if dists[i] <= l_best:
                    l_best = dists[i]
        dist_best = np.min(dists)
        tour_best = [sub_start] + tours[np.argmin(dists)]
        
        return tour_best, dist_best
    
def generate_test_dist_matrix(n, symmetric = True):
    """
        Generates an n x n matrix of distances. Diagonal elements are set to infinity.
    
    """
    dist_matrix = np.abs(np.random.normal(size=(n, n)))
    if symmetric:
        dist_matrix = 0.5 * (dist_matrix + dist_matrix.transpose())
    for i in range(dist_matrix.shape[0]):
        dist_matrix[i,i] = np.inf
    return dist_matrix

def calculate_distance(dist_matrix, tour):
    """
        Calculates the distance for a given tour, just to make sure there's no funny business
    
    """
    total_dist = 0.0
    n_stops = len(tour)
    for i in range(1,n_stops):
        total_dist += dist_matrix[tour[i-1], tour[i]]
    return total_dist
