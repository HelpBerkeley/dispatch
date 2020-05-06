import functools
import googlemaps
import gmaps
import numpy as np
from datetime import datetime as dt


GMAPS_CLIENT = None


def configure(api_key):
    global GMAPS_CLIENT
    gmaps.configure(api_key=api_key)
    GMAPS_CLIENT = googlemaps.Client(key=api_key)


def _gmaps_check_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if GMAPS_CLIENT is None:
            raise Exception(
                "Please make sure to run `dispatcher.configure(<your gmaps API key)` first")
        return func(*args, **kwargs)
    return wrapper


def _get_duration(start, end):
    now = dt.now()
    res = GMAPS_CLIENT.directions(start,
                                  end,
                                  mode="driving",
                                  departure_time=now)
    if len(res) != 1:
        raise Exception("directions result has size {}".format(
            len(res)))

    if len(res[0]['legs']) != 1:
        raise Exception("expected one leg, not {}".format(
            len(res)))

    return res[0]['legs'][0]['duration']['value']


@_gmaps_check_decorator
def travelling_salesman_NN(start_location, end_location, destinations):
    route = [start_location] + [None]*len(destinations) + [end_location]
    route, time = _find_NN_route(destinations, route, 0)
    # reverse if need be
    if route[0] != start_location:
        route.reverse()
    return route, time


def _find_NN_route(destinations, route, total_time):
    if len(destinations) == 0:
        return route, total_time
    # find previous point and index of point to add
    for i, p in enumerate(route):
        if p is None:
            start = route[i-1]
            break
    closest, min_dist = find_closest(start, destinations)
    print("Found new point in route")
    route[i] = closest
    total_time += min_dist
    # we start from other side of the path next iteration
    route.reverse()
    return _find_NN_route([p for p in destinations if p != closest], route, total_time)


def _find_NN_route_forward(start_location, destinations, route, total_time):
    if len(destinations) == 0:
        return route, total_time
    min_dist = np.inf
    closest = None
    for p in destinations:
        dist = _get_duration(start_location, p)
        if dist < min_dist:
            min_dist = dist
            closest = p
    print("Found new point in route")
    route.append(closest)
    total_time += min_dist
    return _find_NN_route(closest, [p for p in destinations if p != closest], route, total_time)


def find_closest(start, destinations):
    min_dist = np.inf
    closest = None
    for p in destinations:
        dist = _get_duration(start, p)
        if dist < min_dist:
            min_dist = dist
            closest = p
    return closest, min_dist


def generate_gmaps_url(route):
    '''route: list of (lat, lon)'''
    prefix = 'https://www.google.com/maps/dir/'
    return prefix + '/'.join(route).replace("#", '%23').replace(' ', '+')


def address_to_latlon(addr):
    return GMAPS_CLIENT.geocode(addr)[0]['geometry']['location']
