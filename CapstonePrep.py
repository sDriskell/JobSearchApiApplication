import requests
import time
import sqlite3
import feedparser
import pandas as pd
import plotly_express as px

from geopy.geocoders import Nominatim
from typing import Dict, List, Tuple, Any

"""
Shane Driskell
COMP 490
Prof. Santore
10 FEB 2020
"""


def get_github_jobs_data() -> List[Dict]:
    """retrieve github jobs data in form of a list of dictionaries after json processing"""
    all_data = []
    page = 1
    more_data = True
    while more_data:
        url = f"https://jobs.github.com/positions.json?page={page}"
        raw_data = requests.get(url)
        if "GitHubber!" in raw_data.text:
            # sometimes if I ask for pages too quickly I get an error; only happens in testing
            continue  # trying continue, but might want break
        if not raw_data.ok:  # if we didn't get a 200 response code, don't try to decode with .json
            continue
        partial_jobs_list = raw_data.json()
        all_data.extend(partial_jobs_list)
        if len(partial_jobs_list) < 50:
            more_data = False
        time.sleep(.1)  # short sleep between requests so I dont wear out my welcome.
        page += 1
    return all_data


def save_data(data, filename='data.txt'):
    with open(filename, 'a', encoding='utf-8') as file:
        for item in data:
            print(item, file=file)


def hard_code_create_table(cursor: sqlite3.Cursor):
    create_statement = f"""CREATE TABLE IF NOT EXISTS all_jobs(
    id TEXT PRIMARY KEY,
    type TEXT,
    url TEXT,
    created_at TEXT,
    company TEXT NOT NULL,
    company_url TEXT,
    location TEXT,
    title TEXT NOT NULL,
    description TEXT,
    how_to_apply TEXT,
    company_logo TEXT
    );
        """
    cursor.execute(create_statement)


# Filter table used to display search results
def create_table_filter_jobs(cursor: sqlite3.Cursor):
    create_statement = f"""CREATE TABLE IF NOT EXISTS filter_jobs(
    id TEXT PRIMARY KEY,
    type TEXT,
    url TEXT,
    created_at TEXT,
    company TEXT NOT NULL,
    company_url TEXT,
    location TEXT,
    title TEXT NOT NULL,
    description TEXT,
    how_to_apply TEXT,
    company_logo TEXT
    );
        """
    cursor.execute(create_statement)


# For cities and their lat/longs
def create_table_cache(cursor: sqlite3.Cursor):
    create_statement = f"""CREATE TABLE IF NOT EXISTS location_cache(
    city TEXT PRIMARY KEY,
    latitude TEXT,
    longitude TEXT
    );
        """
    cursor.execute(create_statement)


def hard_code_save_to_db(cursor: sqlite3.Cursor, all_github_jobs: List[Dict[str, Any]]):
    """in the insert statement below we need one '?' for each column, then we will use a second param with each of the
    values when we execute it. SQLITE3 will do the data sanitization to avoid little bobby tables style problems"""

    cursor.execute('''DELETE FROM all_jobs''')

    insert_statement = f"""INSERT INTO all_jobs(
        id, type, url, created_at, company, company_url, location, title, description, how_to_apply, company_logo)
        VALUES(?,?,?,?,?,?,?,?,?,?,?)"""
    for job_info in all_github_jobs:
        # first turn all the values from the jobs dict into a tuple
        data_to_enter = tuple(job_info.values())
        cursor.execute(insert_statement, data_to_enter)


# Ingest stackoverflow jobs feed with parser
def feed_parser_to_db(cursor: sqlite3.Cursor):
    url = f"https://stackoverflow.com/jobs/feed"
    feed = feedparser.parse(url)
    data_feed_parser = []
    raw_feed = requests.get(url)
    data_feed_parser.extend(raw_feed)
    # Format date entries to be uniform
    for jobs in feed.entries:
        date = "(%d/%02d/%02d)" % (jobs.published_parsed.tm_year,
                                   jobs.published_parsed.tm_mon,
                                   jobs.published_parsed.tm_mday)
        title = jobs.title
        location = title[title.rfind("(")+1:title.rfind(")")]

        cursor.execute('''INSERT INTO all_jobs(id, type, url, created_at, company, company_url, location,
        title, description, how_to_apply, company_logo) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (jobs.guid, None, jobs.link, date, jobs.guid, jobs.link, location, jobs.title, jobs.description,
                        None, None,))


def geo_locate(cursor, location):
    geo_code = Nominatim(user_agent="Project4")
    cursor.execute('''SELECT * FROM location_cache WHERE city LIKE?''', (location,))
    row = cursor.fetchone()

    if row is None:  # Only add if does not exist
        loc = geo_code.geocode(location)
        latitude = loc.latitude
        longitude = loc.longitude

        if loc is not None:
            print("adding to cache...")
            cursor.execute('''INSERT INTO location_cache(city, latitude, longitude) VALUES(?,?,?)''',
                           (location, latitude, longitude))
        else:
            cursor.execute('''INSERT INTO location_cache(city, latitude, longitude) VALUES(?,?,?)''',
                           ("remote", "41.820150", "-70.587270"))  # temp plot point for remote locations


def populate_filter_jobs_table(cursor, filtered_input):
    cursor.execute('''DELETE FROM filter_jobs''')
    execute = "INSERT INTO filter_jobs SELECT * FROM all_jobs " + filtered_input
    cursor.execute(execute)


def open_db(filename: str) -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
    db_connection = sqlite3.connect(filename)  # connect to existing DB or create new one
    cursor = db_connection.cursor()  # get ready to read/write data
    return db_connection, cursor


def close_db(connection: sqlite3.Connection):
    connection.commit()  # make sure any changes get saved
    connection.close()


def main():
    jobs_table_name = 'github_jobs_table'  # might be better as a constant in global space
    db_name = 'jobdemo.sqlite'
    connection, cursor = open_db(db_name)

    print("getting data...")
    data = get_github_jobs_data()
    hard_code_create_table(cursor)
    hard_code_save_to_db(cursor, data)
    feed_parser_to_db(cursor)

    print("filtering...")
    create_table_filter_jobs(cursor)
    print("geocode...")
    create_table_cache(cursor)
    print("filter jobs...")
    populate_filter_jobs_table(cursor, "WHERE location LIKE 'Boston, MA'")

    print("locating places...")
    cursor.execute('''SELECT * FROM filter_jobs''')
    items = cursor.fetchall()
    for jobs in items:  # Parses out the location data to be created into lat/long
        try:
            geo_locate(cursor, jobs[6])
        except AttributeError:
            print("no location passed...")

    print("join statement...")
    dataframe = pd.read_sql_query('''SELECT id, type, url, created_at, company, company_url, location, title, longitude,
    latitude FROM filter_jobs INNER JOIN location_cache on location_cache.city = filter_jobs.location''', connection)

    print("plot coords...")  # convert string into int for plotting
    figure = px.scatter_geo(dataframe, lat="latitude", lon="longitude", hover_name='location')
    figure.update_layout(mapbox_style="carto-darkmatter")
    figure.show()

    close_db(connection)


if __name__ == '__main__':
    main()


"""
References:
https://pythonexamples.org/python-sqlite3-check-if-table-exists/
https://www.dataquest.io/blog/python-api-tutorial/
https://stackoverflow.com/questions/23718896/pretty-print-json-in-python-pythonic-way
https://stackoverflow.com/questions/12599033/python-write-to-file-from-dictionary
https://community.jamasoftware.com/blogs/john-lastname/2017/09/29/managing-multiple-pages-of-results-in-the-jama-rest-api
https://webhost.bridgew.edu/jsantore/Spring2020/Capstone/3ContinuousIntegration.pdf
http://webhost.bridgew.edu/jsantore/Spring2020/Capstone/4DataHandling.pdf
https://www.sqlitetutorial.net/sqlite-python/insert/
https://semaphoreci.com/community/tutorials/testing-python-applications-with-pytest
https://www.pythonforbeginners.com/feedparser/using-feedparser-in-python
https://www.sqlitetutorial.net/sqlite-python/insert/
"""
