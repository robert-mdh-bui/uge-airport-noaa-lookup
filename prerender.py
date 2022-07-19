import folium
import pandas as pd
from folium import plugins

# Loading pkl
distances = pd.read_pickle('data_noaa/distances.pkl')
df_stations = pd.read_pickle('data_noaa/df_stations.pkl')
airports = pd.read_pickle('data_noaa/airports.pkl')
mly_pivoted = pd.read_pickle('data_noaa/mly_pivoted.pkl')


# Folium draw func
def draw_top5_map(input_iata):
    top5stations = distances[[input_iata]] \
        .sort_values(by=input_iata) \
        .head(5) \
        .reset_index() \
        .merge(
        df_stations,
        left_on='index',
        right_on='id',
        how='left'
    ) \
        .rename(columns={input_iata: 'distance'}) \
        .merge(
        mly_pivoted,
        left_on='index',
        right_on='GHCN_ID'
    )

    top5mly = top5stations[['id', 'Jan', 'Feb', 'Mar', 'Apr',
                            'May', 'Jun', 'Jul', 'Aug', 'Sep',
                            'Oct', 'Nov', 'Dec']]

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
        table_popup = top5mly.iloc[[i]].drop('id', axis=1) \
            .to_html(index=False,
                     justify='justify-all',
                     border=1)

        html_popup = f'''
                <style>
                h3 {{text-align: center;}}
                p {{text-align: center;}}
                </style>
                <h3>{top5stations.iloc[i]['id']}</h3>
                <hr>
                <p>Name: <b>{top5stations.iloc[i]['name']}</b>
                <br>Distance: <b>{round(top5stations.iloc[i]['distance'], 2)} mi</b></p>
                <hr>
                <p>
                Monthly Low Temps 2016-2020:{table_popup}
                </p>
                '''

        popup = folium.Popup(html_popup, max_width=1000)

        folium.Marker(
            [top5stations.iloc[i]['lat'], top5stations.iloc[i]['lon']],
            popup=popup,
            icon=folium.Icon(color='green',
                             icon='cloud',
                             prefix='fa')
        ).add_to(m5)

    # Init + add minimap
    minimap = plugins.MiniMap()
    m5.add_child(minimap)

    return m5


# Pre-rendering 1 map (ORD)
# test_obj = draw_top5_map("ORD")
# test_obj.save("assets/.testORD.html")

# Pre-rendering all airports' top-5 map
for x in range(0, len(airports)):
    inputx = str(airports.iloc[x]['iata'])
    filename = str("assets/" + inputx + ".html")

    map_obj = draw_top5_map(inputx)
    map_obj.save(filename)
