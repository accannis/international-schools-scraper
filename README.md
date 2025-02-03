# Italy Schools Scraper

This project scrapes information about international schools in Italy from the International Schools Database website.

## Setup

1. Create a virtual environment (already done):
```bash
python3 -m venv venv
```

2. Activate the virtual environment:
```bash
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the scraper:
```bash
python scraper.py
```

The script will:
1. Use Selenium to automate browser interaction
2. Extract school information from all Italian cities
3. Save the results to a CSV file
