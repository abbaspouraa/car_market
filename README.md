# Car Market Deal Finder (FB Marketplace)

A Python/Selenium tool that scans Facebook Marketplace for predefined truck models/price ranges, stores results, and emails you when new “good value” listings appear.

## Features

- Headless Chrome scraping with Selenium and smart waits.

- De-dupe + “sold/removed” detection to avoid stale alerts.

- Simple pricing heuristics via model rules.

- Email alerts using a templated HTML email.

- Optional shell script + cron for scheduling.

## Repo layout

- main.py – entrypoint; orchestrates search → parse → notify. 

- google_chrom_driver.py – browser/session setup (Chrome/Chromedriver). 

- db_process.py – persistence, de-dupe, and “already seen/sold” tracking. 

- model_price.py – model → target price rules/heuristics. 

- identify_sold.py – flags sold/removed items. 

- send_email.py, gmail_script.py, email_template.html – alerting pipeline. 

- requirements.txt – Python deps. data_collection.sh – convenience runner. 

## Quick start

1- Prereqs

  - Python 3.10+ (recommended)

  - Google Chrome + matching ChromeDriver on PATH

  - A sender email (Gmail works best with an App Password)

2- Setup
```bash
git clone https://github.com/abbaspouraa/car_market.git
cd car_market
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3- Config
Create .env in the project root (example below).
If you prefer not to use a .env, export the variables in your shell or hard-code a simple config.py.

```env
# Search parameters
FB_SEARCH_QUERY="tacoma, tundra, f150"
FB_LOCATION="Toronto, ON"
FB_RADIUS_KM=250
MIN_PRICE=3000
MAX_PRICE=25000

# Email (use an app password for Gmail)
ALERT_TO="me@example.com"
ALERT_FROM="me@example.com"
SMTP_HOST="smtp.gmail.com"
SMTP_PORT=587
SMTP_USER="me@example.com"
SMTP_PASS="your_app_password"

# Storage (pick one approach used in db_process.py)
DB_URL="sqlite:///car_market.db"
# or for local file-based sqlite: DB_PATH="./car_market.db"
```

4- Run it

```bash
python main.py
# or
bash data_collection.sh
```

5- Cron (optional)
```bash
# Run every 30 minutes
*/30 * * * * /usr/bin/bash /path/to/repo/data_collection.sh >> /var/log/car_market.log 2>&1
```
## Tuning “good value”

- Update thresholds in model_price.py (e.g., by year/trim/mileage).

- Add extra sanity checks (e.g., exclude salvage/“for parts”).

## Anti-ban hygiene

- Respect site ToS; add randomized delays/jitter.

- Backoff on errors; rotate user-agents if needed.

- Avoid scraping when logged into personal accounts you care about.

## Troubleshooting

- Blank results: verify you can load the search URL in a normal browser; check selectors/XPaths.

- Driver errors: ChromeDriver must match your Chrome version.

- Email not sending: confirm SMTP credentials or Gmail App Password.

## Roadmap

- Migrate from Selenium page rendering → API/HTML parsing where possible.

- Structured output for downstream analysis (CSV/Parquet).

- Optional webhook (Discord/Slack) instead of email.
