# Shane Driskell
# CAPSTONE COMP 490

# Working Functions:

- Create a data base with a table/document

- Save data from 

- Create separate function that takes in data collected from data pulled


# Needs Working On: 

- Testing: Have test check to see if the data was saved to the database properly

- Testing: Write test to ensure table exists in the database after your program runs

- Testing: write test for your function that saves to the database. (send some data as a parameter to your function, and have it save the data to the database). Try to save some good data, try to save some bad data and make sure that this test fails (and mark it as expected to fail so that the rest of the tests continue)


# To Do:
 
- Update your readme.md to include the new code. update the install and running instructions in the readme. Also, if needed, add a list of anything that is missing. 

- Make sure that your automated tests and linters are running properly on all files including any new ones.

- Make sure that any newly needed files are included in the github repo

- Make sure that your git commit messages are reasonable.

# New Code:

    def main():

        ...    
    
        conn = sqlite3.connect('test.sqlite')
    
        c = conn.cursor()
    
        create_db(data, conn, c)
    
        populate_db(data, conn, c)
    
    
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
