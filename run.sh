#!/bin/bash

echo "Starting Flet Othello Game..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Error: uv is not installed. Please install uv first."
    echo "Visit: https://github.com/astral-sh/uv"
    exit 1
fi

# Check if flet is installed
if ! uv pip list | grep -q flet; then
    echo "Installing dependencies..."
    uv pip install -r requirements.txt
fi

# Run the application
echo "Starting the game..."
flet run src/main.py