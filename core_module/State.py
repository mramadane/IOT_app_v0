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
            "Time": (datetime.timedelta(), False, True)
        }

    def get_states(self, name: str) -> Any:
        return self.states[name][0]

    def set_states(self, name: str, value =None, current_time: datetime.timedelta=None,
                   is_configurable: bool = False, is_readable: bool = False) -> None:
        self.states[name] = (value, is_configurable, is_readable)

    def delete_state(self, name: str, current_time: datetime.timedelta) -> None:
        if name != "Time":
            del self.states[name]
        self.states["Time"] = (current_time, True, True)