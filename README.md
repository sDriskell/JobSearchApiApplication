# Shane Driskell
# CAPSTONE COMP 490

# Working Functions:

- Create a data base with a table/document

- Save data from 

- Create separate function that takes in data collected from data pulled

- Testing: Have test check to see if the data was saved to the database properly

- Testing: Write test to ensure table exists in the database after your program runs

# Not Working: 

- Testing: write test for your function that saves to the database. (send some data as a parameter to your function, and have it save the data to the database). Try to save some good data, try to save some bad data and make sure that this test fails (and mark it as expected to fail so that the rest of the tests continue)


# New Code:
    def create_db(data, conn, c):
        c.execute('''CREATE TABLE IF NOT EXISTS tutorial(company TEXT, id TEXT, type TEXT, url TEXT, created_at TEXT,
        company_url TEXT, location TEXT, title TEXT, description TEXT, how_to_apply TEXT);''')


    def populate_db(data, conn, c):
        for jobs in data:
            c.execute('''INSERT INTO tutorial(company, id, type, url, created_at, company_url, location, title,
            description, how_to_apply) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (jobs["company"], jobs["id"], jobs["type"], jobs["url"], jobs["created_at"], jobs["company_url"],
                   jobs["location"], jobs["title"], jobs["description"], jobs["how_to_apply"],))
        conn.commit()
        c.close()
        conn.close()

    def build_list():
        data = get_github_jobs_data()
        save_data(data)
        return data


    def build_database(data):
        # Build connection and cursor for database
        conn = sqlite3.connect('test.sqlite')
        c = conn.cursor()
        # Create and populate database
        create_db(data, conn, c)
        populate_db(data, conn, c)
        # Close connection and cursor
        c.close()
        conn.close()


    def main():
        data = build_list()
        build_database(data)
        
   
# New Test Code:
    def test_database():
        data = CapstonePrep.get_github_jobs_data()
        conn = sqlite3.connect('test.sqlite')
        c = conn.cursor()
        CapstonePrep.create_db(data, conn, c)
        CapstonePrep.populate_db(data, conn, c)

        c.execute('''SELECT count(name) FROM sqlite_master WHERE type='table' AND name='tutorial' ''')
        if c.fetchone()[0] == 1:
            {print("Table was built.")}

        c.close()
        conn.close()

