import folium
import pandas as pd
from folium import plugins

# Loading pkl
distances = pd.read_pickle('data_noaa/distances.pkl')
df_stations = pd.read_pickle('data_noaa/df_stations.pkl')
airports = pd.read_pickle('data_noaa/airports.pkl')


# Folium draw func
def draw_top5_map(input_iata):
    top5stations = distances[[input_iata]] \
        .sort_values(by=input_iata) \
        .head(5) \
        .reset_index() \
        .merge(df_stations,
               left_on='index',
               right_on='id',
               how='left') \
        .rename(columns={input_iata: 'distance'})

    input_lat = float(airports[airports.iata == input_iata].lat)
    input_lon = float(airports[airports.iata == input_iata].lon)

    # Init folium map
    m5 = folium.Map(location=[input_lat, input_lon],
                    zoom_start=10,
                    control_scale=True,
                    tiles="Stamen Terrain")

    # Add root marker for airport
    folium.Marker(
        [input_lat, input_lon],
        popup=input_iata,
        icon=folium.Icon(color='blue',
                         icon='plane',
                         prefix='fa')
    ).add_to(m5)

    # Add NOAA station markers
    for i in range(0, len(top5stations)):
        folium.Marker(
            [top5stations.iloc[i]['lat'], top5stations.iloc[i]['lon']],
            popup=top5stations.iloc[i]['id'] + "\n" + top5stations.iloc[i]['name'] + "\n" + str(
                top5stations.iloc[i]['distance']),
            icon=folium.Icon(color='green',
                             icon='cloud',
                             prefix='fa')
        ).add_to(m5)

    # Init + add minimap
    minimap = plugins.MiniMap()
    m5.add_child(minimap)

    return m5


# Pre-rendering all airports' top-5 map
for x in range(0, len(airports)):
    inputx = str(airports.iloc[x]['iata'])
    filename = str("data_dash/prerenders/" + inputx + ".html")

    map_obj = draw_top5_map(inputx)
    map_obj.save(filename)
