#!/usr/bin/env python
# coding: utf-8

import stride, stride.api_proxy
from datetime import datetime, timedelta
import pytz
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from numpy import arange
from math import ceil
import time


def get_line_rides(line, start_datetime, end_datetime, limit=100, offset=0):
    get_params = {
        "limit": limit,
        "offset": offset,
        "gtfs_route__line_refs": line,
        "start_time_from": start_datetime,
        "start_time_to": end_datetime,
    }

    routes = {}
    snap_c = 0
    
    stride.api_proxy.start()
    data = stride.get("/gtfs_rides/list", params=get_params)
    
    for snap in data:
        snap_c += 1
        if snap['gtfs_route_id'] not in routes:
            routes[snap['gtfs_route_id']] = []

        routes[snap['gtfs_route_id']].append(snap['start_time'])
    
    return routes

def generate_bunching_by_hour_graph(line_id_ref, start_time, end_time):
    routes = get_line_rides(line_id_ref, start_time, end_time)

    buses_per_time = {}
    for index, route in enumerate(routes):
        
        times = list([0] * 24)
        for t in list(routes.values())[index]:
            times[t.hour] += 1
        
        buses_per_time[list(routes.keys())[index]] = times

    fig, ax = plt.subplots(1,1)
    sum_yx = [0] * 24
    x = range(0,24)

    labels = [f"route_{index}" for index in range(len(buses_per_time))]

    for index, route in enumerate(list(buses_per_time.values())):
        ax.scatter(x,route)
        ax.plot(x,route, label=labels[index])
        sum_yx = list(map(sum, zip(sum_yx, route)))

    ax.scatter(x,sum_yx)
    ax.plot(x,sum_yx, label=f"routes_sum")

    ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
    plt.legend(loc="upper left")


    plt.show()



def get_starting_time(times, time):
    for t in times:
        if time > t:
            return t
    
    raise ValueError()


def get_freq_buses(route_list, freq_interval: timedelta, start_time: datetime, end_time: datetime):
    """Get a list of all of the buses, organized by frequency.

    :param route_list: the routes
    :param freq_interval: the time delta in hours
    :return: the dictionary of freq:[buses]
    """
    result = dict()
    
    curr_time = start_time
    keys = []
    values = dict()
    while curr_time < end_time:
        keys.append(curr_time)
        values[curr_time] = 0
        curr_time += freq_interval
    
    for r in route_list:
        values[get_starting_time(values.keys())] += 1


def test_bunching_by_hour():
    ROUTE_LINE_REF = 3315
    START_TIME = datetime(2023, 1, 1, hour=0, minute=0, second=0, tzinfo=pytz.timezone('Israel'))
    END_TIME = datetime(2023, 1, 31, hour=23, minute=0, second=0, tzinfo=pytz.timezone('Israel'))

    generate_bunching_by_hour_graph(ROUTE_LINE_REF, START_TIME, END_TIME)


if __name__ == '__main__':
    test_bunching_by_hour()




