import heapq
from .Agent import Agent
from .Messgae import Message
from typing import List, Tuple
from .ScheduleEvent import ScheduledEvent

class Scheduler:
    def __init__(self, start_time: float = 0):
        self.events = []
        self.current_time = start_time
        self.message_queue = []
        self.agents = []

    def add_agent(self, agent):
        self.agents.append(agent)

    def schedule(self, agent: 'Agent', time: float):
        event = ScheduledEvent(time, agent)
        heapq.heappush(self.events, event)

    def schedule_message(self, agent_id: int, message: 'Message'):
        self.message_queue.append((agent_id, message))

    def run(self):
        while self.events or self.message_queue:
            if self.events and (not self.message_queue or self.events[0].time <= self.current_time):
                event = heapq.heappop(self.events)
                self.current_time = event.time
                event.agent.execute()
            elif self.message_queue:
                agent_id, message = self.message_queue.pop(0)
                self.agents[agent_id].handle_message(message)


