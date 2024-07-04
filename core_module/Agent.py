from abc import ABC, abstractmethod
from .State import State
from .Messgae import Message
from .Port import Port
from typing import List, Tuple
from .StandardVariable import StandardVariable
from Viz.viz import NetworkVisualization

class Agent(ABC):
    def __init__(self, id: int = None):
        self.id = id
        self.states = State(0)
        self.ports = []
        self.queue = []
        self.scheduler = None

    @abstractmethod
    def execute(self):
        pass

    def handle_message(self, message: Message):
        if message.port_id < len(self.ports) and self.ports[message.port_id].check_metadata(message.standard_variable):
            self.queue.append((message.port_id, message.standard_variable))
            self.process_queue()
        self.states.set_time(message.time)
        print(f"Agent {self.id} received message with time {message.time}")

    def process_queue(self):
        while self.queue:
            port_id, standard_variable = self.queue.pop(0)
            self.handle_port_message(port_id, standard_variable)

    @abstractmethod
    def handle_port_message(self, port_id: int, standard_variable: StandardVariable):
        pass

    def set_id(self, id: int):
        self.id = id

    def get_id(self) -> int:
        return self.id

    def send_message(self, port_index: int, standard_variable: StandardVariable, time: float):
        if port_index < len(self.ports):
            message = Message(port_index, standard_variable, time)
            self.scheduler.schedule_message(self.id, message)

    def set_scheduler(self, scheduler: 'Scheduler'):
        self.scheduler = scheduler

    def schedule_execution(self, time: float):
        if self.scheduler:
            self.scheduler.schedule(self, time)

    def add_port(self, port: Port):
        self.ports.append(port)