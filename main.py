import argparse
import pandas as pd
from datetime import datetime
from bunching_analayzer import BusBunchingAnalyzer

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

    df = pd.read_csv(args.csv_path)

    # Convert start and end times to datetime objects
    start_time = datetime.strptime(args.start_time, '%Y-%m-%d %H:%M:%S')
    end_time = datetime.strptime(args.end_time, '%Y-%m-%d %H:%M:%S')

    # Create BusBunchingAnalyzer instance
    analyzer = BusBunchingAnalyzer(df)

    # Calculate normalized bunching coefficient
    coeff = analyzer.get_normalized_bunching_coefficient(args.line_number, start_time, end_time)

    # Print result
    print(f'Normalized bunching coefficient for line {args.line_number}: {coeff}')

if __name__ == '__main__':
    main()