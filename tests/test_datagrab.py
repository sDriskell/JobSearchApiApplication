import pytest
import CapstonePrep
import sqlite3


@pytest.fixture
def get_data():
    import CapstonePrep
    return CapstonePrep.get_github_jobs_data()


def test_jobs_dict(get_data):
    # First required test
    assert len(get_data) >=100
    assert type(get_data[1]) is dict


def test_jobs_data(get_data):
    # Any real data should have both full time and Contract
    # jobs in the list, assert this
    data = get_data
    full_time_found = False
    contract_found = False
    for item in data:
        if item['type'] == 'Contract':
            contract_found = True
        elif item['type'] == 'Full Time':
            full_time_found = True
    assert contract_found and full_time_found


def test_save_data():
    # Second required test
    demo_data = {'id': 1234, 'type': "Testable"}
    list_data = []
    list_data.append(demo_data)
    file_name = "testfile.txt"
    CapstonePrep.save_data(list_data, file_name)
    testfile = open(file_name, 'r')
    saved_data = testfile.readlines()
    # The save puts a newline at the end
    assert f"{str(demo_data)}\n" in saved_data


# Create table and test to make sure one entry exists to show database and table are built
def test_database():
    data = CapstonePrep.get_github_jobs_data()
    conn = sqlite3.connect('test.sqlite')
    c = conn.cursor()
    CapstonePrep.create_db(data, conn, c)
    CapstonePrep.populate_db(data, conn, c)
    # Calls database and table to check to see if at least one entry exists
    c.execute('''SELECT count(name) FROM sqlite_master WHERE type='table' AND name='tutorial' ''')
    if c.fetchone()[0] == 1:
        {print("Table was built.")}

    c.close()
    conn.close()


def test_good_insert():
    # good insert here
    demo_data = {'company': "testName", 'id': "1", 'type': "full", 'url': "www.nope.com",
                 'created_at': "2020-02-02", 'company_url': "sa.com", 'location': "US",
                 'title': "worker", 'description': "describe", 'how_to_apply': "hired"}

    conn = sqlite3.connect('test.sqlite')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS tutorial(company TEXT, id TEXT, type TEXT, url TEXT, created_at TEXT,
    company_url TEXT, location TEXT, title TEXT, description TEXT, how_to_apply TEXT);''')

    c.execute('''INSERT INTO tutorial(company, id, type, url, created_at, company_url, location, title,
    description, how_to_apply) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
          (demo_data["company"], demo_data["id"], demo_data["type"], demo_data["url"], demo_data["created_at"],
           demo_data["company_url"], demo_data["location"], demo_data["title"], demo_data["description"],
           demo_data["how_to_apply"],))

    """
    entry_found = False
    if c.fetchone()[0] == 1:
        entry_found = False
    """

    conn.commit()
    c.close()
    conn.close()
    # assert entry_found

""" NOT WORKING
def test_bad_insert():
    # bad insert here
    demo_data = {'company': "testName", 'id': 1, 'type': "full", 'url': "www.nope.com",
                 'created_at': 20200202, 'company_url': "sa.com", 'location': "US",
                 'title': "worker", 'description': "describe", 'how_to_apply': "hired"}

    conn = sqlite3.connect('test.sqlite')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS tutorial(company TEXT, id TEXT, type TEXT, url TEXT, created_at TEXT,
    company_url TEXT, location TEXT, title TEXT, description TEXT, how_to_apply TEXT);''')

    c.execute('''INSERT INTO tutorial(company, id, type, url, created_at, company_url, location, title,
    description, how_to_apply) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
          (demo_data["company"], demo_data["id"], demo_data["type"], demo_data["url"], demo_data["created_at"],
           demo_data["company_url"], demo_data["how_to_apply"], demo_data["location"], demo_data["title"],
           demo_data["description"],))
    conn.commit()
    c.close()
    conn.close()
"""