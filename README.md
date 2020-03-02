# Shane Driskell
# CAPSTONE COMP 490

# Working Functions:

- Updated sprint two test methods to function with updated CapstonePrep.py methods
- Implemented feedparser features into project
- Developed methods for creating feedparser table and adding entries to it
- Successfully stopped my kitten from butt typing in malicious code into my program.
- Create test methods for creating an feedparser table and populating a feedparser entry in the table


# Not Working: 
- N/A


# New Code:
        def hard_code_create_feed(cursor: sqlite3.Cursor):
            create_statement = f"""CREATE TABLE IF NOT EXISTS hardcode_stackoverflow_jobs(
            id TEXT PRIMARY KEY,
            type TEXT,
            url TEXT,
            created_at TEXT,
            company TEXT,
            company_url TEXT,
            location TEXT,
            title TEXT,
            description TEXT,
            how_to_apply TEXT,
            company_logo TEXT
            );
                """
            cursor.execute(create_statement)
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
                cursor.execute('''INSERT INTO hardcode_stackoverflow_jobs(id, type, url, created_at, company, company_url, location,
                title, description, how_to_apply, company_logo) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                               (jobs.guid, None, jobs.link, date, jobs.guid, jobs.link, None, jobs.title, jobs.description,
                                None, None,))

# New Test Code:
  
        def test_feed_table_exists():
            connection, cursor = CapstonePrep.open_db("feedtest.sqlite")
            CapstonePrep.hard_code_create_feed(cursor)
            CapstonePrep.feed_parser_to_db(cursor)
            result_cursor = cursor.execute(f"SELECT name from sqlite_master where (name = 'hardcode_stackoverflow_jobs')")
            success = len(result_cursor.fetchall()) >= 1
            assert success


        def test_save_feed_data():
            connection, cursor = CapstonePrep.open_db("feedtest2.sqlite")
            CapstonePrep.hard_code_create_feed(cursor)
            CapstonePrep.feed_parser_to_db(cursor)
            test_feed = f"SELECT type from {'hardcode_stackoverflow_jobs'} WHERE (id = 274402)"
            result_cursor = cursor.execute(test_feed)
            results = result_cursor.rowcount
            success = len(result_cursor.fetchall()) >= 1
            CapstonePrep.close_db(connection)
            assert success
