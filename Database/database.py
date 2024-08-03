import sqlalchemy as db
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.declarative import declarative_base

from Database import tables
from Utilities.file_utility import read_file_names, read_json_file
from Utilities import environment_utility

_DATABASE_URL = environment_utility.get_env_variable('DATABASE_URL')
_DATABASE_NAME = environment_utility.get_env_variable('DATABASE_NAME')
_IS_DEV = environment_utility.get_env_variable('ENV') == "dev"

_MODELS_FILE_PATH = environment_utility.get_env_variable('MODELS_FILE_PATH')
_MODELS_FILE_EXT = environment_utility.get_env_variable('MODELS_FILE_EXT')

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
    "float": db.Float,
    "string": db.String,
    "boolean": db.Boolean,
    "datetime": db.DateTime,
    "json": db.JSON,
    "float": db.Float,
    "double": db.Double,
}


class PicklableDeclarativeBase:
    def __init__(self, base):
        self.base = base

    def __reduce__(self):
        return self.__class__, (self.base.__module__, self.base.__name__), None, None, iter(
            self.base._decl_class_registry)


picklable_base = PicklableDeclarativeBase(declarative_base())


class Database:
    def __init__(self) -> None:
        if _IS_DEV:
            self.db_path = f"{_DATABASE_URL}/{_DATABASE_NAME}.db"
        else:
            # NOTE: Example Path => postgresql+psycopg2://user:user@localhost:3000/TOM
            self.db_path = f"{_DATABASE_URL}/{_DATABASE_NAME}"
        self.base = picklable_base.base
        self.engine = db.create_engine(self.db_path, echo=True)

    def create_all_tables(self):
        json_model_file_names = read_file_names(_MODELS_FILE_PATH, _MODELS_FILE_EXT, prefix=None)

        for filename in json_model_file_names:
            table_spec = read_json_file(filename)

            TableClass = self.create_table(table_spec)
            tables.insert_to_table_dict(table_name=table_spec[_TABLE_NAME_JSON_KEY], table_class=TableClass)

        self.base.metadata.create_all(self.engine)

    def create_table(self, table_spec):
        # NOTE: Referenced from https://github.com/sqlalchemy/sqlalchemy/discussions/7289#discussioncomment-1588530
        cls_dict = {"__tablename__": table_spec[_TABLE_NAME_JSON_KEY]}

        pk = table_spec[_PRIMARY_KEY_JSON_KEY]

        for column in table_spec[_COLUMN_JSON_KEY]:
            cls_dict.update({column[_COLUMN_NAME_JSON_KEY]: db.Column(
                _TYPE_LOOKUP[column[_COLUMN_TYPE_JSON_KEY]],
                primary_key=(True if pk == column[_COLUMN_NAME_JSON_KEY] else False),
                nullable=column[_COLUMN_NULLABLE_JSON_KEY],
                unique=column[_COLUMN_UNIQUE_JSON_KEY])
            })

        return type(table_spec[_TABLE_NAME_JSON_KEY], (self.base,), cls_dict)

    def execute_query(self, stmt):
        result = None
        with self.engine.connect() as conn:
            result = conn.execute(stmt)
            conn.commit()
            conn.close()

        return result


tom_db = None


def init():
    global tom_db

    if not tom_db:
        tom_db = Database()
        tom_db.create_all_tables()


def execute_query(stmt):
    global tom_db

    return tom_db.execute_query(stmt)
