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


def insert_rows_to_table(table_name, data):
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
    TableClass = table_dict[table_name]

    stmt = db.insert(TableClass).values(data)

    return database.execute_query(stmt)


def get_rows_from_table(table_name, criteria: dict):
    """
    Retrieve rows from the specified table with optional filtering.

    Parameters:
    - table_name: Name of the table to query.
    - criteria: Dictionary of column-value pairs to filter rows.
      - Key: Column Name
      - Value: The value to filter by, or a tuple (start, end) for range queries.

    Example usage:
    - To filter by exact value:
      get_rows_from_table('users', {'name': 'John'})
      
    - To filter by a range (e.g., dates between two values):
      get_rows_from_table('orders', {'order_date': ('2025-01-01', '2025-12-31')})

    Returns:
    - List of rows matching the filter criteria.
    """
    TableClass = table_dict[table_name]

    filters = []
    for col, val in criteria.items():
        # for range queries (e.g. between date range)
        if isinstance(val, tuple):
            start_val, end_val = val
            expr = (getattr(TableClass, col) >= start_val) & (getattr(TableClass, col) <= end_val)
        else:
            expr = getattr(TableClass, col) == val
        filters.append(expr)

    # Construct the select statement
    stmt = db.select(TableClass).where(db.and_(*filters))

    return database.execute_query(stmt)


def get_ordered_rows_with_limit(table_name, criteria: dict, order_by: str = None, limit: int = None):
    """
    Retrieve rows from the specified table with optional filtering, ordering, and limiting.

    Parameters:
    - table_name: Name of the table to query.
    - criteria: Dictionary of column-value pairs to filter rows.
      - Key: Column Name
      - Value: The value to filter by, or a tuple (start, end) for range queries.
    - order_by: Column to order results by in descending order (optional). 
      If specified, results are ordered by this column descending by default.
    - limit: Maximum number of rows to return (optional).

    Example usage:
    - To filter by exact value and order by 'id' in ascending order:
      get_ordered_rows_from_table('users', {'status': 'active'}, 'id')
      
    - To filter by a date range and limit the results:
      get_ordered_rows_from_table('orders', {'order_date': ('2025-01-01', '2025-12-31')}, 'order_date', 10)

    Returns:
    - List of rows matching the filter, ordered, and limited as specified.
    """
    TableClass = table_dict[table_name]

    filters = []
    for col, val in criteria.items():
        # for range queries (e.g. between date range)
        if isinstance(val, tuple):
            start_val, end_val = val
            expr = (getattr(TableClass, col) >= start_val) & (getattr(TableClass, col) <= end_val)
        else:
            expr = getattr(TableClass, col) == val
        filters.append(expr)

    # Construct the select statement
    stmt = db.select(TableClass).where(db.and_(*filters))

    # Apply ordering if specified
    if order_by:
        stmt = stmt.order_by(getattr(TableClass, order_by).desc())

    # Apply limiting if specified
    if limit:
        stmt = stmt.limit(limit)

    return database.execute_query(stmt)


def update_row_in_table(table_name, data: dict, row_id):
    """
    Update a row in the specified table based on the ID.

    Parameters:
    - table_name: Name of the table to update.
    - data: Dictionary representing the new values for columns.
    - row_id: ID of the row to update.

    Returns:
    - True if the update is successful, False otherwise.
    """
    TableClass = table_dict[table_name]

    # Create a dictionary containing the update data
    update_data = {getattr(TableClass, col): val for col, val in data.items()}

    # Construct the update statement
    stmt = db.update(TableClass).values(update_data).where(getattr(TableClass, "id") == row_id)

    try:
        # Execute the update statement
        database.execute_query(stmt)
        return True
    except Exception as e:
        # Handle the exception if the update fails
        _logger.exception("Error updating row in {table_name}: {exc}", table_name=table_name, exc=e)
        return False


def delete_all_rows_from_table(table_name):
    """
    Delete all rows from the specified table.

    Parameters:
    - table_name: The name of the table from which to delete all rows.

    Returns:
    - The number of rows deleted.
    """
    TableClass = table_dict[table_name]

    # Construct the delete statement
    stmt = db.delete(TableClass)

    try:
        result = database.execute_query(stmt)
        rows_deleted = result.rowcount
        return rows_deleted
    except Exception as e:
        _logger.exception(f"Error deleting rows from {table_name}: {e}")
        return 0
