import sqlite3
import feedparser


# Have a parameter that takes a string and names the DB table after it

# def hard_code_create_table(cursor: sqlite3.Cursor):
#    create_statement = f"""CREATE TABLE IF NOT EXISTS hardcode_github_jobs(
#    id TEXT PRIMARY KEY,
#    type TEXT,
#    url TEXT,
#    created_at TEXT,
#    company TEXT NOT NULL,
#    company_url TEXT,
#    location TEXT,
#    title TEXT NOT NULL,
#    description TEXT,
#    how_to_apply TEXT,
#    company_logo TEXT
#    );
#        """
#    cursor.execute(create_statement)

""" cur.execute("CREATE TABLE IF NOT EXISTS " + table_name + " (#stufF here#)")"""

