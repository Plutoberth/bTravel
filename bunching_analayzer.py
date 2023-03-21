import requests
import json
import pandas as pd
from datetime import datetime
from collections import OrderedDict
import matplotlib.pyplot as plt

class BusBunchingAnalyzer:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    # Given a journey ref gets all the arrival times for it
    def get_jounry_arrivals(self, jounry_ref, line):
        # Get the arrival time for each station for the jounry_ref
        stations = line[(line.DatedVehicleJourneyRef == jounry_ref) & (line.actualArrivalTime.notnull())]
        stations_time = stations.drop_duplicates(subset=['stopOrder'])[['stopOrder', 'actualArrivalTime']].drop_duplicates(subset=['actualArrivalTime'], keep='first')
        stations_arrival = {s.stopOrder: datetime.fromisoformat(s.actualArrivalTime) for i, s in stations_time.iterrows()}
        
        return stations_arrival

    # Given 2 stop dicts that contain {stopOrder: arrivalTime}
    # Finds how much j2_stops deviated from j1_stops
    def get_journies_diff(self, j1_stops, j2_stops):
        diff = {}

        start_diff = j2_stops[2] - j1_stops[2]
        for stop, time in j1_stops.items():
            if stop not in j2_stops:
                continue

            diff[stop] = (j2_stops[stop] - j1_stops[stop]) / start_diff

        return diff

    # Compares the stops of a given journey to the stops of all the line
    # Each stop is a dict {stopOrder: arrivalTime}
    def compare_to_line(self, stops, line_stops):
        diffs = []
        for s in line_stops:
            if 2 not in s:
                continue
            diffs.append(get_journies_diff(stops, s))
        return diffs

    # Get all the data for a line for one day
    # The date is isoformat string
    def get_line_data(self, line_num, start_time, end_time):
        line = self.df[(self.df.LINE_SHORT_NAME == line_num) & self.df.messageCreationTime.between(str(start_time), str(end_time))]
        return line

    # Wont return journies that didnt stop at the first station
    def get_line_stops(self, line_num, start_time, end_time):
        line_data = self.get_line_data(line_num, start_time, end_time)
        line_stops = {ref: self.get_jounry_arrivals(ref, line_data) for ref in line_data.DatedVehicleJourneyRef.unique()}
        line_stops_first = {ref: data for ref, data in line_stops.items() if 2 in data}
        
        return line_stops_first

    def get_pairs(self, line_stops):
        pairs = []
        sorted_stops = sorted(OrderedDict(line_stops).items(), key=lambda x: x[1][2])

        for i in range(0, len(sorted_stops) - 2):
            pairs.append((sorted_stops[i], sorted_stops[i + 1]))
        
        return pairs
      
    def get_line_bunching(self, bus_line: str, start_time: datetime, end_time: datetime) -> list:
        """
        Returns a list of tuples representing the bunching coefficients for a given bus line during a given time period.
        Each tuple contains a datetime object of the time the bus left the first station and a dictionary that maps
        station ID to the bunching coefficient of the station.
        """
        line_stops = self.get_line_stops(bus_line, start_time, end_time)
        
        pairs = self.get_pairs(line_stops)
        
        bunching = []
        for j1, j2 in pairs:
            bunching.append((j1[1][2], self.get_journies_diff(j1[1], j2[1])))
        
        return bunching
        
    def get_normalized_bunching_coefficient(self, bus_line: str, start_time: datetime, end_time: datetime) -> float:
        """
        Calculates the normalized bunching coefficient for a given bus line during a given time period.

        Parameters:
        -----------
        bus_line : str
            The number of the bus line to analyze.

        start_time : datetime
            The start time to measure.

        end_time : datetime
            The end time to measure.

        Returns:
        --------
        float
            The normalized bunching coefficient for the given bus line and time period.
        """
        line_bunching = self.get_line_bunching(bus_line, start_time, end_time)

        if not line_bunching:
            raise Exception("The line was not found in the time period specified")

        line_coefficent_sum = 0

       	for bus_departure_time, stops_coefficient in line_bunching:
       		bus_stops_coefficent_sum = 0
       		for stop_id, stop_coefficient in stops_coefficient.items():
       			bus_stops_coefficent_sum += stop_coefficient
       		line_coefficent_sum += bus_stops_coefficent_sum / len(stops_coefficient)

       	return line_coefficent_sum / len(line_bunching)