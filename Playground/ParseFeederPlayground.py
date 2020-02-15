import feedparser
import sqlite3
import requests
from typing import Dict, List


url = "https://stackoverflow.com/jobs/feed"
feed = feedparser.parse(url)

"""
for post in feed.entries:
    date = "(%d/%02d/%02d)" % (post.published_parsed.tm_year,
                               post.published_parsed.tm_mon,
                               post.published_parsed.tm_mday)
    print("post date: " + date)
    print("post title: " + post.title)
    print("post link: " + post.link)
    print("post description: " + post.description)
    print("post id: " + post.guid)
"""
connect = sqlite3.connect('test.sqlite')
cursor = connect.cursor()

all_data = []
url = f"https://stackoverflow.com/jobs/feed"
raw_data = requests.get(url)
partial_jobs_list = raw_data
all_data.extend(partial_jobs_list)

print(all_data)
print(all_data.__len__())


cursor.execute('''CREATE TABLE IF NOT EXISTS jobdb(
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
);''')

for jobs in feed.entries:
    date = "(%d/%02d/%02d)" % (jobs.published_parsed.tm_year,
                               jobs.published_parsed.tm_mon,
                               jobs.published_parsed.tm_mday)
    cursor.execute('''INSERT INTO jobdb(id, type, url, created_at, company, company_url, location, title,
    description, how_to_apply, company_logo) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                   (jobs.guid, None, jobs.link, date, jobs.guid, jobs.link, None, jobs.title, jobs.description,
                    None, None,))

connect.commit()
cursor.close()
connect.close()
