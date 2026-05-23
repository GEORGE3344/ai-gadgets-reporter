# AI Gadget Reporter

A lightweight Python script that scrapes YouTube search results for the latest AI gadget features and produces a daily report.

## Requirements

Ensure you have the required dependencies installed:
```bash
pip install beautifulsoup4 requests schedule
```

## Running the Script

To run the script:
```bash
python report.py
```

The script will:
1. Run an initial check and print the top 3 AI gadget videos.
2. Schedule a daily run to execute at **10:00 PM** local time.
