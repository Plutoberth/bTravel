import pandas as pd
import requests
import json
from datetime import datetime
from collections import OrderedDict
import matplotlib.pyplot as plt

# Given a journey ref gets all the arrival times for it
def get_jounry_arrivals(jounry_ref, line):
    # Get the arrival time for each station for the jounry_ref
    stations = line[(line.DatedVehicleJourneyRef == jounry_ref) & (line.actualArrivalTime.notnull())]
    stations_time = stations.drop_duplicates(subset=['stopOrder'])[['stopOrder', 'actualArrivalTime']].drop_duplicates(subset=['actualArrivalTime'], keep='first')
    stations_arrival = {s.stopOrder: datetime.fromisoformat(s.actualArrivalTime) for i, s in stations_time.iterrows()}
    
    return stations_arrival

# Given 2 stop dicts that contain {stopOrder: arrivalTime}
# Finds how much j2_stops deviated from j1_stops
def get_journies_diff(j1_stops, j2_stops):
    diff = {}

    start_diff = j2_stops[2] - j1_stops[2]
    for stop, time in j1_stops.items():
        if stop not in j2_stops:
            continue

        diff[stop] = (j2_stops[stop] - j1_stops[stop]) / start_diff

    return diff

# Compares the stops of a given journey to the stops of all the line
# Each stop is a dict {stopOrder: arrivalTime}
def compare_to_line(stops, line_stops):
    diffs = []
    for s in line_stops:
        if 2 not in s:
            continue
        diffs.append(get_journies_diff(stops, s))
    return diffs

# Get all the data for a line for one day
# The date is isoformat string
def get_line_data(line_num, date, df):
    line = df[(df.LINE_SHORT_NAME == line_num) & (df.DataFrameRef == date)]
    return line

# Wont return journies that didnt stop at the first station
def get_line_stops(line_num, date, df):
    line_data = get_line_data(line_num, date, df)
    line_stops = {ref: get_jounry_arrivals(ref, line_data) for ref in line_data.DatedVehicleJourneyRef.unique()}
    line_stops_first = {ref: data for ref, data in line_stops.items() if 2 in data}
    
    return line_stops_first

def get_pairs(line_stops):
    pairs = []
    sorted_stops = sorted(OrderedDict(line_stops).items(), key=lambda x: x[1][2])

    for i in range(0, len(sorted_stops) - 2):
        pairs.append((sorted_stops[i], sorted_stops[i + 1]))
    
    return pairs
  
def get_line_bunching(line_num, date, df):
    line_stops = get_line_stops(line_num, date, df)
    pairs = get_pairs(line_stops)
    
    bunching = []
    for j1, j2 in pairs:
        bunching.append((j1[1][2], get_journies_diff(j1[1], j2[1])))
    
    return bunching
