import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base

from Database import tables
from Utilities.file_utility import read_file_names, read_json_file
from Utilities import environment_utility

_TABLE_NAME_JSON_KEY = "table_name"
_PRIMARY_KEY_JSON_KEY = "primary_key"
_COLUMN_JSON_KEY = "columns"
_COLUMN_NAME_JSON_KEY = "name"
_COLUMN_TYPE_JSON_KEY = "type"
_COLUMN_NULLABLE_JSON_KEY = "nullable"
_COLUMN_UNIQUE_JSON_KEY = "unique"

# NOTE: For more supported datatypes, see https://docs.sqlalchemy.org/en/20/core/types.html
_TYPE_LOOKUP = {
    "integer": db.Integer,
    "int64": db.BigInteger,
    "string": db.String,
    "boolean": db.Boolean,
    "datetime": db.DateTime,
    "json": db.JSON,
    "float": db.Float,
    "double": db.Double,
}


class PicklableDeclarativeBase:
    """A wrapper class to make the SQLAlchemy declarative base picklable."""

    def __init__(self, base):
        self.base = base

    def __reduce__(self):
        return (self.__class__, (self.base.__module__, self.base.__name__), None, None
                , iter(self.base._decl_class_registry))


picklable_base = PicklableDeclarativeBase(declarative_base())


class Database:
    """Database class to manage the database connection and table creation."""

    def __init__(self) -> None:

        self.database_url = environment_utility.get_env_string('DATABASE_URL')
        self.database_name = environment_utility.get_env_string('DATABASE_NAME')
        self.is_dev = environment_utility.get_env_string('ENV') == "dev"
        self.models_file_path = environment_utility.get_env_string('MODELS_FILE_PATH')
        self.models_file_extension = environment_utility.get_env_string('MODELS_FILE_EXT')

        if self.is_dev:
            self.db_path = f"{self.database_url}/{self.database_name}.db"
        else:
            # NOTE: Example Path => postgresql+psycopg2://user:user@localhost:3000/TOM
            self.db_path = f"{self.database_url}/{self.database_name}"
        self.base = picklable_base.base
        self.engine = db.create_engine(self.db_path, echo=True)

    def create_all_tables(self):
        """Create all tables defined in the JSON model files."""
        json_model_file_names = read_file_names(self.models_file_path, self.models_file_extension, prefix=None)

        for filename in json_model_file_names:
            table_spec = read_json_file(filename)

            TableClass = self.create_table(table_spec)
            tables.insert_to_table_dict(table_name=table_spec[_TABLE_NAME_JSON_KEY], table_class=TableClass)

        self.base.metadata.create_all(self.engine)

    def create_table(self, table_spec):
        """
        Dynamically create a table class based on the provided JSON specification.
        Ref: https://github.com/sqlalchemy/sqlalchemy/discussions/7289#discussioncomment-1588530
        """
        cls_dict = {"__tablename__": table_spec[_TABLE_NAME_JSON_KEY]}

        pk = table_spec[_PRIMARY_KEY_JSON_KEY]

        for column in table_spec[_COLUMN_JSON_KEY]:
            cls_dict.update({column[_COLUMN_NAME_JSON_KEY]: db.Column(
                _TYPE_LOOKUP[column[_COLUMN_TYPE_JSON_KEY]],
                primary_key=(pk == column[_COLUMN_NAME_JSON_KEY]),
                nullable=column[_COLUMN_NULLABLE_JSON_KEY],
                unique=column[_COLUMN_UNIQUE_JSON_KEY])
            })

        return type(table_spec[_TABLE_NAME_JSON_KEY], (self.base,), cls_dict)

    def execute_query(self, stmt):
        """Execute the given SQL statement using the database connection."""
        result = None
        with self.engine.connect() as conn:
            result = conn.execute(stmt)
            conn.commit()

        return result


tom_db = None


def init():
    """Initialize the database and create all tables."""
    global tom_db

    if tom_db is None:
        tom_db = Database()
        tom_db.create_all_tables()


def execute_query(stmt):
    """Execute a query using the global database connection."""
    global tom_db

    return tom_db.execute_query(stmt)
