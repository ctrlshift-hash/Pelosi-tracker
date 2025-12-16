# Nancy Pelosi Portfolio Tracker

A real-time tracker for Nancy Pelosi's stock portfolio and trading activity, similar to pelositracker.app.

## Features

- **Live Portfolio Data**: Real-time tracking of current holdings
- **Performance Metrics**: Track portfolio performance and total invested
- **Recent Trades**: Display recent trading activity
- **Auto-Refresh**: Automatically updates every 5 minutes
- **Clean UI**: Modern, responsive design similar to pelositracker.app

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open your browser and navigate to:
```
http://localhost:5000
```

## How It Works

The application scrapes live data from pelositracker.app and displays it in a clean, focused interface specifically for Nancy Pelosi's portfolio.

- **Backend**: Flask server that scrapes and caches portfolio data
- **Frontend**: HTML/CSS/JavaScript for displaying the data
- **Scraper**: BeautifulSoup-based scraper that extracts holdings, performance, and trades

## Data Sources

Data is sourced from publicly available financial disclosures (STOCK Act filings) via pelositracker.app.

## Notes

- Data updates automatically every 5 minutes
- All data is for informational purposes only
- Not affiliated with Nancy Pelosi or her office








