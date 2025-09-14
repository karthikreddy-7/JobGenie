Job Scraping PipelineThis project is a Python-based pipeline designed to scrape job postings from various job board websites, transform the data into a clean and structured format, and save it to a CSV file.FeaturesDynamic Location Support: Scrape for a single location or all locations defined in locations.json.Multiple Scrapers: Easily extendable to include more job sites (currently supports Indeed).Data Transformation: Cleans and standardizes raw scraped data into a consistent JobPosting schema.Command-Line Interface: Control the pipeline's execution using intuitive command-line arguments.Configuration Driven: Locations are managed in an external locations.json file.PrerequisitesPython 3.8+PandasJobspy (pip install jobspy)File Structure.
├── config/
│   └── locations.json      # Configuration for job locations
├── pipeline/
│   ├── __init__.py
│   ├── fetcher.py          # Logic for fetching data
│   ├── loader.py           # Logic for saving data
│   └── transformer.py      # Logic for cleaning data
├── scrapers/
│   ├── __init__.py
│   ├── base_scraper.py     # Abstract base class for scrapers
│   └── indeed_scraper.py   # Scraper for Indeed
├── schemas/
│   ├── __init__.py
│   └── job.py              # Pydantic schema for a Job Posting
├── config.py               # Central configuration for default parameters
├── main.py                 # Main entry point to run the pipeline
└── README.md               # This file
How to RunThe script is controlled via the command line from your terminal.Basic UsageYou must provide a search term as the first argument.python main.py "Software Engineer"
Command-Line ArgumentsArgumentDescriptionDefaultExamplesearch_term(Required) The job title to search for.-"Data Analyst"--locationRun for a single, specific location from your JSON file. If omitted, it runs for all locations.None--location "San Francisco"--jobsThe number of job listings to scrape per location.15--jobs 50--hoursFilter jobs posted within the last N hours.24--hours 8Examples1. Scrape for "Data Scientist" across all configured locations (default settings):python main.py "Data Scientist"
2. Scrape the 50 most recent "Project Manager" jobs in "New York" posted within the last week (168 hours):python main.py "Project Manager" --location "New York" --jobs 50 --hours 168
3. Scrape for "DevOps Engineer" in "Dallas" using default job count and time filter:python main.py "DevOps Engineer" --location "Dallas"
OutputThe pipeline will generate a single CSV file in the root directory named job_postings_<timestamp>.csv (e.g., job_postings_20250914_151700.csv). This file contains all the job postings found across the specified locations. The timestamp prevents you from overwriting previous results.