import sqlalchemy as db
from Database import database
from Utilities import logging_utility

table_dict = None

_logger = logging_utility.setup_logger(__name__)

def insert_to_table_dict(table_name, table_class):
    global table_dict

    if table_dict is None:
        table_dict = {}

    table_dict[table_name] = table_class


"""
The required format of the 'data' argument is a dictionary s.t.:
- Key ==> Column Name
- Value ==> Value to insert into Column

I.e. 
{
    "name": "John",
    "age": 10
}
"""
def insert_rows_to_table(table_name, data):
    TableClass = table_dict[table_name]

    stmt = db.insert(TableClass).values(data)

    return database.execute_query(stmt)


"""
The required format of the 'data' argument is a dictionary s.t.:
- Key ==> Column Name
- Value ==> Value to filter by

I.e.
{
    "name": "John",
}
"""
def get_rows_from_table(table_name, data: dict):
    TableClass = table_dict[table_name]

    filters = []
    for col, val in data.items():
        # for range queries (e.g. between date range)
        if isinstance(val, tuple):
            start_val, end_val = val
            expr = (getattr(TableClass, col) >= start_val) & (
                getattr(TableClass, col) <= end_val)
        else:
            expr = (getattr(TableClass, col) == val)
        filters.append(expr)

    stmt = db.select(TableClass).where(db.and_(*filters))

    return database.execute_query(stmt)


"""
Update a row in the specified table based on the ID.

Parameters:
- table_name: Name of the table to update.
- data: Dictionary representing the new values for columns.
- row_id: ID of the row to update.

Returns:
- True if the update is successful, False otherwise.
"""
def update_row_in_table(table_name, data: dict, row_id):
    TableClass = table_dict[table_name]

    # Create a dictionary containing the update data
    update_data = {getattr(TableClass, col): val for col, val in data.items()}

    # Construct the update statement
    stmt = db.update(TableClass).values(update_data).where(
        getattr(TableClass, 'id') == row_id)

    try:
        # Execute the update statement
        database.execute_query(stmt)
        return True
    except Exception as e:
        # Handle the exception if the update fails
        _logger.exception("Error updating row in {table_name}: {exc}", table_name=table_name, exc=e)
        return False
