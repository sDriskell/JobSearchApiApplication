import requests
import time
from typing import Dict, List, Tuple, Any
import sqlite3


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
    create_statement = f"""CREATE TABLE IF NOT EXISTS hardcode_github_jobs(
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


def hard_code_save_to_db(cursor: sqlite3.Cursor, all_github_jobs: List[Dict[str, Any]]):
    """in the insert statement below we need one '?' for each column, then we will use a second param with each of the
    values when we execute it. SQLITE3 will do the data sanitization to avoid little bobby tables style problems"""
    insert_statement = f"""INSERT INTO hardcode_github_jobs(
        id, type, url, created_at, company, company_url, location, title, description, how_to_apply, company_logo)
        VALUES(?,?,?,?,?,?,?,?,?,?,?)"""
    for job_info in all_github_jobs:
        # first turn all the values from the jobs dict into a tuple
        data_to_enter = tuple(job_info.values())
        cursor.execute(insert_statement, data_to_enter)


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
    data = get_github_jobs_data()
    hard_code_create_table(cursor)
    hard_code_save_to_db(cursor, data)
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
