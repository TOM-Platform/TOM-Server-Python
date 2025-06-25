from Utilities import logging_utility
from Database import tables
from .aiget_service_config import AigetConfig

_logger = logging_utility.setup_logger(__name__)


def save_knowledge(knowledge):
    if not knowledge:
        _logger.error("[DB] Knowledge is empty, not saving knowledge")
        return
    _logger.debug("[DB] Saving knowledge")

    knowledge_json = {AigetConfig.DB_KNOWLEDGE_SUMMARY_KEY: knowledge}
    tables.insert_rows_to_table(AigetConfig.KNOWLEDGE_TABLE, knowledge_json)


def get_recent_knowledge(number_of_rows):
    _logger.debug("[DB] Getting recent knowledge")
    cursor = tables.get_ordered_rows_with_limit(AigetConfig.KNOWLEDGE_TABLE, {}, order_by="id", limit=number_of_rows)
    rows = cursor.fetchall()
    columns = cursor.keys()
    result_list = [dict(zip(columns, row)) for row in rows]
    recent_knowledge = [entry["knowledge"] for entry in result_list]
    return recent_knowledge
