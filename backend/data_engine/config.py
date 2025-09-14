import os

# --- File Paths ---
# Assumes the script is run from the root directory where main.py is located.
# The path points to 'config/locations.json' relative to the script's directory.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCATIONS_CONFIG_PATH = os.path.join(BASE_DIR, 'config', 'locations.json')

# --- Scraping Parameters ---
DEFAULT_JOBS_TO_SCRAPE = 15
DEFAULT_HOURS_OLD = 24 # Corresponds to jobs posted in the last day
