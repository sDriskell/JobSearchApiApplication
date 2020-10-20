"""
Shane Driskell
Project: Job Search API App
Purpose:  To build an application that takes job postings from two APIs (GitHub & Stackoverflow)
and populates a SQL database.  That database is then used to create a GUI that plots the job
postings on a map and presents a pop-up with the job data associated with it.

The goal of this is to revisit a previous assignment, improve and finish the started assignment

The get_github_jobs_data and save_data functions were originally provided for this assignment
"""

import requests
import time
import sqlite3
import feedparser
from typing import Dict, List, Tuple, Any

# For development purposes, delete when completed
import pprint


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


def get_github_jobs_data() -> List[Dict]: # Provided by professor
    """Retrieve github jobs data in form of a list of dictionaries after json processing"""
    all_data = []
    page = 1
    more_data = True
    while more_data:
        url = f"https://jobs.github.com/positions.json?page={page}"
        raw_data = requests.get(url)
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


def save_to_github_db(cursor: sqlite3.Cursor, all_jobs: List[Dict[str, Any]]):  # Portions provided by professor
    """Injest GitHub data into a table"""
    cursor.execute('''DELETE FROM g_jobs''')  # Scrub previous results to start over
    insert_statement = """INSERT INTO g_jobs(id, type, url, created_at, company, company_url, location, title, 
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
    # Format date entries to be uniform
    for jobs in feed.entries:
        date = "(%d/%02d/%02d)" % (jobs.published_parsed.tm_year, jobs.published_parsed.tm_mon,
                                   jobs.published_parsed.tm_mday)
        title = jobs.title
        location = title[title.rfind("(")+1:title.rfind(")")]  # Clips location data nestled in title field

        cursor.execute("""INSERT INTO s_jobs(id, author, link, location, date, summary, title) VALUES
        (?,?,?,?,?,?,?)""", (jobs.id, jobs.author, jobs.link, location, date, jobs.summary, jobs.title))


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

    print("Saving database...")
    close_db(connection)


if __name__ == '__main__':
    main()

