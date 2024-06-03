from flask import Flask, render_template_string
import requests
import pandas as pd
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import json
import pytz
from datetime import datetime

# Create a Flask server
server = Flask(__name__)

# Your Google Drive file ID
FILE_ID = '1-BldP2RQxfVXDa9hje7T3civXGVNpkzx'
FILE_URL = f'https://drive.google.com/uc?export=download&id={FILE_ID}'

# Function to fetch and parse the JSON data
def fetch_data():
    try:
        response = requests.get(FILE_URL)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        open_trades = []
        for strategy, trades in data['open_trades'].items():
            # if trades != "Strat_PnL":
                for symbol, trade in trades.items():
                    if symbol != "Strat_PnL":
                        trade_data = {
                            'Strategy': strategy,
                            'Live Status': trade['live_stat'],
                            'Symbol': symbol,
                            'Type': trade['type'],
                            'Price': trade['ltp'],
                            'Quantity': trade['qty'],
                            'Stop Loss': trade['sl'],
                            'Target': trade['tgt'],
                            'Order Time': trade['order_time'],
                            'Kite Token': trade['kite_token'],
                            'Current LTP': trade['c_ltp'],
                            'PnL':trade['PnL']


                        }
                        open_trades.append(trade_data)
        return pd.DataFrame(open_trades)
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame()  # Return an empty DataFrame in case of error

# Function to get current IST time
def get_current_ist_time():
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S')

# Create a Dash app
app = dash.Dash(__name__, server=server, url_base_pathname='/dashboard/')

# Fetch initial data
initial_data = fetch_data()

app.layout = html.Div([
    html.Div(id='live-time', style={'position': 'absolute', 'top': '10px', 'left': '10px', 'fontSize': 20}),
    html.H1('Algroww Dashboard', style={'textAlign': 'center'}),
    dcc.Interval(
        id='interval-component',
        interval=1*1000,  # in milliseconds (60 seconds)
        n_intervals=0
    ),
    dcc.Interval(
        id='time-interval-component',
        interval=1000,  # in milliseconds (1 second)
        n_intervals=0
    ),
    dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in initial_data.columns],
        data=initial_data.to_dict('records')
    )
])

@app.callback(
    Output('table', 'data'),
    [Input('interval-component', 'n_intervals')]
)
def update_table(n):
    df = fetch_data()
    return df.to_dict('records')

@app.callback(
    Output('live-time', 'children'),
    [Input('time-interval-component', 'n_intervals')]
)
def update_time(n):
    return get_current_ist_time()

# Define a route for the Flask server
@server.route('/')
def index():
    return render_template_string('''
        <h1>Welcome to the Dashboard</h1>
        <p><a href="/dashboard/">Go to Dashboard</a></p>
    ''')

# Run the Flask server
if __name__ == '__main__':
    server.run(debug=True)
