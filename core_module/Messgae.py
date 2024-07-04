from .StandardVariable import StandardVariable
class Message:
    def __init__(self, port_id: int, standard_variable: StandardVariable, time: float):
        self.port_id = port_id
        self.standard_variable = standard_variable
        self.time = time
