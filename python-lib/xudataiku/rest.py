from dataclasses import dataclass
from typing import Dict

import xu.rest


@dataclass(frozen=True)
class Client:
    _xu_server_preset: dict
    _xu_client: xu.rest.Client
    _dataiku_types: Dict[str, str]
    _dataiku_meanings: Dict[str, str]

    def _log_info(self, s):
        print(s)
        return

    def _log_warn(self, s):
        print(s)
        return

    def _log_err(self, s):
        print(s)
        return

    def __init__(self, xu_server_preset):
        host = xu_server_preset.get("host")
        tls_enabled = xu_server_preset.get("tlsEnabled")
        custom_port_enabled = xu_server_preset.get("customPortEnabled")
        port = xu_server_preset.get("port") if custom_port_enabled else 8165 if tls_enabled else 8065
        user = xu_server_preset.get("user")
        password = xu_server_preset.get("password")

        object.__setattr__(self, "_xu_server_preset", xu_server_preset)
        object.__setattr__(self, "_xu_client", xu.rest.Client(
            host, port, tls_enabled, user, password, self._log_info, self._log_warn, self._log_err))

        object.__setattr__(self, "_dataiku_types", {
            "Byte": "smallint",  # tinyint is signed 8 bit integer, but byte is unsigned 8 bit integer
            "Short": "smallint",
            "Int": "int",
            "Long": "bigint",
            "Decimal": "string",  # there seems to be no fixed point type
            "Double": "double",
            "NumericString": "string",
            "StringLengthMax": "string",
            "StringLengthUnknown": "string",
            "ByteArrayLengthExact": "string",  # there seems to be no binary / blob type
            "ByteArrayLengthMax": "string",  # there seems to be no binary / blob type
            "ByteArrayLengthUnknown": "string",  # there seems to be no binary / blob type
            "ConvertedDate": "date",
            "Date": "string",
            "Time": "date",
        })

        object.__setattr__(self, "_dataiku_meanings", {
            "Byte": "LongMeaning",
            "Short": "LongMeaning",
            "Int": "LongMeaning",
            "Long": "LongMeaning",
            "Decimal": "DoubleMeaning",
            "Double": "DoubleMeaning",
            "NumericString": "LongMeaning",
            "StringLengthMax": "Text",
            "StringLengthUnknown": "Text",
            "ByteArrayLengthExact": "Text",  # there seems to be no binary / blob meaning
            "ByteArrayLengthMax": "Text",  # there seems to be no binary / blob meaning
            "ByteArrayLengthUnknown": "Text",  # there seems to be no binary / blob meaning
            "ConvertedDate": "Date",
            "Date": "Date",
            "Time": "Date",
        })

    def get_extraction_choices(self):
        names = self._xu_client.get_extractions("Dataiku")

        choices = []
        for name in names:
            choices.append({"value": {"xuServerPreset": self._xu_server_preset, "extractionName": name}, "label": name})

        return {"choices": choices}

    def _to_dataiku_column(self, xu_column):
        xu_result_type = xu_column.result_type
        dataiku_column = {
            "name": xu_column.name,
            "comment": xu_column.description,
            "type": self._dataiku_types[xu_result_type],
            "meaning": self._dataiku_meanings[xu_result_type]
        }

        if "Decimal" == xu_result_type:
            # sign + digits + decimal point
            has_decimal_point = 0 < xu_column.decimal_count
            dataiku_column["maxLength"] = 1 + xu_column.length + (1 if has_decimal_point else 0)
        elif "Date" == xu_result_type:
            dataiku_column["maxLength"] = 8
        elif xu_result_type in ["NumericString", "StringLengthMax"]:
            dataiku_column["maxLength"] = xu_column.length
        elif xu_result_type in ["ByteArrayLengthExact", "ByteArrayLengthMax"]:
            dataiku_column["maxLength"] = xu_column.length * 2

        return dataiku_column

    def get_read_schema(self, extraction_name):
        xu_columns = self._xu_client.get_result_columns(extraction_name)

        dataiku_columns = []
        for xu_column in xu_columns:
            dataiku_columns.append(self._to_dataiku_column(xu_column))

        return {"columns": dataiku_columns}

    def get_parameter_name_choices(self, extraction_name):
        params = self._xu_client.get_parameters(extraction_name)
        choices = []
        for p in params.CustomParameters:
            choices.append({"value": p.Name, "label": p.Name})
        for p in params.ExtractionParameters:
            choices.append({"value": p.Name, "label": p.Description})
        for p in params.SourceParameters:
            choices.append({"value": p.Name, "label": p.Description})

        return {"choices": choices}

    def run_extraction(self, name, dataiku_parameters, dataset_schema, records_limit):
        # print("dataset_schema", dataset_schema)

        column_names = list(map(lambda column: column.get("name"), dataset_schema.get("columns")))
        parameters = {}
        print(dataiku_parameters)
        for p in dataiku_parameters:
            parameters[p.get("paramName")] = p.get("paramValue")

        is_preview = 0 < records_limit
        if is_preview:
            parameters["preview"] = "true"

        csv_rows = self._xu_client.run_extraction(name, parameters)
        columns_count = len(column_names)
        records_count = 0
        for values in csv_rows:
            if is_preview and records_count >= records_limit:
                break

            yield {column_names[i]: values[i] for i in range(0, columns_count)}
            records_count += 1
