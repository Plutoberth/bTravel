import requests
import os
import json
import pandas as pd
import math
import matplotlib.pyplot as plt

class RouteProgressGraphBuilder:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.groups = self.df[["LINE_ID", "DatedVehicleJourneyRef", "DataFrameRef",
                               "percentageFromStart", "messageCreationTime"]].groupby(self.df.LINE_ID)
    
    def plot_bus_line(self, line_ref, start_time, end_time):
        line_rides = self.groups.get_group(line_ref)[["DatedVehicleJourneyRef", "DataFrameRef",
                                                       "percentageFromStart", "messageCreationTime"]].fillna(0)
        line_rides = line_rides.groupby(["DatedVehicleJourneyRef", "DataFrameRef"])

        ax = None

        # Add graph line for each bus ride
        # Only in requested date
        for l in line_rides:
            time_list = l[1]["messageCreationTime"].tolist()
            if time_list[0] > start_time and time_list[-1] < end_time:
                ax = l[1].plot(x='messageCreationTime',y='percentageFromStart', ax=ax, legend=False)

        ax.set_xlim(start_time, end_time)

        plt.savefig(os.path.normpath(f"{line_ref}_route_journeys.png"))
        
    def add_stop_lines(self, line_ref, start_time, end_time):
        j = json.loads(requests.get(f"https://open-bus-stride-api.hasadna.org.il/gtfs_routes/list?line_refs={line_ref}&order_by=date%20desc").text)
        stops = j[0]

        fig, ax = plt.subplots()

        line_rides = self.groups.get_group(line_ref)[["DatedVehicleJourneyRef", "DataFrameRef",
                                                       "percentageFromStart", "messageCreationTime"]].fillna(0)
        line_rides = line_rides.groupby(["DatedVehicleJourneyRef", "DataFrameRef"])

        # Add graph line for each bus ride
        # Only in requested date
        for l in line_rides:
            if l[1]["messageCreationTime"].between(str(start_time), str(end_time)):
                ax = l[1].plot(x='messageCreationTime',y='percentageFromStart', ax=ax, legend=False)

        # Add horizontal dashed lines for each stop
        for stop in stops:
            ax.axhline(y=stop, color='black', linestyle='--')

        ax.set_xlim(pd.Timestamp(date + ' 06'), pd.Timestamp(date + ' 12'))
        ax.set_xlabel('Time')
        ax.set_ylabel('Percentage of route completed')

        plt.savefig(f"{line_ref}_{date}_stops.png")