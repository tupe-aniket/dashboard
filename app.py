import requests
import pandas as pd
import pytz
from datetime import datetime
import threading
from flet import Page, Column, Row, Text, DataTable, app

# Your Google Drive file ID
FILE_ID = '1-BldP2RQxfVXDa9hje7T3civXGVNpkzx'
FILE_URL = f'https://drive.google.com/uc?export=download&id={FILE_ID}'

class Dashboard(Page):
    def __init__(self):
        super().__init__()
        self.live_time = Text(size=20)
        self.strat_pnl_nifty_trend = Text()
        self.strat_pnl_nifty_scalp = Text()
        self.table = DataTable(
            columns=[
                {"name": "Strategy", "id": "Strategy"},
                {"name": "Live Status", "id": "Live Status"},
                {"name": "Symbol", "id": "Symbol"},
                {"name": "Type", "id": "Type"},
                {"name": "Price", "id": "Price"},
                {"name": "Quantity", "id": "Quantity"},
                {"name": "Stop Loss", "id": "Stop Loss"},
                {"name": "Target", "id": "Target"},
                {"name": "Order Time", "id": "Order Time"},
                {"name": "Kite Token", "id": "Kite Token"},
                {"name": "Current LTP", "id": "Current LTP"},
                {"name": "PnL", "id": "PnL"},
            ],
            data=[]
        )
        self.add_children(
            Column([
                Row([self.live_time], alignment='start'),
                Row([Text('Algroww Dashboard', size=30)], alignment='center'),
                self.table,
                Row([self.strat_pnl_nifty_trend], alignment='center'),
                Row([self.strat_pnl_nifty_scalp], alignment='center')
            ])
        )

    def did_mount(self):
        # Start updating time and data on mount
        threading.Thread(target=self.update_loop, daemon=True).start()

    def update_loop(self):
        while True:
            try:
                self.update_time()
                self.update_data()
            except Exception as e:
                print(f"Error in update loop: {e}")

            # Update every 1 second
            threading.Event().wait(1)

    def update_time(self):
        ist = pytz.timezone('Asia/Kolkata')
        current_time = datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S')
        self.live_time.value = f"Current IST Time: {current_time}"

    def update_data(self):
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
                            'PnL': trade['PnL']
                        }
                        open_trades.append(trade_data)

            strat_pnl_nifty_trend = data['open_trades']['NIFTY_Trend']['Strat_PnL']
            strat_pnl_nifty_scalp = data['open_trades']['NIFTY_Scalp']['Strat_PnL']

            # Update table data
            self.table.data = open_trades

            # Update PnL values
            self.strat_pnl_nifty_trend.value = f'NIFTY Trend Strat PnL: {strat_pnl_nifty_trend}'
            self.strat_pnl_nifty_scalp.value = f'NIFTY Scalp Strat PnL: {strat_pnl_nifty_scalp}'

        except requests.RequestException as e:
            print(f"Error fetching data: {e}")

def main():
    page = Dashboard()
    page.title = "Algroww Dashboard"
    page.horizontal_alignment = "center"
    page.vertical_alignment = "start"
    return page


if __name__ == "__main__":
    app(target=main)
