from typing_extensions import ParamSpecKwargs
import datetime
import math
import random
from core_module.State import States
from typing import Any, Dict, List, Tuple, Set
from abc import ABC, abstractmethod

class Agent:
    def __init__(self):
        self.id: int = 0
        self.state: States = States()
        self.connections: Dict[int, Dict[str, Any]] = {}
        self.queue: List[Tuple[int, Any, datetime.timedelta]] = []
        self.out_messages: List[Tuple[int, Any, datetime.timedelta]] = []
        self.metadata: Dict[str, Any] = {}

    def set_state(self, name: str, value: Any) -> None:
        self.state.set_state(name,value)

    def get_state(self, name: str) -> Any:
        return self.state.get_state(name)
    def update_connections(self, new_connections: Dict[int, Dict[str, Any]]) -> None:
        self.connections = new_connections.copy()
    def set_id(self, id: int) -> None:
        self.id = id

    def get_id(self) -> int:
        return self.id

    def add_message_to_queue(self, message: Tuple[int, Any, datetime.timedelta]) -> None:
        self.queue.append(message)

    def send_message(self, message: Tuple[int, Any, datetime.timedelta]) -> None:
        self.out_messages.append(message)

    def get_message_out(self) -> List[Tuple[int, Any, datetime.timedelta]]:
        messages = self.out_messages
        self.out_messages = []
        return messages

    def handler(self) -> None:
        raise NotImplementedError("Handler method must be implemented by subclasses")

    def connector(self, target_metadata: Dict[str, Any]) -> bool:
        raise NotImplementedError("Connector method must be implemented by subclasses")
