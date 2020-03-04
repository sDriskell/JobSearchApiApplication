# Shane Driskell
# CAPSTONE COMP 490

# Working Functions:

- Created Map
- Created_table_cache table


# Not Working: 
Unable to get my filter jobs table to function.  My location is set in a Tuple format and I'm unable to parse out the town. ''.join() does not work and cannot couple the city and country into a string.  I get one of two attribute erros; either tuple object has no attribute location or list object has no attribute (when I use ''.join().  This leads to me being unable to create an overlay of job data and proper test methods.

Where I'm failing is I don't know what I want to do.  It's not a "you don't know what you don't know" but more of picturing/imagining what you're looking to do.


# New Code:

        def create_table_cache(cursor: sqlite3.Cursor):
                create_statement = f"""CREATE TABLE IF NOT EXISTS filter_jobs(
                location TEXT PRIMARY KEY,
                latitude TEXT,
                longitude TEXT
                );"""
                cursor.execute(create_statement)


        # Unable to convert tuple location into a name and lat/long
        # takes cursor,column to filter on, and value to filter on
        def filter_jobs(cursor):
                geolocator = Nominatim(user_agent="specify_your_app_here")
                cursor.execute('''SELECT location from all_jobs''')
                records = cursor.fetchall()
                for row in records:
                        location_string = records.location[records.rfind("'(")+1:records.rfind(",")]
                        time.sleep(0.5)
                        try:
                                place = geolocator.geocode(location_string)
                                location_lat = location_string.latitude
                                location_long = location_string.longitude
                                cursor.execute('''INSERT INTO filter_jobs(location, latitude, longitude) VALUES (?, ?, ?)''',
                                        (location_string, location_lat, location_long,))
                        except AttributeError:
                                print(row)  # AttributeError: 'tuple' object has no attribute 'location'


        # Plot job locations on googleMap
        def create_map(cursor):
                latitudes = []
                longitudes = []
                gmap = gmplot.GoogleMapPlotter(35, -102, 5)
                gmap.scatter(latitudes, longitudes, 'red', size=10)
                gmap.draw("jobMap.html")
                
                
# New Test Code:
  
        N/A
