# Trading AI Docker

A comprehensive Docker-based environment for algorithmic trading, machine learning, and backtesting strategies. This project provides both CPU and GPU-optimized Docker images with pre-configured tools for trading analysis.

## 🚀 Features

- **Dual Docker Images**: CPU and NVIDIA CUDA GPU variants
- **Pre-installed Libraries**: pandas, numpy, scikit-learn, yfinance, ta, jupyter, and more
- **Example Strategies**: Moving average crossover, LSTM price prediction, live trading bot template
- **Jupyter Notebooks**: Interactive tutorials for getting started, technical analysis, and backtesting
- **CI/CD Ready**: GitHub Actions workflow for automated Docker builds

## 📁 Project Structure

```
trading-ai-docker/
├── Dockerfile              # Main CPU-optimized image
├── Dockerfile.gpu          # NVIDIA CUDA variant
├── docker-compose.yml      # Multi-service setup
├── .github/
│   └── workflows/
│       └── docker-publish.yml  # Auto-build on push
├── examples/
│   ├── basic_strategy.py   # Simple moving average crossover
│   ├── ml_prediction.py    # LSTM price prediction
│   └── live_trading.py     # Real-time trading bot template
├── notebooks/
│   ├── 01_getting_started.ipynb
│   ├── 02_technical_analysis.ipynb
│   └── 03_backtesting.ipynb
└── README.md
```

## 🛠️ Quick Start

### Prerequisites

- Docker and Docker Compose installed
- (Optional) NVIDIA Docker runtime for GPU support

### Running with Docker Compose

**CPU Version:**
```bash
docker-compose up trading-ai-cpu
```

**GPU Version:**
```bash
docker-compose --profile gpu up trading-ai-gpu
```

The Jupyter notebook will be available at:
- CPU: http://localhost:8888
- GPU: http://localhost:8889

### Building Images Manually

**CPU Image:**
```bash
docker build -t trading-ai:latest -f Dockerfile .
```

**GPU Image:**
```bash
docker build -t trading-ai:gpu -f Dockerfile.gpu .
```

### Running Containers

**CPU:**
```bash
docker run -p 8888:8888 -v $(pwd)/examples:/app/examples -v $(pwd)/notebooks:/app/notebooks trading-ai:latest
```

**GPU:**
```bash
docker run --gpus all -p 8889:8888 -v $(pwd)/examples:/app/examples -v $(pwd)/notebooks:/app/notebooks trading-ai:gpu
```

## 📚 Examples

### Basic Strategy (Moving Average Crossover)

```bash
docker exec -it trading-ai-cpu python examples/basic_strategy.py
```

### ML Prediction (LSTM)

```bash
docker exec -it trading-ai-gpu python examples/ml_prediction.py
```

### Live Trading Bot

```bash
docker exec -it trading-ai-cpu python examples/live_trading.py
```

## 📓 Jupyter Notebooks

1. **01_getting_started.ipynb**: Introduction to fetching and analyzing stock data
2. **02_technical_analysis.ipynb**: Technical indicators (RSI, MACD, Bollinger Bands)
3. **03_backtesting.ipynb**: Strategy backtesting and performance metrics

Access notebooks through the Jupyter interface in your browser.

## 🔧 Configuration

### Environment Variables

- `JUPYTER_ENABLE_LAB`: Enable JupyterLab (default: yes)

### Volumes

The docker-compose setup mounts:
- `./examples` → `/app/examples`
- `./notebooks` → `/app/notebooks`
- `./data` → `/app/data` (create this directory for data persistence)

## 🤖 CI/CD

The GitHub Actions workflow automatically builds and publishes Docker images on:
- Push to main/master branch
- Tagged releases (v*)
- Pull requests (build only, no push)

Images are published to GitHub Container Registry (ghcr.io).

## 📦 Included Libraries

- **Data Analysis**: pandas, numpy
- **Visualization**: matplotlib, seaborn
- **Machine Learning**: scikit-learn, tensorflow, torch (GPU)
- **Trading**: yfinance, ta (Technical Analysis Library)
- **Development**: jupyter, notebook

## 🔐 Security Notes

- This is a development environment. Do not use in production without proper security hardening
- API keys and credentials should be stored securely (use environment variables or secrets management)
- The live trading example is a template - implement proper risk management before live trading

## 📝 License

This project is provided as-is for educational and development purposes.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## ⚠️ Disclaimer

This software is for educational purposes only. Trading involves risk, and past performance does not guarantee future results. Always do your own research and consider consulting with a financial advisor before making trading decisions.
