import flet as ft
import requests
import pandas as pd
import pytz
from datetime import datetime
from flet import Page, Column, Row, Text, DataTable, DataColumn, DataCell, DataRow, UserControl, app

# Your Google Drive file ID
FILE_ID = '1-BldP2RQxfVXDa9hje7T3civXGVNpkzx'
FILE_URL = f'https://drive.google.com/uc?export=download&id={FILE_ID}'

class Dashboard(UserControl):
    def build(self):
        self.live_time = Text(size=20)
        self.strat_pnl_nifty_trend = Text()
        self.strat_pnl_nifty_scalp = Text()
        self.table = DataTable(
            columns=[
                DataColumn(label=Text("Strategy")),
                DataColumn(label=Text("Live Status")),
                DataColumn(label=Text("Symbol")),
                DataColumn(label=Text("Type")),
                DataColumn(label=Text("Price")),
                DataColumn(label=Text("Quantity")),
                DataColumn(label=Text("Stop Loss")),
                DataColumn(label=Text("Target")),
                DataColumn(label=Text("Order Time")),
                DataColumn(label=Text("Kite Token")),
                DataColumn(label=Text("Current LTP")),
                DataColumn(label=Text("PnL")),
            ]
        )

        return Column([
            Row([self.live_time], alignment='start'),
            Row([Text('Algroww Dashboard', size=30)], alignment='center'),
            self.table,
            Row([self.strat_pnl_nifty_trend], alignment='center'),
            Row([self.strat_pnl_nifty_scalp], alignment='center')
        ])

    def did_mount(self):
        self.update_dashboard()

    def update_dashboard(self):
        self.update_time()
        self.update_data()
        self.page.interval = 1000  # Update every 1 second

    def update_time(self):
        ist = pytz.timezone('Asia/Kolkata')
        current_time = datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S')
        self.live_time.value = f"Current IST Time: {current_time}"
        self.update()

    def update_data(self):
        df, strat_pnl_nifty_trend, strat_pnl_nifty_scalp = self.fetch_data()

        self.table.rows.clear()
        for _, row in df.iterrows():
            self.table.rows.append(DataRow(cells=[
                DataCell(Text(row['Strategy'])),
                DataCell(Text(str(row['Live Status']))),
                DataCell(Text(row['Symbol'])),
                DataCell(Text(row['Type'])),
                DataCell(Text(str(row['Price']))),
                DataCell(Text(str(row['Quantity']))),
                DataCell(Text(str(row['Stop Loss']))),
                DataCell(Text(str(row['Target']))),
                DataCell(Text(row['Order Time'])),
                DataCell(Text(row['Kite Token'])),
                DataCell(Text(str(row['Current LTP']))),
                DataCell(Text(str(row['PnL']))),
            ]))

        self.strat_pnl_nifty_trend.value = f'NIFTY Trend Strat PnL: {strat_pnl_nifty_trend}'
        self.strat_pnl_nifty_scalp.value = f'NIFTY Scalp Strat PnL: {strat_pnl_nifty_scalp}'
        self.update()

    def fetch_data(self):
        try:
            response = requests.get(FILE_URL)
            response.raise_for_status()  # Raise an error for bad status codes
            data = response.json()
            open_trades = []
            for strategy, trades in data['open_trades'].items():
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
                            'PnL': trade['PnL']  # Ensure 'PnL' key is handled safely
                        }
                        open_trades.append(trade_data)

            strat_pnl_nifty_trend = data['open_trades']['NIFTY_Trend']['Strat_PnL']
            strat_pnl_nifty_scalp = data['open_trades']['NIFTY_Scalp']['Strat_PnL']

            return pd.DataFrame(open_trades), strat_pnl_nifty_trend, strat_pnl_nifty_scalp
        except requests.RequestException as e:
            print(f"Error fetching data: {e}")
            return pd.DataFrame(), 0, 0  # Return empty DataFrame and zeroes in case of error

def main(page: Page):
    page.title = "Algroww Dashboard"
    page.horizontal_alignment = "center"
    page.vertical_alignment = "start"
    page.add(Dashboard())

app(target=main)
