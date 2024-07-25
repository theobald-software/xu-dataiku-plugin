import base64
import json
from dataclasses import dataclass
from http.client import HTTPResponse
from io import TextIOWrapper

from typing import Callable, List, Dict, MutableMapping
from urllib.parse import urlencode

from xu.parameterization import RunParameter, RunParameterCollection
from xu.result_table import ResultColumn


@dataclass(frozen=True)
class _URLBuilder:
    _root: str
    _metadata_root: str

    def __init__(self, host: str, port: int, tls_enabled: bool):
        schema = "https://" if tls_enabled else "http://"
        root = f"{schema}{host}:{port}"
        metadata_root = f"{root}/config/extractions"

        object.__setattr__(self, "_root", root)
        object.__setattr__(self, "_metadata_root", metadata_root)

    def get_extractions(self, destination_type: str) -> str:
        return f"{self._metadata_root}?destinationType={destination_type}"

    def get_parameters(self, extraction_name: str) -> str:
        return f"{self._metadata_root}/{extraction_name}/parameters"

    def get_result_columns(self, extraction_name: str) -> str:
        return f"{self._metadata_root}/{extraction_name}/result-columns"

    @staticmethod
    def _get_query_string(run_parameters: RunParameterCollection) -> str:
        all_parameters: [RunParameter] = []

        if run_parameters.ExtractionParameters and len(run_parameters.ExtractionParameters) > 0:
            all_parameters = all_parameters + run_parameters.ExtractionParameters

        if run_parameters.SourceParameters and len(run_parameters.SourceParameters) > 0:
            all_parameters = all_parameters + run_parameters.SourceParameters

        if run_parameters.CustomParameters and len(run_parameters.CustomParameters) > 0:
            all_parameters = all_parameters + run_parameters.CustomParameters

        url_params = dict()

        for tempParam in all_parameters:
            if tempParam.Value and tempParam.Value != tempParam.DefaultValue and len(str(tempParam.Value)) > 0:
                url_params[tempParam.Name] = tempParam.Value

        return urlencode(url_params)

    def get_run(self, extraction_name: str, parameters: Dict[str, str]) -> str:
        query_string = urlencode(parameters)
        url = f"{self._root}/run/{extraction_name}"
        if 0 < len(query_string):
            url += f"?{query_string}"

        return url


@dataclass(frozen=True)
class Client:
    _url_builder: _URLBuilder
    _user: str
    _password: str
    _log_info: Callable[[str], None]
    _log_warning: Callable[[str], None]
    _log_error: Callable[[str], None]

    def __init__(self,
                 host: str,
                 port: int,
                 tls_enabled: bool,
                 user: str,
                 password: str,
                 log_info: Callable[[str], None],
                 log_warning: Callable[[str], None],
                 log_error: Callable[[str], None]) -> None:

        object.__setattr__(self, "_url_builder", _URLBuilder(host, port, tls_enabled))
        object.__setattr__(self, "_user", user)
        object.__setattr__(self, "_password", password)

        object.__setattr__(self, "_log_info", log_info)
        object.__setattr__(self, "_log_warning", log_warning)
        object.__setattr__(self, "_log_error", log_error)

        self._log_info("XtractRequestHandler initialized")

    def _execute_web_request(self, url: str) -> HTTPResponse:
        from urllib import request

        headers: MutableMapping[str, str]
        if (not url.startswith("https://")  # do not send credentials on unencrypted connections
                or self._user is None or "" == self._user):
            headers = {}
        else:
            original_bytes = f"{self._user}:{self._password}".encode()
            b64_bytes = base64.b64encode(original_bytes)
            b64_str = b64_bytes.decode()
            headers = {"Authorization": f"Basic {b64_str}"}

        req = request.Request(url, None, headers)
        return request.urlopen(req)

    def get_extractions(self, destination_type):
        server_url = self._url_builder.get_extractions(destination_type)

        self._log_info(f"Loading extractions from {server_url}")
        response = self._execute_web_request(server_url)
        if response.status == 200:
            content = response.read().decode('utf-8')
            json_data = json.loads(content)
            extractions = json_data.get("extractions", [])

            names = []
            for extraction in extractions:
                names.append(extraction.get("name"))

            return names

    def get_result_columns(self, extraction: str) -> List[ResultColumn]:
        self._log_info("===== XtractRequestHandler.load_extraction_metadata started =====")
        try:
            import ssl
            # Connect to the server
            server_url = self._url_builder.get_result_columns(extraction)

            self._log_info(f"Loading result columns from {server_url}")
            response: HTTPResponse = self._execute_web_request(server_url)

            self._log_info(f"Result columns request finished")

            # Check if the request was successful (status code 200)
            if response.status == 200:
                try:
                    # Parse the JSON data from the response content
                    content = response.read().decode('utf-8')
                    # self._log_info(f"Columns content: '${content}'")
                    json_data = json.loads(content)

                    # Access the list of column dictionaries under the "columns" key
                    columns_data: [ResultColumn] = []

                    for xtract_result_column in json_data.get("columns", []):
                        columns_data.append(
                            ResultColumn(
                                name=xtract_result_column.get("name"),
                                description=xtract_result_column.get("description"),
                                result_type=xtract_result_column.get("type"),
                                length=xtract_result_column.get("length"),
                                decimal_count=xtract_result_column.get("decimalsCount"),
                                is_primary_key=xtract_result_column.get("isPrimaryKey")))
                        # self._log_info(columns_data[-1].to_log_string())

                    return columns_data

                except json.JSONDecodeError as json_error:
                    self._log_error(f"Error parsing JSON: {json_error}")
                    raise json_error
            else:
                self._log_warning(f"Server returned status code {response.status}")
        except Exception as ex:
            self._log_error(f"Error occured during metadata load: {repr(ex)}")
            raise ex
        self._log_info("XtractRequestHandler.load_extraction_metadata finished")

    def get_parameters(self, extraction: str) -> RunParameterCollection:
        self._log_info("===== XtractRequestHandler.get_parameters started =====")
        try:
            # Connect to the server
            server_url = self._url_builder.get_parameters(extraction)

            self._log_info(f"Loading parameters from {server_url}")
            response: HTTPResponse = self._execute_web_request(server_url)
            self._log_info(f"Parameters request finished")

            # Check if the request was successful (status code 200)
            if response.status == 200:
                try:
                    result_collection = RunParameterCollection()

                    content = response.read().decode('utf-8')
                    self._log_info(f"content: '${content}'")
                    json_data = json.loads(content)
                    result_collection.read_from_dictionary(json_data)

                    return result_collection

                except json.JSONDecodeError as json_error:
                    self._log_error(f"Error parsing JSON: {json_error}")
                    raise json_error
            else:
                self._log_warning(f"Server returned status code {response.status}")
                # TODO: raise error
        except Exception as ex:
            self._log_error(f"Error occured during metadata load: {repr(ex)}")
            raise ex

    @staticmethod
    def _parse_csv(response, read_buffer_size):
        # We assume, that the line and column separator will never appear in the payload.
        # That makes CSV parsing quite easy, because we can ignore escaping / quoting, and just split strings.

        # Unfortunately, TextIOWrapper does not like 0x1e as newline symbol.
        # We don't want to load the entire response into memory before splitting lines.
        # Therefore, we need to take care of buffered reading and line splitting.

        text_io_wrapper = TextIOWrapper(buffer=response, encoding="utf-8", newline="")
        line_buffer = ""
        read_count = read_buffer_size
        while read_buffer_size == read_count:
            read_buffer = text_io_wrapper.read(read_buffer_size)
            read_count = len(read_buffer)
            if 0 == read_count:
                break

            lines = read_buffer.split("\x1e")
            lines[0] = line_buffer + lines[0]

            # Line separator is the last symbol of the payload,
            # therefore the last line is either incomplete or empty.
            # This is also true, if there is only one line in the list, i.e. line length > read buffer size.
            line_buffer = lines.pop()

            for line in lines:
                yield line.split("\x1f")

    def run_extraction(
            self,
            extraction: str,
            parameters: Dict[str, str],
            read_buffer_size=0x2000):
        self._log_info("===== XtractRequestHandler.run_extraction started =====")
        try:
            server_url = self._url_builder.get_run(extraction, parameters)

            self._log_info(f"starting extraction {server_url}")
            response: HTTPResponse = self._execute_web_request(server_url)
            self._log_info(f"Start extraction request finished")

            if response.status == 200:
                return self._parse_csv(response, read_buffer_size)
            else:
                raise RuntimeError(f"Response had status code {response.status}")
        except Exception as ex:
            # TODO: no need to catch when just passing up. Remove if no cleanup or the like necessary
            self._log_error(f"Error occured during extraction start: {repr(ex)}")
            raise ex
        finally:
            self._log_info("XtractRequestHandler.run_extraction finished")
