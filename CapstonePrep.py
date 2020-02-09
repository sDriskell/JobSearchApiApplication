import requests
import time
from typing import Dict, List
import sqlite3


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


def save_data(data, filename='data.txt'):
    with open(filename, 'a', encoding='utf-8') as file:
        for item in data:
            print(item, file=file)


def save_to_db(data):
    """:keyword data is a list of dictionaries. Each dictionary is a JSON
    object with a bit of jobs data"""
    conn = sqlite3.connect('test.sqlite')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tutorial(company TEXT, id TEXT, type TEXT, url TEXT, created_at TEXT,
    company_url TEXT, location TEXT, title TEXT, description TEXT, how_to_apply TEXT);''')

    for jobs in data:
        c.execute('''INSERT INTO tutorial(company, id, type, url, created_at, company_url, location, title,
        description, how_to_apply) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (jobs["company"], jobs["id"], jobs["type"], jobs["url"], jobs["created_at"], jobs["company_url"],
                   jobs["location"], jobs["title"], jobs["description"], jobs["how_to_apply"],))
    conn.commit()
    c.close()
    conn.close()


def main():
    data = get_github_jobs_data()
    save_data(data)
    save_to_db(data)


if __name__ == '__main__':
    main()
