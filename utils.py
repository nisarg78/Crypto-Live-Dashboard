import pandas as pd
import numpy as np

# --- Technical Indicators ---
def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calculate_macd(prices, span_short=12, span_long=26, span_signal=9):
    ema_short = prices.ewm(span=span_short, adjust=False).mean()
    ema_long = prices.ewm(span=span_long, adjust=False).mean()
    macd = ema_short - ema_long
    signal = macd.ewm(span=span_signal, adjust=False).mean()
    return macd, signal

def calculate_sma(prices, window=20):
    return prices.rolling(window=window).mean()

def calculate_ema(prices, span=20):
    return prices.ewm(span=span, adjust=False).mean()

def calculate_bollinger_bands(prices, window=20, num_std=2):
    sma = calculate_sma(prices, window)
    std = prices.rolling(window=window).std()
    upper_band = sma + (std * num_std)
    lower_band = sma - (std * num_std)
    return sma, upper_band, lower_band

def calculate_stochastic_oscillator(prices, window=14):
    low_min = prices.rolling(window=window).min()
    high_max = prices.rolling(window=window).max()
    k = 100 * (prices - low_min) / (high_max - low_min)
    return k
