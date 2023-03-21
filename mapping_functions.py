import json
import requests
from collections import defaultdict
import numpy as np
import plotly.express as px
import pandas as pd

# Analyzer functions
def get_line_bunching_avg(bunching):
    station_bunch = defaultdict(list)
    for journey in bunching:
        for station_order, bunch in journey[1].items():
            station_bunch[station_order].append(bunch)

    bunching_avg = []      
    for station, bunch_list in station_bunch.items():
        bunching_avg.append((station, sum(bunch_list) / len(bunch_list)))
    
    return bunching_avg

def get_stop_cor(stop_id):
    return json.loads(requests.get(f"https://open-bus-stride-api.hasadna.org.il/gtfs_stops/list?limit=1&code={stop_id}").text)[0]

# Get the stop cor for each stopOrder
def get_line_stops_cor(line_num, df):
    stop_order_id = df[(df.LINE_SHORT_NAME == line_num)][['stopOrder', 'stopId']].drop_duplicates()
    cors = {}
    for i, data in stop_order_id.iterrows():
        stop_order, stop_id = data
        d = get_stop_cor(stop_id)
        cors[stop_order] = (d['lat'], d['lon'])
    
    return cors
  
# Mapping functions
def zoom_center(lons: tuple=None, lats: tuple=None, lonlats: tuple=None,
      format: str='lonlat', projection: str='mercator',
      width_to_height: float=2.0) -> (float, dict):
    """Finds optimal zoom and centering for a plotly mapbox.
    Must be passed (lons & lats) or lonlats.
    Temporary solution awaiting official implementation, see:
    https://github.com/plotly/plotly.js/issues/3434

    Parameters
    --------
    lons: tuple, optional, longitude component of each location
    lats: tuple, optional, latitude component of each location
    lonlats: tuple, optional, gps locations
    format: str, specifying the order of longitud and latitude dimensions,
      expected values: 'lonlat' or 'latlon', only used if passed lonlats
    projection: str, only accepting 'mercator' at the moment,
      raises `NotImplementedError` if other is passed
    width_to_height: float, expected ratio of final graph's with to height,
      used to select the constrained axis.

    Returns
    --------
    zoom: float, from 1 to 20
    center: dict, gps position with 'lon' and 'lat' keys

    >>> print(zoom_center((-109.031387, -103.385460),
    ...     (25.587101, 31.784620)))
    (5.75, {'lon': -106.208423, 'lat': 28.685861})
    """
    if lons is None and lats is None:
      if isinstance(lonlats, tuple):
          lons, lats = zip(*lonlats)
      else:
          raise ValueError(
              'Must pass lons & lats or lonlats'
          )

    maxlon, minlon = max(lons), min(lons)
    maxlat, minlat = max(lats), min(lats)
    center = {
      'lon': round((maxlon + minlon) / 2, 6),
      'lat': round((maxlat + minlat) / 2, 6)
    }

    # longitudinal range by zoom level (20 to 1)
    # in degrees, if centered at equator
    lon_zoom_range = np.array([
      0.0007, 0.0014, 0.003, 0.006, 0.012, 0.024, 0.048, 0.096,
      0.192, 0.3712, 0.768, 1.536, 3.072, 6.144, 11.8784, 23.7568,
      47.5136, 98.304, 190.0544, 360.0
    ])

    if projection == 'mercator':
      margin = 1.2
      height = (maxlat - minlat) * margin * width_to_height
      width = (maxlon - minlon) * margin
      lon_zoom = np.interp(width , lon_zoom_range, range(20, 0, -1))
      lat_zoom = np.interp(height, lon_zoom_range, range(20, 0, -1))
      zoom = round(min(lon_zoom, lat_zoom), 2)
    else:
      raise NotImplementedError(
          f'{projection} projection is not implemented'
      )

    return zoom, center

def plot_bunching_map(station_bunch, cors):
    values = []
    lats = []
    lons = []
    
    for station, bunch in station_bunch:
        values.append(bunch)
        lats.append(cors[station][0])
        lons.append(cors[station][1])
        
    data = {
        'lats': {i: lats[i] for i in range(len(lats))}, 
        'lons': {i: lons[i] for i in range(len(lons))}, 
        'values': {i: values[i] for i in range(len(values))}
    }
        
    zoom, center = zoom_center(lons, lats, width_to_height=(800/600) * 2)
    fig = px.scatter_mapbox(pd.DataFrame(data), lat='lats', lon='lons', color='values', mapbox_style='carto-positron',
                            height=600, width=800, zoom=zoom, center=center, color_continuous_scale="blackbody_r",
                            range_color=[0, 3])

    fig.write_image('fig_export.png')
    return fig



# plot_bunching_map useage example
# df = pd.read_csv('VM_9999_2023-01.csv')
# bunching = get_line_bunching(line_num, date, df)
# station_bunch = get_line_bunching_avg(bunching)
# cors = get_line_stops_cor(line_num, df)
# fig = plot_bunching_map(station_bunch, cors)
# fig.write_image('fig_export.png')
