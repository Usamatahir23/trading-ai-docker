# LSTM Price Prediction Model

import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

try:
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from tensorflow.keras.optimizers import Adam
    TENSORFLOW_AVAILABLE = True
except ImportError:
    try:
        from keras.models import Sequential
        from keras.layers import LSTM, Dense, Dropout
        from keras.optimizers import Adam
        TENSORFLOW_AVAILABLE = True
    except ImportError:
        TENSORFLOW_AVAILABLE = False
        print("Warning: TensorFlow/Keras not available. Install with: pip install tensorflow")


def prepare_data(data, lookback=60):
    prices = data['Close'].values.reshape(-1, 1)
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_prices = scaler.fit_transform(prices)
    
    X, y = [], []
    for i in range(lookback, len(scaled_prices)):
        X.append(scaled_prices[i-lookback:i, 0])
        y.append(scaled_prices[i, 0])
    
    X, y = np.array(X), np.array(y)
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))
    
    return X, y, scaler


def build_lstm_model(input_shape, units=50, dropout=0.2):
    if not TENSORFLOW_AVAILABLE:
        raise ImportError("TensorFlow/Keras is required for LSTM model")
    
    model = Sequential([
        LSTM(units=units, return_sequences=True, input_shape=input_shape),
        Dropout(dropout),
        LSTM(units=units, return_sequences=True),
        Dropout(dropout),
        LSTM(units=units),
        Dropout(dropout),
        Dense(units=1)
    ])
    
    model.compile(optimizer=Adam(learning_rate=0.001), loss='mean_squared_error')
    return model


def train_model(symbol, period='2y', lookback=60, epochs=50, batch_size=32):
    if not TENSORFLOW_AVAILABLE:
        print("TensorFlow/Keras not available. Cannot train model.")
        return None, None, None, None
    
    print(f"Downloading data for {symbol}...")
    stock = yf.Ticker(symbol)
    data = stock.history(period=period)
    
    if data.empty:
        print(f"No data available for {symbol}")
        return None, None, None, None
    
    print("Preparing data...")
    X, y, scaler = prepare_data(data, lookback)
    
    split = int(len(X) * 0.8)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]
    
    print("Building and training model...")
    model = build_lstm_model((X_train.shape[1], 1))
    
    history = model.fit(
        X_train, y_train,
        epochs=epochs,
        batch_size=batch_size,
        validation_data=(X_test, y_test),
        verbose=1
    )
    
    print("Making predictions...")
    train_predictions = model.predict(X_train)
    test_predictions = model.predict(X_test)
    
    train_predictions = scaler.inverse_transform(train_predictions)
    test_predictions = scaler.inverse_transform(test_predictions)
    y_train_actual = scaler.inverse_transform(y_train.reshape(-1, 1))
    y_test_actual = scaler.inverse_transform(y_test.reshape(-1, 1))
    
    train_rmse = np.sqrt(mean_squared_error(y_train_actual, train_predictions))
    test_rmse = np.sqrt(mean_squared_error(y_test_actual, test_predictions))
    test_mae = mean_absolute_error(y_test_actual, test_predictions)
    
    print(f"\n=== Model Performance ===")
    print(f"Train RMSE: ${train_rmse:.2f}")
    print(f"Test RMSE: ${test_rmse:.2f}")
    print(f"Test MAE: ${test_mae:.2f}")
    
    return model, scaler, history, {
        'train_predictions': train_predictions,
        'test_predictions': test_predictions,
        'train_actual': y_train_actual,
        'test_actual': y_test_actual,
        'test_rmse': test_rmse,
        'test_mae': test_mae
    }


def predict_next_days(model, scaler, data, lookback=60, days=5):
    if not TENSORFLOW_AVAILABLE:
        return None
    
    prices = data['Close'].values[-lookback:].reshape(-1, 1)
    scaled_prices = scaler.transform(prices)
    
    predictions = []
    current_sequence = scaled_prices.flatten()
    
    for _ in range(days):
        X_input = current_sequence[-lookback:].reshape(1, lookback, 1)
        next_pred = model.predict(X_input, verbose=0)
        predictions.append(scaler.inverse_transform(next_pred)[0, 0])
        current_sequence = np.append(current_sequence, next_pred[0, 0])
    
    return predictions


if __name__ == "__main__":
    if not TENSORFLOW_AVAILABLE:
        print("Please install TensorFlow: pip install tensorflow")
    else:
        symbol = "AAPL"
        print(f"Training LSTM model for {symbol}...")
        
        model, scaler, history, results = train_model(
            symbol, period='2y', lookback=60, epochs=20, batch_size=32
        )
        
        if model is not None:
            stock = yf.Ticker(symbol)
            recent_data = stock.history(period='1y')
            
            print("\n=== Predicting Next 5 Days ===")
            predictions = predict_next_days(model, scaler, recent_data, days=5)
            if predictions:
                for i, pred in enumerate(predictions, 1):
                    print(f"Day {i}: ${pred:.2f}")
