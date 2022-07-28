import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

# Dash init
app = dash.Dash(__name__)

# Flask init
server = app.server

# App layout
app.layout = html.Div(
    [

        html.H2(
            children="Web App: Mapping US Airports Monthly Low Temps with NOAA Stations",
            style={
                'textAlign': 'center',
                'font_family': 'SourceSansProSemiBold'
            }
        ),

        dcc.Markdown(
            children='Created by [Robert Bui](https://github.com/robert-mdh-bui/uge-airport-noaa-lookup). \
            Licensed under [GNU General Public License 3.0](https://www.gnu.org/licenses/gpl-3.0.en.html)',
            style={
                'display': 'flex',
                'justifyContent': 'center'
            }
        ),
        dcc.Markdown(
            children='''
            This web app is derived from a project originally created for winter operations planning at \
            a major US legacy airline.
            ''',
            style={
                'display': 'flex',
                'justifyContent': 'center'
            }
        ),
        dcc.Markdown(
            children='''
            Data sources consist of publicly available information from [IATA](https://www.iata.org/en/publications/directories/code-search/)\
            and [NOAA](https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-daily).
            ''',
            style={
                'display': 'flex',
                'justifyContent': 'center'
            }
        ),
        dcc.Markdown(
            children='''
            Tools used:
            -   `folium`: Python wrapper for `JS.leaflet` to create interactive GIS maps.
            -   `dash`: Python package by `plotly` to implement interactive visualization.
            -   Miscellaneous: `pandas`, `airportsdata`, `haversine`.
            -   Deployed on Salesforce Heroku, powered by `dash` and `gunicorn.`''',
            style={
                'display': 'flex',
                'justifyContent': 'center'
            }
        ),

        html.Div(
            [

                # HTML div for input text box
                html.Div(
                    [
                        html.Div(
                            children="Input 3-Letter IATA Code (ALL CAPS - US airports only): ",
                            style={
                                'textAlign': 'center'
                            }
                        ),
                        dcc.Input(
                            id='textinput',
                            type='text',
                            value='ORD'
                        )
                    ],
                    style={
                        'display':'flex',
                        'justifyContent':'center'
                    }
                ),

                # HTML div for output map
                html.Div(
                    [
                        html.Iframe(
                            id="my-output",
                            src="assets/ORD.html",
                            style={
                                'height': '800px',
                                'width': '90%',
                                'margin-top': '20px',
                                'margin-left': '5%',
                                'margin-right': '5%'
                                #'display': 'flex',
                                #'justifyContent': 'center'
                            }
                        )
                    ]
                ),
                dcc.Markdown(
                    children='''
                    No proprietary information or data has been used in this app.
                    ''',
                    style={
                        'display': 'flex',
                        'justifyContent': 'center'
                    }
                )
            ]
        )
    ]
)


# Callback decorator for updating func
@app.callback(
    Output('my-output', 'src'),
    Input('textinput', 'value'),
    prevent_initial_call=True
)
def update_output_div(input_value):
    return f'assets/{input_value}.html'

# Check
if __name__ == '__main__':
    app.run_server(debug=True)
