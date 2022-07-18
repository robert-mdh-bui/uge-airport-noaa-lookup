import dash
import dash_core_components as dcc
from dash import html
from dash.dependencies import Input, Output

# Dash init
app = dash.Dash(__name__)

# Flask init
server = app.server

# App layout
app.layout = html.Div(
    [
        html.Iframe(
            id="my-output",
            src="assets/ORD.html",
            style={'height': '80%',
                   'width': '100%'}
        ),
        dcc.Input(
            id='textinput',
            placeholder='Enter 3-letter IATA code',
            type='text',
            value='ORD'
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
