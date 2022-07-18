US Airport to 5 Nearest NOAA Weather Stations [Web App](https://uge-airport-noaa-lookup.herokuapp.com/)
================
Robert Duc Bui
2022-07-18

![Example:
ORD](https://github.com/robert-mdh-bui/uge-airport-noaa-lookup/blob/main/assets/ORD_screenshot.png?raw=true)

# Prerequisites

To gather and process the data necessary, we will be using the following
Python packages:

-   `pandas`: useful data tools & data frame manipulation.

-   `airportsdata`: open-source Python package to retrieve airport
    information.

-   `haversine`: Python package to calculate distance based on
    coordinates.

-   `dash`: Python package to implement interactive visualizations.

-   `folium`: Python wrapper for `leaflet` to create interactive GIS
    maps.

<!-- -->

    import pandas as pd
    import airportsdata as ad

    import haversine
    from haversine import haversine, haversine_vector, Unit

    import dash
    import dash_core_components as dcc
    from dash import html
    from dash.dependencies import Input, Output

    import folium
    from folium import plugins

# Data Sources

We will be using the following data sources:

-   Airport coordinates (latitude/longitude), ICAO code conversion:
    `airportsdata` from
    [PyPI](https://pypi.org/project/airportsdata/)/[github](https://github.com/mborsetti/airportsdata).
    Data sourced from
    [IATA](https://www.iata.org/en/publications/directories/code-search/)
    made available under the [MIT
    License](https://opensource.org/licenses/MIT).

-   NOAA weather stations participating in [Global Historical
    Climatology Network
    daily](https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/) reporting
    (GHCN-d)
    [metadata](https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt):
    [NOAA
    NCDC](https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/readme.txt).
    Data sourced from the [NOAA NCEI’s open
    API](https://www.ncei.noaa.gov/support/access-data-service-api-user-documentation).

# Methodology

## Step 1: Importing data

The following script imports our data from aforementioned sources.

-   Airport metadata: Filtered for US-based airports only. Selecting for
    IATA code, ICAO code, Latitude, and Longitude.

-   NOAA metadata: retrieve data frame of all NOAA weather stations
    participating in GHCN reporting program for US climate normals.

-   Monthly normal temps from 2006-2020: reading in
    `mly-normal-allall.csv`, downloaded from [NOAA
    site](https://www.ncei.noaa.gov/data/normals-monthly/2006-2020/).

Next, using the monthly normals dataset station ID as primary keys, we
perform a SQL join with the station metadata, only keeping stations with
monthly normal temp data. From this joined table we keep the following
variables:

-   NOAA internal reporting ID

-   Station coordinates (longitude/latitude)

<!-- -->

    ###
    # Reading publicly-available airport metadata
    airports = pd.DataFrame.from_dict(ad.load('IATA'),orient = 'index')[['iata','name','country','lat','lon']]
    airports = airports[airports.country == "US"]

    ###
    # Reading GHCND Station Metadata
    colspecs = [(0, 11), (12, 20), (21, 30), (31, 37), (38, 40), (41, 71), (73,-1)]

    ghcnd_metadata = pd.read_fwf("/content/drive/MyDrive/career/United Ground/uge_deicing_heatwatch_2022/data_noaa/ghcnd-stations.txt",
                                 colspecs = colspecs)
    ghcnd_metadata = ghcnd_metadata.drop(ghcnd_metadata.columns[[4,6]],axis=1)

    ###
    # Extracting monthly normals data (to filter out stations with missing data)
    mly = pd.read_csv('/content/drive/MyDrive/career/United Ground/uge_deicing_heatwatch_2022/data_noaa/by_variable/mly-normal-allall.csv')

    df_stations = mly[['GHCN_ID']]\
      .drop_duplicates()\
      .rename(columns = {'GHCN_ID' : "id"})\
      .merge(ghcnd_metadata,
             on = "id",
             how = 'left')

## Step 2: Finding nearest weather station to each airport

To determine which weather station is closest to each airport, we will
be calculating the distance between each airport and station by their
latitudes and longitudes. We could use either Haversine (half-versine)
distance or Euclidean distance - here, to account for the curvature of
the Earth, we will be using Haversine distance.

The Haversine distance formula, given
![r](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;r "r")
as the radius of earth,
![d](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;d "d")
as the distance between two points,
![\\phi\_{1},\\phi\_{2}](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;%5Cphi_%7B1%7D%2C%5Cphi_%7B2%7D "\phi_{1},\phi_{2}")
as latitudes, and
![\\lambda\_{1}, \\lambda\_{2}](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;%5Clambda_%7B1%7D%2C%20%5Clambda_%7B2%7D "\lambda_{1}, \lambda_{2}")
as longitudes, is as follows:

![
haversin(\\frac{d}{r}) = haversin(\\phi\_{2} - \\phi\_{1}) + cos(\\phi\_{1}) cos(\\phi\_{2}) haversin(\\lambda\_{2} - \\lambda\_{1})
](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;%0Ahaversin%28%5Cfrac%7Bd%7D%7Br%7D%29%20%3D%20haversin%28%5Cphi_%7B2%7D%20-%20%5Cphi_%7B1%7D%29%20%2B%20cos%28%5Cphi_%7B1%7D%29%20cos%28%5Cphi_%7B2%7D%29%20haversin%28%5Clambda_%7B2%7D%20-%20%5Clambda_%7B1%7D%29%0A "
haversin(\frac{d}{r}) = haversin(\phi_{2} - \phi_{1}) + cos(\phi_{1}) cos(\phi_{2}) haversin(\lambda_{2} - \lambda_{1})
")

Otherwise, to find the distance
![d](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;d "d"),
we can perform the following calculation:

![
a = sin^2(\\frac{\\phi\_{2} - \\phi\_{1}}{2}) + cos(\\phi\_{1})cos(\\phi\_{2})sin^2(\\frac{\\lambda\_{2} - \\lambda\_{1}}{2})
](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;%0Aa%20%3D%20sin%5E2%28%5Cfrac%7B%5Cphi_%7B2%7D%20-%20%5Cphi_%7B1%7D%7D%7B2%7D%29%20%2B%20cos%28%5Cphi_%7B1%7D%29cos%28%5Cphi_%7B2%7D%29sin%5E2%28%5Cfrac%7B%5Clambda_%7B2%7D%20-%20%5Clambda_%7B1%7D%7D%7B2%7D%29%0A "
a = sin^2(\frac{\phi_{2} - \phi_{1}}{2}) + cos(\phi_{1})cos(\phi_{2})sin^2(\frac{\lambda_{2} - \lambda_{1}}{2})
")

![
d = r.(2. atan2(\\sqrt{a},\\sqrt{1-a}))
](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;%0Ad%20%3D%20r.%282.%20atan2%28%5Csqrt%7Ba%7D%2C%5Csqrt%7B1-a%7D%29%29%0A "
d = r.(2. atan2(\sqrt{a},\sqrt{1-a}))
")

Using the option `comb=True` in the `haversine` function, we create a
matrix of all possible combinations of one IATA airport code and one
NOAA weather station. We can derive the pairwise distances, and save
this matrix for archival purposes.

    # Calculating pairwise distances (haversine - not taking altitude into account)
    distances = pd.DataFrame(haversine_vector(airports.zipped.tolist(),df_stations.zipped.tolist(),Unit.MILES, comb=True))
    distances.columns = airports.iata.tolist()
    distances.index = df_stations.id.tolist()
    # Saving dataframes to .pkl file
    distances.to_pickle('distances.pkl')
    airports.to_pickle('airports.pkl')
    df_stations.to_pickle('df_stations.pkl')

## Step 3: Pre-Rendering Maps for All Airports

To speed up serving the interactive maps on our web application, we will
pre-render the `leaflet`-based interactive GIS maps using `folium`, save
them as `html` files, and load them on-demand later on.

Using `folium`, we can layout a topographical tileset as the base of the
map. A topological map makes sense for our purpose in finding which
station is most representative of climate and weather conditions, as we
can visually check for differences in altitude, or the presence of
geological features that can affect local climate conditions. Here we
use the open-source `Stamen Terrain` tileset.

    # Finding nearest 5 NOAA stations to input airport
    # Working example here is ORD - O'Hare International

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


    draw_top5_map("ORD")

![Example:
ORD](https://github.com/robert-mdh-bui/uge-airport-noaa-lookup/blob/main/assets/ORD_screenshot.png?raw=true)

Finally, we call the function in a `for` loop to pre-render for every
airport with an IATA code in the US and save all `html` files to the
`asset` folder, which will in turn be rendered in the `dash` app as an
`iframe`.

    # Pre-rendering all airports' top-5 map
    for x in range(0, len(airports)):
        inputx = str(airports.iloc[x]['iata'])
        filename = str("data_dash/prerenders/" + inputx + ".html")

        map_obj = draw_top5_map(inputx)
        map_obj.save(filename)

## Step 4: `Dash` Application & Deployment

Our `app.py` file instantiates a `flask` application through `dash`,
which allows the user to input a 3-letter IATA code into a text field,
which the application uses to look up within the pre-renders saved in
the `asset` folder. The corresponding `html` containing the `folium` map
is then rendered on the webpage as an `iframe`.

Should the user input a string of text that is not a 3-letter IATA code,
the `iframe` will return a 404 error, but does not crash the page. If a
correct code is then submitted, then the corresponding prerender would
appear.

The application is then deployed on Salesforce’s Heroku PaaS. Very
little additional requirements are needed aside from the two
prerequisite config files, which should be included in the `git`
repository:

-   `requirements.txt` contains all the necessary packages that the
    deployed app needs to function.

-   `Procfile` contains `web: gunicorn app:server`

    -   `web: gunicorn` initializes `gunicorn`, which serves the `flask`
        app for production.

    -   `app: server` calls `app.py` and refers specifically to the
        `server` object, itself instantiated by calling the `app.server`
        class/method in the script.

The deployed application can be found at
<https://uge-airport-noaa-lookup.herokuapp.com/>.
