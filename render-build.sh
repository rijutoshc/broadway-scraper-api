#!/bin/bash
# Update package list and install Chromium and ChromeDriver
apt-get update && apt-get install -y chromium chromium-driver

# Install Python dependencies
pip install -r requirements.txt
