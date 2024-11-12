import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from data_handler import DataHandler
from plotter import StockPlotter
from indicators import Indicators
import yfinance as yf
#from nltk.sentiment.vader import SentimentIntensityAnalyzer
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
#from sklearn.ensemble import RandomForestRegressor

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class StockApp:
    def __init__(self, master):
        self.master = master
        self.master.geometry("800x600")
        self.data_handler = DataHandler()
        self.indicators = Indicators()

        # Create a Canvas for scrolling
        self.canvas = tk.Canvas(self.master)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create a Scrollbar
        self.scrollbar = tk.Scrollbar(self.master, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure the canvas to work with the scrollbar
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Create a frame inside the canvas
        self.frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.frame, anchor='nw')

        # Create PanedWindow for resizable left and plot frames
        self.paned_window = tk.PanedWindow(self.frame, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # Create left frame with specified dimensions and add to PanedWindow
        self.left_frame = tk.Frame(self.paned_window, width=1000, height=1400)  # Set dimensions here
        self.paned_window.add(self.left_frame, stretch="always")  # Makes it resize with window adjustments
        self.paned_window.paneconfigure(self.left_frame, minsize=200)  # Minimum width for left pane

        # Create plot frame and add to PanedWindow with resizable properties
        self.plot_frame = tk.Frame(self.paned_window, bg="white" , width=800, height=650)
        self.paned_window.add(self.plot_frame)

        # Configure the minimum size for the plot area
        self.paned_window.paneconfigure(self.plot_frame, minsize=800)  # Minimum size for plot area

        # Initialize plotter with the plot_frame
        self.plotter = StockPlotter(self.plot_frame)
        self.selected_indicators = []
        self.indicator_vars = {}
        self.setup_gui()

        # Update scroll region
        self.frame.bind("<Configure>", self.on_frame_configure)

    def setup_gui(self):
        self.create_left_frame()
        self.create_plot_frame()  # Ensure to call this to create the plot frame
        self.load_tickers()

    def on_frame_configure(self, event):
        # Update the scroll region of the canvas to encompass the frame
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def create_left_frame(self):
        # Ticker Label and Entry
        ticker_label = tk.Label(self.left_frame, text="Ticker Symbol:")
        ticker_label.grid(row=0, column=0, padx=5, pady=5, sticky='W')
        self.ticker_entry = tk.Entry(self.left_frame)
        self.ticker_entry.grid(row=0, column=1, padx=5, pady=5)

        # Range selection
        self.range_var = tk.StringVar(value="1d")
        range_label = tk.Label(self.left_frame, text="Range:")
        range_label.grid(row=1, column=0, padx=5, pady=5, sticky='W')
        self.range_entry = ttk.Combobox(self.left_frame, textvariable=self.range_var,
                                        values=["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "ytd", "max"])
        self.range_entry.grid(row=1, column=1, padx=5, pady=5)

        # Interval selection
        self.interval_var = tk.StringVar(value="5m")
        interval_label = tk.Label(self.left_frame, text="Interval:")
        interval_label.grid(row=2, column=0, padx=5, pady=5, sticky='W')
        self.interval_entry = ttk.Combobox(self.left_frame, textvariable=self.interval_var,
                                           values=["1m", "2m", "5m", "15m", "30m", "1h", "1d"])
        self.interval_entry.grid(row=2, column=1, padx=5, pady=5)

        # Hours ahead
        self.hours_ahead_var = tk.StringVar(value='24')
        hours_ahead_label = tk.Label(self.left_frame, text="Hours Ahead:")
        hours_ahead_label.grid(row=3, column=0, padx=5, pady=5, sticky='W')
        self.hours_ahead_entry = tk.Entry(self.left_frame, textvariable=self.hours_ahead_var)
        self.hours_ahead_entry.grid(row=3, column=1, padx=5, pady=5)

        # Button for indicator selection
        indicator_button = tk.Button(self.left_frame, text="Select Indicators", command=self.open_indicators)
        indicator_button.grid(row=4, column=0, padx=5, pady=5)

        # Settings icon
        settings_icon = ImageTk.PhotoImage(Image.open(r"C:\users\chant\Downloads\settings.png").resize((10, 10)))

        # Settings button with grid() now
        settings_button = tk.Button(self.left_frame, text="Settings", image=settings_icon, command=self.open_settings)
        settings_button.grid(row=0, column=2, padx=1, pady=0, sticky='ne')  # top-right corner

        # Update Button
        update_button = tk.Button(self.left_frame, text="Update", 
                                command=lambda: self.update_predictions(self.ticker_entry.get(), self.selected_indicators))
        update_button.grid(row=5, column=0, padx=5, pady=5)

        # Refresh Tickers Button
        refresh_button = tk.Button(self.left_frame, text="Refresh Tickers", command=self.load_tickers)
        refresh_button.grid(row=6, column=0, columnspan=2, pady=5)

        # Result labels
        self.result_label = tk.Label(self.left_frame, text="")
        self.result_label.grid(row=7, columnspan=2, pady=5)

        # Ticker Treeview
        self.ticker_treeview = ttk.Treeview(self.left_frame, columns=("Ticker"), show='headings')
        self.ticker_treeview.heading("Ticker", text="Ticker")

        # Add a scrollbar
        scrollbar = ttk.Scrollbar(self.left_frame, orient=tk.VERTICAL, command=self.ticker_treeview.yview)
        scrollbar.grid(row=10, column=2, sticky='ns')
        self.ticker_treeview.configure(yscroll=scrollbar.set)

        # Set up treeview to allow selection
        self.ticker_treeview.grid(row=10, column=0, columnspan=2, sticky='nsew')

        # Bind double-click event to load ticker
        self.ticker_treeview.bind("<Double-1>", self.load_ticker_to_entry)

        # Configure grid weights for resizing
        self.left_frame.grid_rowconfigure(10, weight=1)
        self.left_frame.grid_columnconfigure(1, weight=1)

    def load_tickers(self):
        tickers = self.data_handler.fetch_tickers()
        logging.info(f"Loaded tickers: {tickers}")

        # Clear existing tickers in the treeview
        for item in self.ticker_treeview.get_children():
            self.ticker_treeview.delete(item)

        # Populate the Treeview with tickers
        for ticker in tickers:
            self.ticker_treeview.insert('', 'end', values=(ticker,))

    def load_ticker_to_entry(self, event):
        selected_item = self.ticker_treeview.selection()
        if selected_item:
            ticker = self.ticker_treeview.item(selected_item)["values"][0]
            self.ticker_entry.delete(0, tk.END)
            self.ticker_entry.insert(0, ticker)

            # Fetch stock data based on the selected ticker, interval, and range
            interval = self.interval_var.get()
            range_ = self.range_var.get()
            data = self.data_handler.fetch_data(ticker, interval, range_)

            # Call plot_stock_data_with_ladders with actual stock data and selected indicators
            self.plotter.plot_stock_data_with_ladders(data, self.selected_indicators)

    def create_plot_frame(self):
        self.plot_frame = tk.Frame(self.paned_window)
        self.paned_window.add(self.plot_frame)
        self.paned_window.paneconfigure(self.plot_frame, minsize=560)
    
    def open_indicators(self):
        # Function to open the indicator selection window
        indicator_window = tk.Toplevel(self.master)
        indicator_window.title("Select Indicators")
        indicator_window.geometry("400x500")  # Increased height to fit new indicators

        tk.Label(indicator_window, text="Select Indicators:").pack(pady=10)

        # Updated list of indicators
        indicators = {
            "SMA": "Simple Moving Average (SMA)",
            "EMA": "Exponential Moving Average (EMA)",
            "RSI": "Relative Strength Index (RSI)",
            "Bollinger Bands": "Volatility with upper and lower bands around a moving average",
            "MACD": "Moving Average Convergence Divergence (MACD)",
            "Stochastic": "Stochastic Oscillator",
            "ATR": "Average True Range",
            "ADX": "Average Directional Index"
        }

        # Create checkboxes for each indicator
        for indicator in indicators:
            var = tk.BooleanVar(value=False)
            self.indicator_vars[indicator] = var
            checkbox = tk.Checkbutton(indicator_window, text=indicators[indicator], variable=var, command=self.check_selected_indicators)
            checkbox.pack(anchor='w')

        # Apply button to confirm selection
        self.apply_button = tk.Button(indicator_window, text="Apply", command=lambda: self.apply_and_close(indicator_window), state='disabled')
        self.apply_button.pack(pady=10)

    def apply_and_close(self, window):
         self.update_selected_indicators()
         window.destroy()

    def open_settings(self):
        # Example method to open settings window
        settings_window = tk.Toplevel(self.master)
        settings_window.title("Settings")
        settings_window.geometry("300x300")

        tk.Label(settings_window, text="Settings options go here").pack(pady=10)
        
        # Add more widgets for your settings as needed
        apply_button = tk.Button(settings_window, text="Apply", command=self.apply_settings)
        apply_button.pack(pady=20)

    def check_selected_indicators(self):
        # Check if any indicators are selected to enable the Apply button
        if any(var.get() for var in self.indicator_vars.values()):
            self.apply_button.config(state='normal')
        else:
            self.apply_button.config(state='disabled')

    def update_selected_indicators(self):
        self.selected_indicators = [indicator for indicator, var in self.indicator_vars.items() if var.get()]
        logging.info(f"Selected Indicators: {self.selected_indicators}")

        # Fetch the ticker from the entry field
        ticker = self.ticker_entry.get()

        # Update predictions with the selected indicators
        self.update_predictions(ticker, self.selected_indicators)

    def update_predictions(self, ticker, indicators):
        # Fetch stock data
        data = self.data_handler.fetch_data(ticker, self.interval_var.get(), self.range_var.get())
        
        if data is not None:
            # Apply indicators
            if "SMA" in indicators:
                data['SMA'] = self.indicators.simple_moving_average(data['Close'])
            if "EMA" in indicators:
                #data['EMA'] = self.indicators.exponential_moving_average(data['Close'])
                data['EMA20'] = data['Close'].ewm(span=20, adjust=False).mean()
                data['EMA50'] = data['Close'].ewm(span=50, adjust=False).mean()
                data = self.indicators.calculate_buy_sell_signals(data)  # Call the buy/sell signal calculation
            if "RSI" in indicators:
                data['RSI'] = self.indicators.relative_strength_index(data['Close'])
            if "Bollinger Bands" in indicators:
                data[['Upper Band', 'Lower Band']] = self.indicators.bollinger_bands(data['Close'])
            if "MACD" in indicators:
                data = self.indicators.calculate_macd(data)
            if "Stochastic" in indicators:
                data['Stochastic'] = self.indicators.stochastic_oscillator(data['Close'])
            if "ATR" in indicators:
                data['ATR'] = self.indicators.average_true_range(data)
            if "ADX" in indicators:
                data['ADX'] = self.indicators.average_directional_index(data)

            # Plot the updated data
            self.plotter.plot_stock_data_with_ladders(data, indicators)
            self.result_label.config(text=f"Predictions updated for {ticker} with indicators: {', '.join(indicators)}")
        else:
            messagebox.showerror("Data Fetch Error", "Could not fetch data for the selected ticker.")

