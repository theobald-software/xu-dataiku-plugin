from enum import Enum
from typing import List


class RunParameterType(Enum):
    Text = 1
    Number = 2
    Flag = 3
    Binary = 4
    List_String = 5

    @staticmethod
    def string_to_parameter_type(type_string: str):
        if type_string == "Text":
            return RunParameterType.Text
        if type_string == "Number":
            return RunParameterType.Number
        if type_string == "Flag":
            return RunParameterType.Flag
        if type_string == "Binary":
            return RunParameterType.Binary
        if type_string == "List (string)":
            return RunParameterType.List_String

        raise ValueError(f"Unsupported runtime parameter type string '{type_string}'.")


class RunParameter:
    Name: str
    Description: str
    ParameterType: RunParameterType
    DefaultValue: object
    Value: object

    def __init__(self, name: str, description: str, parameter_type: str, default_value: object, value: object) -> None:
        self.Name = name
        self.Description = description
        self.ParameterType = RunParameterType.string_to_parameter_type(parameter_type)
        self.DefaultValue = default_value
        self.Value = value


class RunParameterCollection:
    ExtractionParameters: List[RunParameter]
    SourceParameters: List[RunParameter]
    CustomParameters: List[RunParameter]

    def __init__(self):
        self.ExtractionParameters: [RunParameter] = []
        self.SourceParameters: [RunParameter] = []
        self.CustomParameters: [RunParameter] = []

    def read_from_dictionary(self, parameters_dictionary) -> None:
        self.ExtractionParameters.clear()
        self.SourceParameters.clear()
        self.CustomParameters.clear()

        self.ExtractionParameters = self._read_parameters_from_dict("extraction", parameters_dictionary)
        self.SourceParameters = self._read_parameters_from_dict("source", parameters_dictionary)
        self.CustomParameters = self._read_parameters_from_dict("custom", parameters_dictionary)

    @classmethod
    def create_from_dict(cls, parameter_dictionary: dict) -> "RunParameterCollection":
        result_collection = RunParameterCollection()
        result_collection.read_from_dictionary(parameter_dictionary)
        return result_collection

    @staticmethod
    def _read_parameters_from_dict(parameter_collection_name: str, parameters_dictionary: dict) -> List[RunParameter]:
        result_list: List[RunParameter] = []

        temp_parameter: dict
        for temp_parameter in parameters_dictionary[parameter_collection_name]:
            result_list.append(
                RunParameter(
                    name=temp_parameter.get("name", ""),
                    description=temp_parameter.get("description", ""),
                    parameter_type=temp_parameter.get("type", ""),
                    default_value=temp_parameter.get("default", ""),
                    value=temp_parameter.get("value", "")
                )
            )

        return result_list
