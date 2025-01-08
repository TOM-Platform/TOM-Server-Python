from Services.martial_arts_service.martial_arts_const import METRICS_TABLE_NAME
from Database.tables import get_rows_from_table


def get_by_id(session_id):
    existing_row = get_rows_from_table(
        METRICS_TABLE_NAME, {"id": session_id}).fetchone()
    return existing_row


def get_between_date_range(start_unix_timestamp, end_unix_timestamp):
    # Divide Unix timestamps by 1000 to convert them to seconds
    start_date = start_unix_timestamp / 1000
    end_date = end_unix_timestamp / 1000

    # Construct filter condition
    filter_condition = {"datetime": (start_date, end_date)}

    # Call the function to get rows from the table with the given filter condition
    existing_rows = get_rows_from_table(METRICS_TABLE_NAME, filter_condition)

    return existing_rows


def get_period_data(start_date, end_date):
    data = get_between_date_range(start_date, end_date)
    return [row_to_dict(row) for row in data]


def get_session_data_by_id(session_id):
    data = get_by_id(session_id)
    return row_to_dict(data)


def row_to_dict(row):
    # Convert SQLAlchemy Row object to a dictionary
    d = row._asdict()
    return d
