#!/bin/bash

# Define the virtual environment name
VENV_NAME="smartgantry"

echo "Updating package list..."
sudo apt update

echo "Installing system dependencies..."
sudo apt install -y portaudio19-dev cmake python3-venv python3-pip

# Create and activate virtual environment
echo "Creating virtual environment: $VENV_NAME"
python3 -m venv $VENV_NAME

echo "Activating virtual environment..."
source $VENV_NAME/bin/activate

# Ensure pip is up to date
echo "Upgrading pip..."
pip install --upgrade pip

# Check if requirements.txt exists before installing
if [ -f "requirements.txt" ]; then
    echo "Installing Python dependencies from requirements.txt..."
    pip install -r requirements.txt
else
    echo "Error: requirements.txt file not found!"
    exit 1
fi

echo "Setup completed successfully!"
