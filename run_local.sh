#!/bin/bash

echo "Starting Data Chatbot Agent..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3 from https://www.python.org/downloads/"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies if requirements file exists
if [ -f "requirements_local.txt" ]; then
    echo "Installing dependencies..."
    pip install -r requirements_local.txt
fi

# Set API key (replace with your actual key if needed)
export OPENROUTER_API_KEY=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

# Start the application
echo ""
echo "Starting Data Chatbot Agent..."
echo "Your app will open in the browser at http://localhost:8501"
echo "Press Ctrl+C to stop the application"
echo ""
streamlit run app.py