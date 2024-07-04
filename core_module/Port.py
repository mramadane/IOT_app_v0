from .StandardVariable import StandardVariable
from typing import List
class Port:
    def __init__(self, port_id: int, name: str, acceptable_variables: List[StandardVariable]):
        self.port_id = port_id
        self.name = name
        self.acceptable_variables = acceptable_variables

    def check_metadata(self, standard_variable: StandardVariable) -> bool:
        for acceptable_variable in self.acceptable_variables:
            if all(item in standard_variable.metadata.items() for item in acceptable_variable.metadata.items()):
                return True
        return False
