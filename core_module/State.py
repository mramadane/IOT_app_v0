from .StandardVariable import StandardVariable
from typing import List, Tuple

class State:
    def __init__(self, time: float):
        self.time = StandardVariable({"type": "time"}, time)
        self.standard_variables = []

    def add_state(self, standard_variable: StandardVariable):
        self.standard_variables.append(standard_variable)

    def get_states(self) -> Tuple[List[StandardVariable], StandardVariable]:
        return self.standard_variables, self.time

    def set_time(self, time: float):
        self.time.value = time
