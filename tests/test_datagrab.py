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


# Test to ensure database and table are created
def test_database():
    data = CapstonePrep.get_github_jobs_data()
    conn = sqlite3.connect('test.sqlite')
    c = conn.cursor()
    CapstonePrep.create_db(data, conn, c)
    CapstonePrep.populate_db(data, conn, c)
    # Create table and test to make sure one entry exists to show database and table are built
    c.execute('''SELECT count(name) FROM sqlite_master WHERE type='table' AND name='tutorial' ''')
    if c.fetchone()[0] == 1:
        {print("Table was built.")}

    c.close()
    conn.close()


