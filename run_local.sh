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