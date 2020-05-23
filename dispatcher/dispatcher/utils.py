import functools
import googlemaps
import gmaps
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


def get_duration(start, end):
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


def generate_gmaps_url(route):
    '''route: list of (lat, lon)'''
    prefix = 'https://www.google.com/maps/dir/'
    return prefix + '/'.join(route).replace("#", '%23').replace(' ', '+')


def address_to_latlon(addr):
    return GMAPS_CLIENT.geocode(addr)[0]['geometry']['location']
