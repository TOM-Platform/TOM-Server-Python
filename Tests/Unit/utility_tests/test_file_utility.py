import pytest
import shutil
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


# Sample directory and file names to use in tests
TEST_ROOT = os.path.join(file_utility.get_project_root(), "tmp", "test_root")
TEST_FOLDERS = ["folder1", "folder2"]
TEST_FILES = ["file1.txt", "file2.txt"]


@pytest.fixture(scope="function")
def setup_test_environment():
    # Create a test root directory and subfolders
    os.makedirs(os.path.join(TEST_ROOT, *TEST_FOLDERS))

    # Create test files
    for file_name in TEST_FILES:
        with open(os.path.join(TEST_ROOT, *TEST_FOLDERS, file_name), 'w') as f:
            f.write("test")

    yield  # This is where the testing happen

    # Teardown: remove the test root directory after each test
    try:
        shutil.rmtree(TEST_ROOT)
    except OSError as e:
        print(f"Error removing test root directory {TEST_ROOT}: {e}")


def test_get_path_from_project_root(setup_test_environment):
    # Arrange
    folders = TEST_FOLDERS
    expected_path = os.path.join(TEST_ROOT, *folders)

    # Act
    result = file_utility.get_path_from_project_root(["tmp", "test_root", *folders])

    # Assert
    assert result == expected_path
    assert os.path.exists(result)


def test_get_path_with_filename(setup_test_environment):
    # Arrange
    directory = os.path.join(TEST_ROOT, *TEST_FOLDERS)
    filename = "file3.txt"
    expected_path = os.path.join(directory, filename)

    # Act
    result = file_utility.get_path_with_filename(directory, filename)

    # Assert
    assert result == expected_path


def test_delete_all_files_in_dir(setup_test_environment):
    # Arrange
    dir_path = os.path.join(TEST_ROOT, *TEST_FOLDERS)

    # Act
    result = file_utility.delete_all_files_in_dir(dir_path)

    # Assert
    assert result == True
    assert len(os.listdir(dir_path)) == 0  # Ensure directory is empty


def test_delete_all_files_in_dir_exception(setup_test_environment):
    # Arrange
    dir_path = os.path.join(TEST_ROOT, "non_existing_folder")

    # Act
    result = file_utility.delete_all_files_in_dir(dir_path)

    # Assert
    assert result == False
