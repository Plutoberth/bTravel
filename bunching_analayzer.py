import argparse
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

def main():
    # Create argument parser
    parser = argparse.ArgumentParser(description='analyze bunching phenomenon in buses.')

    # Add arguments
    parser.add_argument('csv_path', type=str, help='Path to CSV file.')
    parser.add_argument('line_number', type=int, help='Line number of the bus.')
    parser.add_argument('start_time', type=str, help='Start time in format YYYY-MM-DD HH:MM:SS.')
    parser.add_argument('end_time', type=str, help='End time in format YYYY-MM-DD HH:MM:SS.')

    # Parse arguments
    args = parser.parse_args()

    # Convert start and end times to datetime objects
    start_time = datetime.strptime(args.start_time, '%Y-%m-%d %H:%M:%S')
    end_time = datetime.strptime(args.end_time, '%Y-%m-%d %H:%M:%S')

    # Create BusBunchingAnalyzer instance
    analyzer = BusBunchingAnalyzer(args.csv_path)

    # Calculate normalized bunching coefficient
    coeff = analyzer.get_normalized_bunching_coefficient(args.line_number, start_time, end_time)

    # Print result
    print(f'Normalized bunching coefficient for line {args.line_number}: {coeff}')

if __name__ == '__main__':
    main()