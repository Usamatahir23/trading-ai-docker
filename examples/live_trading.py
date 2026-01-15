# Real-time Trading Bot Template

import time
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    print("Warning: yfinance not available. Install with: pip install yfinance")


class TradingBot:
    def __init__(self, symbol, initial_capital=10000, position_size=0.1):
        self.symbol = symbol
        self.capital = initial_capital
        self.position_size = position_size
        self.position = 0
        self.entry_price = 0
        self.trades = []
        self.portfolio_value = initial_capital
        
    def get_latest_data(self, period='1d', interval='1m'):
        if not YFINANCE_AVAILABLE:
            print("yfinance not available")
            return None
        
        try:
            ticker = yf.Ticker(self.symbol)
            data = ticker.history(period=period, interval=interval)
            return data
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None
    
    def calculate_indicators(self, data):
        if data is None or len(data) < 20:
            return None
        
        close = data['Close']
        
        indicators = {
            'sma_20': close.rolling(20).mean().iloc[-1],
            'sma_50': close.rolling(50).mean().iloc[-1] if len(data) >= 50 else None,
            'rsi': self.calculate_rsi(close, 14),
            'current_price': close.iloc[-1],
            'volume': data['Volume'].iloc[-1]
        }
        
        return indicators
    
    def calculate_rsi(self, prices, period=14):
        if len(prices) < period + 1:
            return None
        
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1]
    
    def generate_signal(self, indicators):
        if indicators is None:
            return 'HOLD'
        
        signal = 'HOLD'
        price = indicators['current_price']
        sma_20 = indicators['sma_20']
        rsi = indicators['rsi']
        
        if self.position == 0:
            if sma_20 and price > sma_20 and rsi and rsi < 70:
                signal = 'BUY'
        elif self.position == 1:
            if rsi and rsi > 70 or (sma_20 and price < sma_20):
                signal = 'SELL'
        
        return signal
    
    def execute_trade(self, signal, price):
        if signal == 'BUY' and self.position == 0:
            self.position = 1
            self.entry_price = price
            trade_amount = self.capital * self.position_size
            shares = trade_amount / price
            self.capital -= trade_amount
            
            trade = {
                'timestamp': datetime.now(),
                'action': 'BUY',
                'price': price,
                'shares': shares,
                'amount': trade_amount
            }
            self.trades.append(trade)
            print(f"[BUY] {shares:.2f} shares @ ${price:.2f}")
            
        elif signal == 'SELL' and self.position == 1:
            trade = self.trades[-1] if self.trades else None
            if trade:
                shares = trade['shares']
                proceeds = shares * price
                profit = proceeds - trade['amount']
                self.capital += proceeds
                self.position = 0
                
                trade_record = {
                    'timestamp': datetime.now(),
                    'action': 'SELL',
                    'price': price,
                    'shares': shares,
                    'amount': proceeds,
                    'profit': profit,
                    'profit_pct': (profit / trade['amount']) * 100
                }
                self.trades.append(trade_record)
                print(f"[SELL] {shares:.2f} shares @ ${price:.2f} | Profit: ${profit:.2f} ({trade_record['profit_pct']:.2f}%)")
    
    def update_portfolio_value(self, current_price):
        if self.position == 1 and self.trades:
            last_trade = self.trades[-1]
            if last_trade['action'] == 'BUY':
                shares = last_trade['shares']
                position_value = shares * current_price
                self.portfolio_value = self.capital + position_value
            else:
                self.portfolio_value = self.capital
        else:
            self.portfolio_value = self.capital
    
    def run(self, interval=60, max_iterations=None):
        print(f"Starting trading bot for {self.symbol}")
        print(f"Initial capital: ${self.capital:.2f}")
        print(f"Position size: {self.position_size * 100}%")
        print(f"Update interval: {interval} seconds")
        print("-" * 50)
        
        iteration = 0
        
        try:
            while max_iterations is None or iteration < max_iterations:
                data = self.get_latest_data(period='1d', interval='5m')
                
                if data is not None and len(data) > 0:
                    indicators = self.calculate_indicators(data)
                    
                    if indicators:
                        current_price = indicators['current_price']
                        signal = self.generate_signal(indicators)
                        
                        if signal in ['BUY', 'SELL']:
                            self.execute_trade(signal, current_price)
                        
                        self.update_portfolio_value(current_price)
                        
                        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
                        print(f"Price: ${current_price:.2f} | Signal: {signal} | Position: {self.position}")
                        print(f"Portfolio Value: ${self.portfolio_value:.2f}")
                        if indicators['rsi']:
                            print(f"RSI: {indicators['rsi']:.2f}")
                        print("-" * 50)
                
                time.sleep(interval)
                iteration += 1
                
        except KeyboardInterrupt:
            print("\n\nTrading bot stopped by user")
            self.print_summary()
    
    def print_summary(self):
        print("\n" + "=" * 50)
        print("TRADING SUMMARY")
        print("=" * 50)
        print(f"Final Portfolio Value: ${self.portfolio_value:.2f}")
        print(f"Total Return: ${self.portfolio_value - 10000:.2f} ({(self.portfolio_value / 10000 - 1) * 100:.2f}%)")
        print(f"Total Trades: {len([t for t in self.trades if t['action'] == 'BUY'])}")
        
        completed_trades = [t for t in self.trades if 'profit' in t]
        if completed_trades:
            total_profit = sum(t['profit'] for t in completed_trades)
            avg_profit = total_profit / len(completed_trades)
            print(f"Completed Trades: {len(completed_trades)}")
            print(f"Total Profit: ${total_profit:.2f}")
            print(f"Average Profit per Trade: ${avg_profit:.2f}")


if __name__ == "__main__":
    if not YFINANCE_AVAILABLE:
        print("Please install yfinance: pip install yfinance")
    else:
        bot = TradingBot(symbol='AAPL', initial_capital=10000, position_size=0.1)
        bot.run(interval=60, max_iterations=5)
