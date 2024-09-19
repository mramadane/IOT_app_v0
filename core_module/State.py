from typing_extensions import ParamSpecKwargs
import datetime
import math
import random
import matplotlib.pyplot as plt
from typing import Any, Dict, List, Tuple, Set
from abc import ABC, abstractmethod

class States:
    def __init__(self):
        self.states: Dict[str, Tuple[Any, bool, bool]] = {
            "Time": datetime.timedelta()
        }

    def get_state(self, name: str) -> Any:
        return self.states[name]

    def set_state(self, name: str, value =None, current_time: datetime.timedelta=None,
                   is_configurable: bool = False, is_readable: bool = False) -> None:
        self.states[name] = value

    def delete_state(self, name: str, current_time: datetime.timedelta) -> None:
        if name != "Time":
            del self.states[name]