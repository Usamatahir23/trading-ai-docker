# CPU-optimized Docker image for Trading AI
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt* ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Install common trading libraries
RUN pip install --no-cache-dir \
    pandas \
    numpy \
    matplotlib \
    seaborn \
    scikit-learn \
    yfinance \
    ta \
    jupyter \
    notebook

# Copy application code
COPY . .

# Expose Jupyter port
EXPOSE 8888

# Default command
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]
