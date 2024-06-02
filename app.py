from flask import Flask, jsonify, render_template_string
import requests
import pandas as pd
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import json

# Create a Flask server
server = Flask(__name__)

# Your Google Drive file ID
FILE_ID = '1-BldP2RQxfVXDa9hje7T3civXGVNpkzx'
FILE_URL = f'https://drive.google.com/uc?export=download&id={FILE_ID}'

# Function to fetch and parse the JSON data
def fetch_data():
    response = requests.get(FILE_URL)
    data = response.json()
    open_trades = []
    for strategy, trades in data['open_trades'].items():
        for symbol, trade in trades.items():
            trade_data = {
                'Strategy': strategy,
                'Symbol': symbol,
                'LTP': trade['ltp'],
                'Quantity': trade['qty'],
                'Live Status': trade['live_stat'],
                'Kite Token': trade['kite_token'],
                'Stop Loss': trade['sl'],
                'Target': trade['tgt'],
                'Type': trade['type'],
                'Order Time': trade['order_time'],
                'Current LTP': trade['c_ltp']
            }
            open_trades.append(trade_data)
    return pd.DataFrame(open_trades)

# Create a Dash app
app = dash.Dash(__name__, server=server, url_base_pathname='/dashboard/')

app.layout = html.Div([
    html.H1('Dashboard'),
    dcc.Interval(
        id='interval-component',
        interval=60*1000,  # in milliseconds (60 seconds)
        n_intervals=0
    ),
    dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in fetch_data().columns],
        data=fetch_data().to_dict('records')
    )
])

@app.callback(
    Output('table', 'data'),
    [Input('interval-component', 'n_intervals')]
)
def update_table(n):
    df = fetch_data()
    return df.to_dict('records')

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
