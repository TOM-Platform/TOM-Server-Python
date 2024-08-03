import pytest
import os

from Utilities import file_utility


def test_append_file():
    data = "test"
    file_name = os.getcwd() + "file.txt"

    file_utility.append_data(file_name, data)

    f = open(file_name, "r")
    assert f.read() == data

    f.close()
    os.remove(file_name)


def test_is_yaml_file_true():
    file_name = "something.yaml"

    assert file_utility.is_yaml_file(file_name) == True


def test_is_yaml_file_false():
    file_name = "something.txt"

    assert file_utility.is_yaml_file(file_name) == False


def test_is_file_exists_true():
    file_name = os.getcwd() + "file1.txt"
    f = open(file_name, "w")
    f.close()

    assert file_utility.is_file_exists(file_name) == True

    os.remove(file_name)


def test_is_file_exists_true():
    file_name = os.getcwd() + "file2.txt"

    assert file_utility.is_file_exists(file_name) == False


def test_create_new_directory():
    new_dir = os.path.join(file_utility.get_project_root(), "temp_dir")
    assert file_utility.create_directory(new_dir) == True
    assert os.path.isdir(new_dir)

    os.rmdir(new_dir)


def test_create_new_directory_with_empty_name():
    assert file_utility.create_directory('') == False


def test_read_file():
    file_name = os.getcwd() + "file3.txt"
    data = "something"

    with open(file_name, "w") as f:
        f.write(data)
        f.close()

    assert file_utility.read_file(file_name) == [data]
    os.remove(file_name)


def test_read_yaml_file():
    file_name = os.getcwd() + "file4.yaml"
    data = "key:value"

    with open(file_name, "w") as f:
        f.write(data)
        f.close()

    assert file_utility.read_yaml_file(file_name) == data
    os.remove(file_name)


def test_read_json_file():
    file_name = os.getcwd() + "file5.json"
    data = "key:value"

    with open(file_name, "w") as f:
        f.write(data)
        f.close()

    assert file_utility.read_yaml_file(file_name) == data
    os.remove(file_name)


def test_write_data():
    file_name = os.getcwd() + "file6.txt"
    data = "Something"

    file_utility.write_data(file_name, data)

    with open(file_name, "r") as f:
        assert f.read() == data
        f.close()

    os.remove(file_name)
