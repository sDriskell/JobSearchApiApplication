import requests
import time
from typing import Dict, List
import sqlite3

"""
Shane Driskell
COMP 490
Prof. Santore
10 FEB 2020

References:
https://pythonexamples.org/python-sqlite3-check-if-table-exists/
https://www.dataquest.io/blog/python-api-tutorial/
https://stackoverflow.com/questions/23718896/pretty-print-json-in-python-pythonic-way
https://stackoverflow.com/questions/12599033/python-write-to-file-from-dictionary
https://community.jamasoftware.com/blogs/john-lastname/2017/09/29/managing-multiple-pages-of-results-in-the-jama-rest-api
https://webhost.bridgew.edu/jsantore/Spring2020/Capstone/3ContinuousIntegration.pdf
http://webhost.bridgew.edu/jsantore/Spring2020/Capstone/4DataHandling.pdf
"""


def get_github_jobs_data() -> List[Dict]:
    """retrieve github jobs data in form of a list of dictionaries
    after json processing"""
    all_data = []
    page = 1
    more_data = True
    while more_data:
        url = f"https://jobs.github.com/positions.json?page={page}"
        raw_data = requests.get(url)
        if "GitHubber!" in raw_data:  # sometimes if I ask for pages too quickly I get an error; only happens in testing
            continue  # trying continue, but might want break
        partial_jobs_list = raw_data.json()
        all_data.extend(partial_jobs_list)
        if len(partial_jobs_list) < 50:
            more_data = False
        time.sleep(.1)  # short sleep between requests so I dont wear out my welcome.
        page += 1
    return all_data


# Pushes List[Dict] to .txt
def save_data(data, filename='data.txt'):
    with open(filename, 'a', encoding='utf-8') as file:
        for item in data:
            print(item, file=file)


# Set the columns for database
def create_db(data, conn, c):
    c.execute('''CREATE TABLE IF NOT EXISTS tutorial(company TEXT, id TEXT, type TEXT, url TEXT, created_at TEXT,
    company_url TEXT, location TEXT, title TEXT, description TEXT, how_to_apply TEXT);''')


# Add rows to database populated with each individual dictionary
def populate_db(data, conn, c):
    for jobs in data:
        c.execute('''INSERT INTO tutorial(company, id, type, url, created_at, company_url, location, title,
        description, how_to_apply) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (jobs["company"], jobs["id"], jobs["type"], jobs["url"], jobs["created_at"], jobs["company_url"],
                   jobs["location"], jobs["title"], jobs["description"], jobs["how_to_apply"],))
    # Commit and close so rows are saved
    conn.commit()


def main():
    # Build list[dict] and .txt file
    data = get_github_jobs_data()
    save_data(data)
    # Build connection and cursor for database
    conn = sqlite3.connect('test.sqlite')
    c = conn.cursor()
    # Create and populate database
    create_db(data, conn, c)
    populate_db(data, conn, c)
    # Close connection and cursor
    c.close()
    conn.close()


if __name__ == '__main__':
    main()
