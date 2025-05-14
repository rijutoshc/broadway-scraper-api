#!/usr/bin/env bash

apt-get update
apt-get install -y chromium

# Verify install
chromium --version || echo "Chromium not installed"


