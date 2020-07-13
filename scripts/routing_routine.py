import dispatcher
import pandas as pd
import datetime as dt

import datetime as dt
from pytz import timezone
import os
import sys


# utility functions
def split_by_drivers(df):
    '''
    Given a dataframe with all routes, yields one
    dataframe per route.
    '''
    id_seps = df.loc[df.full_address.isna()].index
    id_start = 0
    for id_ in id_seps:
        yield df.iloc[id_start:id_]
        id_start = id_ + 1
    yield df.iloc[id_start:len(df)]


def get_start_end(df):
    '''
    Given single route data, returns start and end points for the routing algorithm
    '''
    return tuple(df.loc[~df.Consumer.astype(bool)].iloc[-2:][['lat', 'lng']].values.tolist())


def get_destinations(df):
    '''
    Given single route data, returns list of locations to route
    '''
    return df.loc[df.Consumer.astype(bool), ['lat', 'lng']].values.tolist()


def add_results(df, route):
    '''adds results from routing back into the main dataframe'''
    dest_df = pd.DataFrame([{'lat': lat, 'lng': lng, 'order': i}
                            for i, (lat, lng) in enumerate(route)])
    df_res = pd.merge(df, dest_df, on=['lat', 'lng'], how='left')
    id_start = df_res.loc[df_res.order == 0].index[0]
    df_res['order'] += id_start
    df_res.loc[~df_res.Consumer.astype(
        bool), 'order'] = df_res.loc[~df_res.Consumer.astype(bool)].index
    df_res = df_res.sort_values(by=['order']).drop(['order'], axis=1)
    df_res.loc[len(df_res), 'Consumer'] = dispatcher.generate_gmaps_url(
        df_res.full_address.values.tolist())
    return df_res


def dedup_destinations(destinations):
    '''make sure we don't process duplicate locations'''
    unique_dest = []
    for i, d1 in enumerate(destinations):
        found_dup = False
        for j, d2 in enumerate(destinations):
            if j <= i:
                continue
            if (d1[0] == d2[0]) & (d1[1] == d2[1]):
                print("found duplicate")
                found_dup = True
                break
        if not found_dup:
            unique_dest.append(d1)
    return unique_dest


def run_algo(route_df):
    start, end = get_start_end(route_df)
    destinations = get_destinations(route_df)
    destinations = dedup_destinations(destinations)
    route, time = dispatcher.travelling_salesman_NN(start, end, destinations)
    print("Route found: {} min".format(time/60))
    return add_results(route_df, route)


if __name__ == "__main__":
    # Configure using API key
    # GMAPS_API_KEY needs to be populated with the API key value
    if os.environ.get("GMAPS_API_KEY") is None:
        raise Exception("GMAPS_API_KEY needs to be populated")
    dispatcher.configure(os.environ.get("GMAPS_API_KEY"))

    # Parse input arguments
    if len(sys.argv) != 2:
        raise Exception(f"Usage: python {sys.argv[0]} <path to file>")
    input_file = sys.argv[1]
    df = pd.read_csv(input_file)

    # Output filename
    # tomorrow = dt.datetime.now(timezone('US/Pacific')) + dt.timedelta(hours=16)
    # output_file = f'/tmp/helpberkeley_routes_{tomorrow.strftime("%m%d")}.csv'

    # Sanity checks on input df
    mandatory_columns = ['Address', 'City', 'Consumer']
    for c in mandatory_columns:
        if c not in df.columns:
            raise Exception(f"Missing column '{c}'")
    if not isinstance(df.Consumer[0], bool):
        raise Exception(
            f"First row of data should be a driver (value for 'Driver' should 'true'")

    # populate lat/long data
    df['full_address'] = df['Address']+", " + \
        df['City'].fillna("Berkeley") + ", CA"
    df["lat"] = None
    df["lng"] = None
    df.loc[~df.full_address.isna(), ["lat", "lng"]] = \
        df[~df.full_address.isna()].full_address.apply(
            lambda x: pd.Series(dispatcher.address_to_latlon(x)))

    # run algorithm for each route
    res = []
    for d in split_by_drivers(df):
        res.append(run_algo(d))
    output = pd.concat(res).reset_index(drop=True)
    output.to_csv('/tmp/helpberkeley_routes.csv', index=False)
