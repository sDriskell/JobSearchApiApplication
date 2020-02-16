import pytest
import CapstonePrep


@pytest.fixture
def get_data():
    import CapstonePrep
    return CapstonePrep.get_github_jobs_data()


def test_jobs_dict(get_data):
    # first required test
    assert len(get_data) >= 100
    assert type(get_data[1]) is dict


def test_jobs_data(get_data):
    # any real data should have both full time and Contract
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


def test_table_exists():
    fake_row = {'id': 'F$RT%YH&', 'type': 'Full Time', 'url': 'http://wwww.fakedata.com', 'created_at': '02-12-2020',
                'company': "Don't Work Here Comp", 'company_url': None, 'location': "giant urban metro",
                'title': 'Junior software peon', 'description': "blah blah, devops, scrum, hot tech",
                'how_to_apply': "http://runaway.com", 'company_logo': None}
    connection, cursor = CapstonePrep.open_db('testonly.sqlite')
    CapstonePrep.hard_code_create_table(cursor)
    result_cursor = cursor.execute(f"SELECT name from sqlite_master where (name = 'hardcode_github_jobs')")
    success = len(result_cursor.fetchall()) >= 1
    assert success


def test_save_data():  # modern sprint2 version of save data
    # this is fake data, but I'm testing the save_to_db function so fake data is fine
    fake_row = {'id': 'F$RT%YH&', 'type': 'Full Time', 'url': 'http://wwww.fakedata.com', 'created_at': '02-12-2020',
                'company': "Don't Work Here Comp", 'company_url': None, 'location': "giant urban metro",
                'title': 'Junior software peon', 'description': "blah blah, devops, scrum, hot tech",
                'how_to_apply': "http://runaway.com", 'company_logo': None}
    connection, cursor = CapstonePrep.open_db('testonly.sqlite')
    CapstonePrep.hard_code_create_table(cursor)
    # might have to blow away db on later runs - first run is fine
    CapstonePrep.hard_code_save_to_db(cursor, [fake_row])
    test_query = F"SELECT type from {'hardcode_github_jobs'} WHERE (id = 'F$RT%YH&')"
    result_cursor = cursor.execute(test_query)
    results = result_cursor.rowcount
    success = len(result_cursor.fetchall()) >= 1
    CapstonePrep.close_db(connection)
    assert success
