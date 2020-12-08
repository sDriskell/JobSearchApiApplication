"""
Shane Driskell
Project: Job Search API App
Purpose:  To build an application that takes job postings from two APIs (GitHub & Stackoverflow)
and populates a SQL database.  That database is then used to create a GUI that plots the job
postings on a map and presents a pop-up with the job data associated with it.

The goal of this is to revisit a previous assignment, improve, and finish the started assignment

The get_github_jobs_data and save_data functions were originally provided for this assignment
"""

import requests
import time
import sqlite3
import feedparser
import time
import pandas as pd
import plotly_express as px

from typing import Dict, List, Tuple, Any
from geopy.geocoders import Nominatim


def save_data(data, filename='data.txt'):
    """Store to a text file"""
    with open(filename, 'w', encoding="utf-8") as file:
        for item in data:
            print(item, file=file)


def open_db(filename: str) -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
    """Create or manage a database file"""
    db_connection = sqlite3.connect(filename)  # Create or connect to DB
    cursor = db_connection.cursor()  # Read/write data
    return db_connection, cursor


def close_db(connection: sqlite3.Connection):
    """Close DB once finished with"""
    connection.commit()
    connection.close()


def get_github_jobs_data() -> List[Dict]:  # Provided by professor
    """Retrieve github jobs data in form of a list of dictionaries after json processing"""
    all_data = []
    page = 1
    more_data = True
    while more_data:
        url = f"https://jobs.github.com/positions.json?page={page}"
        raw_data = requests.get(url)
        raw_data.raise_for_status()
        if "GitHubber!" in raw_data:  # Avoid error in testing
            continue  # Trying continue, but might want break
        partial_jobs_list = raw_data.json()
        all_data.extend(partial_jobs_list)
        if len(partial_jobs_list) < 50:
            more_data = False
        time.sleep(.1)  # Avoid overwhelming site.
        page += 1
    return all_data


def create_table_github(cursor: sqlite3.Cursor):
    """Build a table for job data to be stored"""
    create_statement = f"""CREATE TABLE IF NOT EXISTS g_jobs(
    id TEXT PRIMARY KEY,
    company TEXT NOT NULL,
    company_logo TEXT,
    company_url TEXT,
    created_at DATE,
    description TEXT,
    how_to_apply TEXT,
    location TEXT,
    title TEXT NOT NULL,
    type TEXT,
    url TEXT);"""
    cursor.execute(create_statement)


def create_table_stackoverflow(cursor: sqlite3.Cursor):
    """Build a table for Stack Overflow job data to be stored"""
    create_statement = f"""CREATE TABLE IF NOT EXISTS s_jobs(
    id TEXT PRIMARY KEY,
    author TEXT NOT NULL,
    link TEXT,
    location TEXT,
    date DATE,
    summary TEXT,
    title TEXT NOT NULL
);"""
    cursor.execute(create_statement)


def create_combined_table(cursor: sqlite3.Cursor):
    """Create new table that will contain content from previous searches"""
    create_statement = f"""CREATE TABLE IF NOT EXISTS combined_jobs(
    id TEXT PRIMARY KEY,
    company TEXT,
    link TEXT,
    location TEXT,
    date DATE,
    content TEXT,
    title TEXT,
    latitude TEXT,
    longitude TEXT);"""
    cursor.execute(create_statement)


def create_location_cache(cursor:sqlite3.Cursor):
    """Create a table with location name and coordinates"""
    create_statement = f"""CREATE TABLE IF NOT EXISTS location_cache(
    location TEXT PRIMARY KEY,
    latitude FLOAT,
    longitude FLOAT);"""
    cursor.execute(create_statement)


def save_to_github_db(cursor: sqlite3.Cursor, all_jobs: List[Dict[str, Any]]):
    """Ingest GitHub data into a table"""
    cursor.execute(f'''DELETE FROM g_jobs''')  # Scrub previous results to start over
    insert_statement = f"""INSERT INTO g_jobs(id, type, url, created_at, company, company_url, location, title, 
    description, how_to_apply, company_logo) VALUES(?,?,?,?,?,?,?,?,?,?,?)"""

    # Turn all values from the jobs dict into a tuple
    for job_info in all_jobs:
        data_to_enter = tuple(job_info.values())
        cursor.execute(insert_statement, data_to_enter)


def get_stack_overflow_jobs(cursor: sqlite3.Cursor):
    """Ingest Stack Overflow feed directly into a separate table"""
    cursor.execute('''DELETE FROM s_jobs''')  # Scrub previous results to start over
    url = f"https://stackoverflow.com/jobs/feed"
    feed = feedparser.parse(url)

    for jobs in feed.entries:
        date = "(%d/%02d/%02d)" % (jobs.published_parsed.tm_year, jobs.published_parsed.tm_mon,
                                   jobs.published_parsed.tm_mday)  # Format date entries to be uniform
        title = jobs.title
        location = title[title.rfind("(")+1:title.rfind(")")]  # Clips location data nested in title field

        cursor.execute(f"""INSERT INTO s_jobs(id, author, link, location, date, summary, title) VALUES
        (?,?,?,?,?,?,?)""", (jobs.id, jobs.author, jobs.link, location, date, jobs.summary, jobs.title))


def combine_tables(cursor: sqlite3.Cursor):
    """Merge both GitHub and StackOverflow tables into a combined table"""
    cursor.execute('''DELETE FROM combined_jobs''')  # Scrub previous results to start over
    geo_code = Nominatim(user_agent="capstone_project")

    # GitHub (g_jobs) merge statement
    merge_g_statement = (f"""
        INSERT INTO
            combined_jobs(id, company, link, location, date, content, title)
        SELECT
            id, company, url, location, created_at, description, title
        FROM
            "g_jobs"
        """)
    cursor.execute(merge_g_statement)

    # StackOverflow (s_jobs) merge statement
    merge_s_statement = (f"""
        INSERT INTO
            combined_jobs(id, company, link, location, date, content, title)
        SELECT
            id, author, link, location, date, summary, title
        FROM
            "s_jobs"
        """)
    cursor.execute(merge_s_statement)


def geo_locate(cursor: sqlite3.Cursor):
    """Generate location data for each city then feed to location_cache table"""
    cursor.execute('''DELETE FROM location_cache''')  # Scrub previous results to start over

    geo_code = Nominatim(user_agent="capstone_project")
    cursor.execute("""SELECT location FROM combined_jobs""")
    jobs = cursor.fetchall()  # Set to .fetchall once development is complete

    for location in jobs:
        try:
            full_loc = geo_code.geocode(location[0])
            print(location[0])
            cursor.execute(f"""INSERT INTO location_cache(location, latitude, longitude)
            VALUES (?,?,?)""", (location[0], full_loc.latitude, full_loc.longitude))
        except AttributeError:
            print(AttributeError)
        except sqlite3.IntegrityError:
            print(sqlite3.IntegrityError)


def create_dataframe(connection: sqlite3.Connection) -> pd.DataFrame:
    """Create dataframe containing fields from combined_jobs and location_cache tables"""
    dataframe = pd.read_sql_query(f"""
        SELECT
            combined_jobs.id, combined_jobs.company, combined_jobs.link, combined_jobs.location,
            combined_jobs.date, combined_jobs.content, combined_jobs.title, location_cache.location,
            location_cache.latitude, location_cache.longitude
        FROM
            combined_jobs
        LEFT OUTER JOIN
            location_cache on (combined_jobs.location = location_cache.location)""",
                                      connection)
    print(dataframe)
    return dataframe


def plot_map(loc_dataframe: pd.DataFrame):
    """Produce map and plots with meta-data on each potential job"""
    figure = px.scatter_geo(loc_dataframe, lat="latitude", lon="longitude",
                            hover_name='title', text='id')
    figure.update_layout(mapbox_style="carto-darkmatter")
    figure.show()


def main():
    jobs_table_name = 'github_jobs_table'
    db_name = 'jobdemo.sqlite'
    print("Opening database...")
    connection, cursor = open_db(db_name)
    print("Creating GitHub table...")
    create_table_github(cursor)
    print("Creating Stack Overflow table...")
    create_table_stackoverflow(cursor)

    print("-" * 60)

    print("Fetching GitHub data...")
    github_data = get_github_jobs_data()
    print("Saving to data.txt...")
    save_data(github_data)
    print("Writing to GitHub table...")
    save_to_github_db(cursor, github_data)

    print("-"*60)

    print("Fetching Stack Overflow data and saving to table...")
    get_stack_overflow_jobs(cursor)

    print("-"*60)

    print("Merging GitHub and Stack Overflow tables...")
    print("Creating combined table...")
    create_combined_table(cursor)
    print("Inserting into combined table...")
    combine_tables(cursor)

    print("-"*60)

    print("Creating location cache table...")
    create_location_cache(cursor)
    print("Generating location data...")
    geo_locate(cursor)
    print("Creating the dataframe...")
    loc_dataframe = create_dataframe(connection)
    print("Plotting locations...")
    plot_map(loc_dataframe)

    print("-" * 60)

    print("Saving database...")
    close_db(connection)


if __name__ == '__main__':
    main()
