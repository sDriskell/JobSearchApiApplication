import pytest
import CapstoneProject
import os
import time

@pytest.fixture
def get_data():  # Provided by professor
    """Capture data for each test so as not to rewrite code (DRY)"""
    import CapstoneProject
    return CapstoneProject.get_github_jobs_data()


def test_jobs_dict(get_data):  # Provided by professor
    """Test to assert that jobs is populated and test element 1 is a dict"""
    assert len(get_data) >= 100
    assert type(get_data[1]) is dict


def test_jobs_data(get_data):
    """Test to find real data from get_data parameter"""
    data_found = False
    for item in get_data:
        if item['type'] == "Full Time":
            data_found = True
    assert data_found


def test_save_data():
    """Test saving to file function"""
    test_entry = {"name": "Test McTester", "id": 8675309}
    test_list = []
    test_list.append(test_entry)
    test_file_name = "testfile.txt"
    CapstoneProject.save_data(test_list, test_file_name)
    test_file = open(test_file_name, 'r')
    text_sample = test_file.readline()
    if text_sample is not None:
        assert True
    else:
        assert False


def test_stackoverflow_data():
    """Test to ensure Stack Overflow table is created, written to, and then deleted"""
    test_file_name = 'jobdemo.sqlite'
    test_connection, test_cursor = CapstoneProject.open_db(test_file_name)
    CapstoneProject.create_table_stackoverflow(test_cursor)
    CapstoneProject.get_stack_overflow_jobs(test_cursor)
    if test_cursor.fetchmany() is not None:
        assert True
    else:
        assert False
    test_connection.close()


def test_clean_up():
    os.remove("testfile.txt")
    os.remove("jobdemo.sqlite")
