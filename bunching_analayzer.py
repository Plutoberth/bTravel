import pandas as pd
from datetime import datetime

class BusBunchingAnalyzer:
    def __init__(self, csv_path: str):
        self.df = pd.read_csv(csv_path)

    def get_line_bunching(self, bus_line: str, start_time: datetime, end_time: datetime) -> list:
        """
        Returns a list of tuples representing the bunching coefficients for a given bus line during a given time period.
        """
        pass
        
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

        line_coefficent_sum = 0

       	for bus_departure_time, stops_coefficient in line_bunching:
       		bus_stops_coefficent_sum = 0
       		for stop_id, stop_coefficient in stops_coefficient.items():
       			bus_stops_coefficent_sum += stop_coefficient
       		line_coefficent_sum += bus_stops_coefficent_sum / len(stops_coefficient)

       	return line_coefficent_sum / len(line_bunching)