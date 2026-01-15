# Simple Moving Average Crossover Strategy

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta


def calculate_sma(data, window):
    return data.rolling(window=window).mean()


def sma_crossover_strategy(symbol, short_window=50, long_window=200, period='1y'):
    stock = yf.Ticker(symbol)
    data = stock.history(period=period)
    
    if data.empty:
        print(f"No data available for {symbol}")
        return None
    
    data['SMA_Short'] = calculate_sma(data['Close'], short_window)
    data['SMA_Long'] = calculate_sma(data['Close'], long_window)
    
    data['Signal'] = 0
    data['Signal'][short_window:] = np.where(
        data['SMA_Short'][short_window:] > data['SMA_Long'][short_window:], 1, 0
    )
    
    data['Position'] = data['Signal'].diff()
    data['Returns'] = data['Close'].pct_change()
    data['Strategy_Returns'] = data['Returns'] * data['Signal'].shift(1)
    
    return data


def backtest_strategy(data, initial_capital=10000):
    if data is None or data.empty:
        return None
    
    data['Cumulative_Returns'] = (1 + data['Returns']).cumprod()
    data['Cumulative_Strategy'] = (1 + data['Strategy_Returns']).cumprod()
    data['Portfolio_Value'] = initial_capital * data['Cumulative_Strategy']
    
    total_return = (data['Portfolio_Value'].iloc[-1] / initial_capital - 1) * 100
    buy_hold_return = (data['Cumulative_Returns'].iloc[-1] - 1) * 100
    buy_signals = len(data[data['Position'] == 1])
    sell_signals = len(data[data['Position'] == -1])
    
    results = {
        'total_return': total_return,
        'buy_hold_return': buy_hold_return,
        'buy_signals': buy_signals,
        'sell_signals': sell_signals,
        'final_value': data['Portfolio_Value'].iloc[-1]
    }
    
    return results


if __name__ == "__main__":
    symbol = "AAPL"
    print(f"Running SMA Crossover Strategy for {symbol}...")
    
    data = sma_crossover_strategy(symbol, short_window=50, long_window=200)
    
    if data is not None:
        results = backtest_strategy(data)
        
        print("\n=== Backtest Results ===")
        print(f"Total Return: {results['total_return']:.2f}%")
        print(f"Buy & Hold Return: {results['buy_hold_return']:.2f}%")
        print(f"Buy Signals: {results['buy_signals']}")
        print(f"Sell Signals: {results['sell_signals']}")
        print(f"Final Portfolio Value: ${results['final_value']:.2f}")
        
        print("\n=== Recent Trading Signals ===")
        recent_signals = data[data['Position'] != 0].tail(10)
        print(recent_signals[['Close', 'SMA_Short', 'SMA_Long', 'Position']])
