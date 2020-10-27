#!/bin/sh

echo "Running all project files..."

if [ ! -d data ]; then
  sh get_files.sh
fi 
cd scripts/
python3 herald_crawler.py
python3 herald_cleaner.py
python3 stuff_crawler.py
python3 stuff_clean.py
echo "Sample Web Scraping and Data Cleaning complete for NZ Herald and stuff.co.nz"
echo "Now creating Economic Policy Uncertainty Index based on downloaded data"
python3 main.py
