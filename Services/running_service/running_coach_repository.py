from datetime import datetime, timedelta
from sqlalchemy import select, func, and_
from Database import database, tables


def get_sessions(date_str: str):
    start_date = datetime.strptime(date_str, '%Y-%m-%d')
    end_date = start_date.replace(hour=23, minute=59, second=59)
    start_timestamp = int(start_date.timestamp() * 1000)
    end_timestamp = int(end_date.timestamp() * 1000)
    RunningExerciseTable = tables.table_dict["RunningExerciseTable"]
    query = (
        select(
            RunningExerciseTable.start_time,
            func.max(RunningExerciseTable.timestamp).label('end_time')
        )
        .where(
            and_(
                RunningExerciseTable.start_time >= start_timestamp,
                RunningExerciseTable.start_time <= end_timestamp
            )
        )
        .group_by(RunningExerciseTable.start_time)
        .order_by(RunningExerciseTable.start_time)
    )
    sessions = database.execute_query(query).fetchall()
    return [{'start_time': session.start_time, 'end_time': session.end_time} for session in sessions]


def get_session_data(session_id: int):
    RunningExerciseTable = tables.table_dict["RunningExerciseTable"]
    query = (
        select(RunningExerciseTable)
        .where(RunningExerciseTable.start_time == session_id)
        .order_by(RunningExerciseTable.timestamp)
    )
    data = database.execute_query(query).fetchall()
    return [row._asdict() for row in data]


def get_available_weeks():
    RunningExerciseTable = tables.table_dict["RunningExerciseTable"]
    # Query to get the earliest timestamp
    query = select(func.min(RunningExerciseTable.timestamp))
    earliest_timestamp = database.execute_query(query).scalar()
    # If no data, return empty list
    if earliest_timestamp is None:
        return []
    # Convert the timestamp to a datetime object, reset the time part
    earliest_date = datetime.fromtimestamp(earliest_timestamp / 1000).replace(
        hour=0, minute=0, second=0, microsecond=0)
    current_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    # Calculate the start of the week for the earliest date
    week_start = earliest_date - timedelta(days=earliest_date.weekday())
    weeks = []
    # Loop through each week from the earliest date to the current date
    while week_start <= current_date:
        week_start_timestamp = int(week_start.timestamp() * 1000)
        week_end_timestamp = int((week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)).timestamp() * 1000)
        # Query to count the data in the current week
        data_count_query = (
            select(func.count())  # pylint: disable=not-callable
            .where(
                and_(
                    RunningExerciseTable.timestamp >= week_start_timestamp,
                    RunningExerciseTable.timestamp <= week_end_timestamp
                )
            )
        )
        data_count = database.execute_query(data_count_query).scalar()
        # If data is found, add the week to the list
        if data_count > 0:
            weeks.append(week_start.strftime('%b %d, %Y'))
        week_start += timedelta(weeks=1)
    return weeks


def get_weekly_calories(week_start: int, week_end: int):
    RunningExerciseTable = tables.table_dict["RunningExerciseTable"]
    subquery = (
        select(
            RunningExerciseTable.start_time,
            func.max(RunningExerciseTable.timestamp).label('max_timestamp')
        )
        .where(
            and_(
                RunningExerciseTable.timestamp >= week_start,
                RunningExerciseTable.timestamp <= week_end
            )
        )
        .group_by(RunningExerciseTable.start_time)
        .subquery()
    )
    query = (
        select(
            func.strftime(
                '%w',
                func.datetime(
                    RunningExerciseTable.timestamp / 1000,
                    'unixepoch'
                )
            ).label('day_of_week'),
            func.sum(RunningExerciseTable.calories).label('total_calories')
        )
        .join(
            subquery,
            and_(
                RunningExerciseTable.start_time == subquery.c.start_time,
                RunningExerciseTable.timestamp == subquery.c.max_timestamp
            )
        )
        .group_by('day_of_week')
        .order_by('day_of_week')
    )
    data = database.execute_query(query).fetchall()
    day_mapping = {1: 'Mon', 2: 'Tue', 3: 'Wed', 4: 'Thu', 5: 'Fri', 6: 'Sat', 0: 'Sun'}
    week_data = []
    for day in range(1, 8):
        adjusted_day = day % 7
        day_data = next((row for row in data if int(row.day_of_week) == adjusted_day), None)
        total_calories = day_data.total_calories if day_data else 0
        week_data.append({
            'day': day_mapping[adjusted_day],
            'total_calories': total_calories
        })
    return week_data
