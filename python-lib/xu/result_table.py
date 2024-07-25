class ResultColumn:
    name: str
    result_type: str
    description: str
    length: int
    decimal_count: int
    is_primary_key: bool

    def __init__(self,
                 name: str,
                 description: str,
                 result_type: str,
                 length: int,
                 decimal_count: int,
                 is_primary_key: bool) -> None:
        self.name = name
        self.description = description
        self.result_type = result_type
        self.length = length
        self.decimal_count = decimal_count
        self.is_primary_key = is_primary_key

    def to_log_string(self) -> str:
        return f"""        self.name = {self.name} 
                         self.description = {self.description} 
                         self.result_type = {self.result_type} 
                         self.length = {self.length} 
                         self.decimal_count = {self.decimal_count} 
                         self.is_primary_key = {self.is_primary_key}"""
