# DS3022 - Data Project 1 (Fall 2025)

## The Pipeline
This is an ELT pipeline that ingests data from 2024 about yellow and green taxi trips in New York City. The goal is to find statistics through the year about carbon dioxide production due to taxi travel. There are four steps:
- Load: Pull the data from the NYC government website, with one table per type of taxi. Also loads vehicle emission rate statistics from a local file.
- Clean: Remove irrelevant data from the NYC taxi data sets, such as duplicates and outliers.
- Transform: Add new columns from data points, such as CO2 production for the whole trip and various columns about the date of the trip.
- Analyze: Use the new columns to calculate statistics for 2024 about when CO2 production is most and least prominent during the year, along with the most CO2-producing trip during the year.

## Design Choices
I made reusability the key focus through my program. Throughout the approach I tried to make the program iterate over repeating code, including, but not limited to:
- Yellow and green taxis
- The date columns, using zip() for pairs of column name and command required
- Strings to be printed and logged are in a report command

I also tried to make sure that the pipeline never conflicts with itself. Column additions and table drops are always if the respective column does not exist or respective table does exist, data loading gives a fresh copy of the data each time, etc.

Readability is another key factor. Code is largely commented and throughout the process I made verification print-outs to ensure the calculations were performed correctly. For the graph of emissions, the graph without Y scaling borders on unreadable for green taxis. I believe demonstrating how usage changes from month to month per taxi type is more important, so I made the graph with two Y axes (one per taxi type, on each side, [monthly_emissions_duo.png](monthly_emissions_duo.png)) that more appropriately demonstrates these changes.

## Running
Make sure DuckDB is installed. Then, clone this repository and run this in the terminal at its folder (MacOS):
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```