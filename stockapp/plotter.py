import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import pandas as pd
import logging
import mplfinance as mpf
import numpy as np
import tkinter as tk

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class StockPlotter:
    def __init__(self, parent):
        self.parent = parent
        pass
    def plot_stock_data(self, data):
        try:
            plt.clf()  # Clear the current figure
            plt.plot(data['Close'], label='Close Price')
            plt.title("Stock Price")
            plt.xlabel("Date")
            plt.ylabel("Price")
            plt.legend()
            plt.grid()
            self.draw()
            logging.info("Stock data plotted successfully.")
        except Exception as e:
            logging.error(f"Error plotting stock data: {e}")
    def clean_stock_data(self, stock_data):
        # Flatten multi-level column headers if they exist
        if isinstance(stock_data.columns, pd.MultiIndex):
            stock_data.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col for col in stock_data.columns]

        # Check column data type before applying pd.to_numeric
        for col in stock_data.columns:
            if stock_data[col].dtype in [object, 'O', 'str']:  # Only try converting object or string types
                stock_data[col] = pd.to_numeric(stock_data[col], errors='coerce')
            else:
                print(f"Skipping conversion for column '{col}' of type {stock_data[col].dtype}")

        return stock_data

    def plot_stock_data_with_ladders(self, stock_data, indicators):
        # Ensure all columns are numeric and handle NaN values
        stock_data_renamed = stock_data.rename(columns={
            'Open_AOS': 'Open',
            'High_AOS': 'High',
            'Low_AOS': 'Low',
            'Close_AOS': 'Close',
            'Volume_AOS': 'Volume'
        })

        # Convert columns to numeric and handle NaN values
        stock_data_renamed[['Open', 'High', 'Low', 'Close', 'Volume']] = (
            stock_data_renamed[['Open', 'High', 'Low', 'Close', 'Volume']]
            .apply(pd.to_numeric, errors='coerce')
        )
        stock_data_renamed = stock_data_renamed.ffill()
        #stock_data_renamed.fillna(method='ffill', inplace=True)

        # Plot the data
        fig, axes = mpf.plot(
            stock_data_renamed,
            type='candle',
            volume=True,
            style='charles',
            addplot=indicators,
            returnfig=True
        )
        return fig, axes
    def draw(self):
        plt.tight_layout()
        self.canvas = FigureCanvasTkAgg(plt.gcf(), master=self.parent)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
