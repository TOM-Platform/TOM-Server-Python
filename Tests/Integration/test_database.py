import os
from os import remove

import pytest

from Tests.Integration.test_db_util import set_test_db_environ, get_integration_path

set_test_db_environ()
from Database import database, tables


@pytest.fixture(scope='session', autouse=True)
def teardown():
    relative_path = get_integration_path()
    db_path = os.path.join(relative_path, "Test.db")
    remove(db_path)


def test_tables_created_on_init():
    database.init()
    all_created_tables = tables.table_dict.keys()
    assert list(all_created_tables) == ["OtherTable", "TestTable"]


def test_insert_data_if_not_exists():
    database.init()
    test_insert_data = {"int_value": 10, "string_value": "Something"}
    tables.insert_rows_to_table("TestTable", test_insert_data)
    result = tables.get_rows_from_table("TestTable", {}).all()

    expected = [
        (1, 10, "Something")
    ]
    assert result == expected


def test_insert_data_if_exists_and_unique_constraint():
    database.init()
    test_insert_data = {"int_value": 20, "string_value": "Another"}
    tables.insert_rows_to_table("OtherTable", test_insert_data)

    with pytest.raises(Exception):
        tables.insert_rows_to_table("OtherTable", test_insert_data)


def test_get_data_if_not_exists():
    result = tables.get_rows_from_table("OtherTable", {"string_value": "Something"}).all()
    assert result == []
