import argparse
import pandas as pd
from os.path import join as ospj
import os
from datetime import datetime

from bunching_analayzer import BusBunchingAnalyzer
import mapping_functions
from route_progress_graph import RouteProgressGraphBuilder
from gen_report import generate_report

REPORT_BASEDIR = "reports"

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

    basedir = ospj(REPORT_BASEDIR, str(line_number))
    os.makedirs(basedir, exist_ok=True)

    # Create BusBunchingAnalyzer instance
    analyzer = BusBunchingAnalyzer(line_df)

    # Calculate normalized bunching coefficient
    coeff = analyzer.get_normalized_bunching_coefficient(line_number, start_time, end_time)

    # Print result
    print(f'Normalized bunching coefficient for line {line_number}: {coeff}')

    bunching = analyzer.get_line_bunching(line_number, start_time, end_time)
    station_bunch = mapping_functions.get_line_bunching_avg(bunching)
    cors = mapping_functions.get_line_stops_cor(line_number, df)

    bunching_map_fig = mapping_functions.plot_bunching_map(station_bunch, cors)
    bunching_map_fig.write_image(ospj(basedir, 'bus_stop_bunching.png'))

    print(f'Analyzed bunching heatmap of line {line_number}')

    route_progress_graph_builder = RouteProgressGraphBuilder(line_df)

    save_path = ospj(basedir, "route_journeys.png")
    route_progress_graph_builder.plot_bus_line(args.line_id, start_time, end_time, save_path)
    
    report_filename = ospj(basedir, "report.pdf")
    generate_report(report_filename, basedir, line_number)

    

    print(f'Analyzed route progress graph of line {line_number} and wrote report to {report_filename}')

if __name__ == '__main__':
    main()