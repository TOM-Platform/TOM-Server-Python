import pytest
from unittest.mock import patch, MagicMock
from Services.pandalens_service.pandalens_db import save_moment, get_all_moments, delete_all_moments
from Database import tables
from Services.pandalens_service import pandalens_const


@patch('Services.pandalens_service.pandalens_db.image_utility.save_image')
@patch('Services.pandalens_service.pandalens_db.file_utility.get_path_with_filename')
@patch('Services.pandalens_service.pandalens_db.file_utility.get_path_from_project_root')
@patch('Services.pandalens_service.pandalens_db.time_utility.get_iso_date_time_str')
@patch('Database.tables.insert_rows_to_table')
def test_save_moment(mock_insert_rows, mock_get_iso_date_time_str, mock_get_path_from_project_root,
                     mock_get_path_with_filename, mock_save_image):
    # Setup mock return values
    mock_get_iso_date_time_str.return_value = "2024-09-01T12:00:00Z"
    mock_get_path_from_project_root.return_value = "/mock_project_root"
    mock_get_path_with_filename.return_value = "/mock_project_root/2024-09-01T12-00-00Z.png"

    # Call the function
    save_moment("Test summary", b"mock_image_data")

    # Assertions
    mock_save_image.assert_called_once_with(filename="/mock_project_root/2024-09-01T12-00-00Z.png",
                                            opencv_frame=b"mock_image_data")
    mock_insert_rows.assert_called_once_with(
        pandalens_const.MOMENTS_TABLE,
        {"image_filename": "2024-09-01T12-00-00Z.png", "summary": "Test summary"}
    )


@patch('Database.tables.get_rows_from_table')
def test_get_all_moments(mock_get_rows_from_table):
    # Setup mock return values
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        ("image1.png", "Summary 1"),
        ("image2.png", "Summary 2")
    ]
    mock_cursor.keys.return_value = ["image_filename", "summary"]
    mock_get_rows_from_table.return_value = mock_cursor

    # Call the function
    result = get_all_moments()

    # Assertions
    expected_result = [
        {"image_filename": "image1.png", "summary": "Summary 1"},
        {"image_filename": "image2.png", "summary": "Summary 2"}
    ]
    assert result == expected_result
    mock_get_rows_from_table.assert_called_once_with(pandalens_const.MOMENTS_TABLE, {})


@patch('Services.pandalens_service.pandalens_db.file_utility.delete_all_files_in_dir')
@patch('Services.pandalens_service.pandalens_db.file_utility.get_path_from_project_root')
@patch('Database.tables.delete_all_rows_from_table')
def test_delete_all_moments(mock_delete_all_rows, mock_get_path_from_project_root, mock_delete_all_files_in_dir):
    # Setup mock return values
    mock_get_path_from_project_root.return_value = "/mock_project_root"

    # Call the function
    delete_all_moments()

    # Assertions
    mock_delete_all_rows.assert_called_once_with(pandalens_const.MOMENTS_TABLE)
    mock_delete_all_files_in_dir.assert_called_once_with("/mock_project_root")
