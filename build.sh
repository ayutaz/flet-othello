#!/bin/bash

echo "Building Flet Othello Game..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Error: uv is not installed. Please install uv first."
    echo "Visit: https://github.com/astral-sh/uv"
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
uv pip install -r requirements.txt

# Build for web
echo "Building web version..."
flet build web \
    --project "Othello Game" \
    --description "A classic Othello game built with Flet"

echo "Build complete! Web files are in build/web/"
echo ""
echo "To run locally:"
echo "  cd build/web"
echo "  python -m http.server 8000"
echo ""
echo "Then open http://localhost:8000 in your browser"