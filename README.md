# Shane Driskell
# CAPSTONE COMP 490

# Working Functions:

- Created Map
- Created the filter table
- Created the location cache table
- Merge tables to plot on map


# Not Working: 
- No UI for setting tags to filter against
- Have to manually change location to filter for in code
- No tags being displayed in GUI
- Package containing module 'plotly' is not listed in project requirements (I've used plotly_express and still get the same)


# New Code:

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
    
        def geo_locate(cursor, location):
                geo_code = Nominatim(user_agent="Project4")
                cursor.execute('''SELECT * FROM location_cache WHERE city LIKE?''', (location,))
                row = cursor.fetchone()

                if row is None:
                        loc = geo_code.geocode(location)
                        latitude = loc.latitude
                        longitude = loc.longitude

                if loc is not None:
                        print("adding to cache...")
                        cursor.execute('''INSERT INTO location_cache(city, latitude, longitude) VALUES(?,?,?)''',
                                (location, latitude, longitude))
                else:
                        cursor.execute('''INSERT INTO location_cache(city, latitude, longitude) VALUES(?,?,?)''',
                                ("remote", "41.820150", "-70.587270"))


        def populate_filter_jobs_table(cursor, filtered_input):
                cursor.execute('''DELETE FROM filter_jobs''')
                execute = "INSERT INTO filter_jobs SELECT * FROM all_jobs " + filtered_input
                cursor.execute(execute)


        def main():
                ...
                print("locating places...")
                cursor.execute('''SELECT * FROM filter_jobs''')
                items = cursor.fetchall()
                for jobs in items:
                        try:
                                geo_locate(cursor, jobs[6])
                        except AttributeError:
                                print("no location passed...")

                print("join statement...")
                dataframe = pd.read_sql_query('''SELECT id, type, url, created_at, company, company_url, location, title, longitude,
                latitude FROM filter_jobs INNER JOIN location_cache on location_cache.city = filter_jobs.location''', connection)

                print("plot coords...")
                figure = px.scatter_geo(dataframe, lat="latitude", lon="longitude", hover_name='location')
                figure.update_layout(mapbox_style="carto-darkmatter")
                figure.show()
                
# New Test Code:
  
        def test_geo_locate():
                connection, cursor = CapstonePrep.open_db("geo_test.sqlite")
                CapstonePrep.create_table_cache(cursor)
                CapstonePrep.geo_locate(cursor, "Boston, MA")
                table_size = cursor.rowcount
                success = table_size >= 1
                CapstonePrep.close_db(connection)
                assert success

