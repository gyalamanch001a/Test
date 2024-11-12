import pandas as pd
import numpy as np
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Indicators:
    def __init__(self):
        pass

    def calculate_rsi(self, data, window=14):
        """Calculate the Relative Strength Index (RSI) for a given DataFrame."""
        delta = data['Close'].diff(1)
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        data['RSI'] = rsi
        logging.info("RSI calculated")
        return data

    def calculate_macd(self, data):
        """ Calculate the MACD (Moving Average Convergence Divergence)
        and Signal Line. Parameters: stock_data (DataFrame): DataFrame 
        containing stock data with 'Close' prices. Returns: DataFrame: 
        DataFrame with added 'MACD' and 'Signal Line' columns. """ 
        short_ema = data['Close'].ewm(span=12, adjust=False).mean() 
        long_ema = data['Close'].ewm(span=26, adjust=False).mean() 
        data['MACD'] = short_ema - long_ema 
        data['Signal Line'] = data['MACD'].ewm(span=9, adjust=False).mean() 
        return data

    def calculate_sma(self, data, window=30):
        """Calculate the Simple Moving Average (SMA)."""
        data['SMA'] = data['Close'].rolling(window=window).mean()
        logging.info("SMA calculated")
        return data

    def calculate_ema(self, data, window=30):
        """Calculate the Exponential Moving Average (EMA)."""
        data['EMA'] = data['Close'].ewm(span=window, adjust=False).mean()
        logging.info("EMA calculated")
        return data
    def calculate_buy_sell_signals(data):
        data['Buy_Signal'] = np.nan
        data['Sell_Signal'] = np.nan
        # Define the condition for buy/sell
        for i in range(1, len(data)):
            if data['EMA20'].iloc[i] > data['EMA50'].iloc[i] and data['EMA20'].iloc[i-1] <= data['EMA50'].iloc[i-1]:
                 logging.info(f"Data Buy Signal: {data}")
                 data['Buy_Signal'].iloc[i] = data['Close'].iloc[i]
            elif data['EMA20'].iloc[i] < data['EMA50'].iloc[i] and data['EMA20'].iloc[i-1] >=data['EMA50'].iloc[i-1]:
                 logging.info(f"Data sell singnal: {data}")
                 data['Sell_Signal'].iloc[i] = data['Close'].iloc[i]

            data['Buy Signal'] = data['Close'] > data['Close'].shift(1)  # Example: Buy signal if close price is higher than previous
            data['Sell Signal'] = data['Close'] < data['Close'].shift(1)  # Example: Sell signal if close price is lower than previous
            
        return data
        pass

    def calculate_bollinger_bands(self, data, window=20, num_std_dev=2):
        """Calculate Bollinger Bands."""
        data['SMA'] = data['Close'].rolling(window=window).mean()
        data['Upper Band'] = data['SMA'] + (data['Close'].rolling(window=window).std() * num_std_dev)
        data['Lower Band'] = data['SMA'] - (data['Close'].rolling(window=window).std() * num_std_dev)
        logging.info("Bollinger Bands calculated")
        return data
    def simple_moving_average(self, series, window=20):
        return series.rolling(window=window).mean()

    def exponential_moving_average(self, series, span=20):
        return series.ewm(span=span, adjust=False).mean()

    def relative_strength_index(self, series, period=14):
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def bollinger_bands(self, series, window=20, num_std_dev=2):
        sma = self.simple_moving_average(series, window)
        rolling_std = series.rolling(window).std()
        upper_band = sma + (rolling_std * num_std_dev)
        lower_band = sma - (rolling_std * num_std_dev)
        return upper_band, lower_band

    def macd(self, series):
        ema_12 = self.exponential_moving_average(series, 12)
        ema_26 = self.exponential_moving_average(series, 26)
        return ema_12 - ema_26

    def stochastic_oscillator(self, series, k_window=14, d_window=3):
        min_low = series.rolling(window=k_window).min()
        max_high = series.rolling(window=k_window).max()
        k = 100 * (series - min_low) / (max_high - min_low)
        d = k.rolling(window=d_window).mean()
        return k, d

    def average_true_range(self, data, window=14):
        high_low = data['High'] - data['Low']
        high_close = (data['High'] - data['Close'].shift()).abs()
        low_close = (data['Low'] - data['Close'].shift()).abs()
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        return tr.rolling(window).mean()

    def average_directional_index(self, data, window=14):
        # Implement ADX calculation here
        pass