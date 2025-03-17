import pandas as pd
import os
import csv
import yfinance as yf
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DataHandler:
    def __init__(self):
        self.tickers_file = 'tickers.csv'  # Replace with your actual path

    def read_csv_data(self):
        if os.path.exists(self.tickers_file):
            with open(self.tickers_file, mode='r') as file:
                reader = csv.reader(file)
                return list(reader)
        else:
            with open(self.tickers_file, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Ticker"])  # Header row
            return []

    def fetch_tickers(self):
        try:
            data = self.read_csv_data()
            tickers = [row[0] for row in data[1:]]  # Skip header row
            if not tickers:
                logging.warning("Ticker list is empty. Add tickers to 'tickers.csv'.")
            logging.info(f"Fetched tickers: {tickers}")
            return tickers
        except FileNotFoundError:
            logging.warning(f"{self.tickers_file} not found. Creating a new one.")
            self.write_default_csv_headers()
            return []
        except Exception as e:
            logging.error(f"Error fetching tickers: {e}")
            return []
    
    def write_default_csv_headers(self):
        with open(self.tickers_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Ticker"])

    def fetch_data(self, ticker, interval, range_):
        try:
            data = yf.download(ticker, period=range_, interval=interval)
            logging.info(f"Fetched data for {ticker}: {data.head()}")
            return data[['Open', 'High', 'Low', 'Close', 'Volume']] 
        except Exception as e:
            logging.error(f"Error fetching data for {ticker}: {e}")
            return pd.DataFrame()  # Return an empty DataFrame on failure

    def update_ticker_data_in_csv(self, ticker, high_earnings, last_closing_price):
        try:
            df = pd.read_csv('top_10_tickers.csv')
            df.loc[df['Ticker'] == ticker, 'High Earnings'] = high_earnings
            df.loc[df['Ticker'] == ticker, 'Last Price'] = last_closing_price
            df.to_csv('top_10_tickers.csv', index=False)
            logging.info(f"Updated ticker data for {ticker}")
        except Exception as e:
            logging.error(f"Error updating data in CSV for {ticker}: {e}")
