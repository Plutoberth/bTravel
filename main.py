import argparse
import pandas as pd
from datetime import datetime
from bunching_analayzer import BusBunchingAnalyzer
from route_progress_graph import RouteProgressGraphBuilder

def main():
    # Create argument parser
    parser = argparse.ArgumentParser(description='analyze bunching phenomenon in buses.')

    # Add arguments
    parser.add_argument('csv_path', type=str, help='Path to CSV file.')
    parser.add_argument('line_id', type=int, help='id of the bus line.')
    parser.add_argument('start_time', type=str, help='Start time in format YYYY-MM-DD HH:MM:SS.')
    parser.add_argument('end_time', type=str, help='End time in format YYYY-MM-DD HH:MM:SS.')

    # Parse arguments
    args = parser.parse_args()

    df = pd.read_csv(args.csv_path, parse_dates=["messageCreationTime"])

    # Convert start and end times to datetime objects
    start_time = datetime.strptime(args.start_time, '%Y-%m-%d %H:%M:%S')
    end_time = datetime.strptime(args.end_time, '%Y-%m-%d %H:%M:%S')

    # Convert bus id to bus line
    line_df = df[df.LINE_ID == args.line_id]
    try:
        line_number = line_df.LINE_SHORT_NAME.unique()[0]
    except IndexError:
        raise Exception("The line id was not found")


    # Create BusBunchingAnalyzer instance
    analyzer = BusBunchingAnalyzer(line_df)

    # Calculate normalized bunching coefficient
    coeff = analyzer.get_normalized_bunching_coefficient(line_number, start_time, end_time)

    # Print result
    print(f'Normalized bunching coefficient for line {line_number}: {coeff}')

    route_progress_graph_builder = RouteProgressGraphBuilder(line_df)

    route_progress_graph_builder.plot_bus_line(args.line_id, start_time, end_time)

if __name__ == '__main__':
    main()