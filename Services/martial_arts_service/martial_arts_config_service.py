from DataFormat.ProtoFiles.MartialArts import ma_session_config_data_pb2
from Database import tables
from . import const
from google.protobuf.json_format import MessageToJson, Parse
from .martial_arts_keys import MA_CONFIG_DATA
import json

# Handles saving and loading of user's session config data from database


class MartialArtsConfigService:
    def __init__(self, martial_arts_service) -> None:
        self.martial_arts_service = martial_arts_service

    def save_config(self, config_data) -> None:
        config_data_dict = {"id": const.CONFIG_ROW_ID,
                            "session_config": MessageToJson(config_data)}
        existing_row = tables.get_rows_from_table(const.CONFIG_TABLE_NAME,
                                                  {"id": const.CONFIG_ROW_ID}).fetchone()
        if not existing_row:
            tables.insert_rows_to_table(
                const.CONFIG_TABLE_NAME, config_data_dict)
        else:
            tables.update_row_in_table(
                const.CONFIG_TABLE_NAME, config_data_dict, const.CONFIG_ROW_ID)

    def send_config(self) -> None:
        rows = tables.get_rows_from_table(const.CONFIG_TABLE_NAME,
                                          {"id": const.CONFIG_ROW_ID})
        first_row = rows.fetchone()
        if not first_row:
            return

        saved_config = first_row.session_config
        self.martial_arts_service.send_to_component(websocket_message=Parse(saved_config, ma_session_config_data_pb2.SessionConfigData()),
                                                    websocket_datatype=MA_CONFIG_DATA)
