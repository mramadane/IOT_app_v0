from core_module.Agent import Agent
from core_module.connections import Connections
import datetime
import math
import random
import matplotlib.pyplot as plt
from typing import Any, Dict, List, Tuple, Set
from abc import ABC, abstractmethod

# Adjusted Scenario class
class Scenario:
    def __init__(self):
        self.agents: List[Agent] = []
        self.connections = Connections()
        self.messages: List[Tuple[int, Any, datetime.timedelta]] = []
        self.simulation_time: datetime.timedelta = datetime.timedelta()
        self.simulation_length: datetime.timedelta = datetime.timedelta()
        self.minimum_step: datetime.timedelta = datetime.timedelta(seconds=1)

    def add_agent(self, agent: Agent) -> None:
        agent.set_id(len(self.agents) + 1)
        self.agents.append(agent)

    def add_connection(self, from_agent_id: int, to_agent_id: int) -> None:
        from_agent = next((a for a in self.agents if a.get_id() == from_agent_id), None)
        to_agent = next((a for a in self.agents if a.get_id() == to_agent_id), None)
        if from_agent and to_agent and from_agent.connector(to_agent.metadata):
            self.connections.add_connection(
                from_agent_id,
                to_agent_id,
                from_agent.metadata,
                to_agent.metadata
            )
            # Update connections for both agents
            from_agent.update_connections(self.connections.get_connections_for_agent(from_agent_id))
            to_agent.update_connections(self.connections.get_connections_for_agent(to_agent_id))
        else:
            raise ValueError("Cannot establish connection between the specified agents.")

    def delete_connection(self, connection_id: int) -> None:
        if connection_id in self.connections.connections:
            conn_info = self.connections.connections[connection_id]
            source_id = conn_info.get("source_device")
            target_id = conn_info.get("target_device")
            self.connections.delete_connection(connection_id)
            # Update connections for involved agents
            source_agent = next((a for a in self.agents if a.get_id() == source_id), None)
            target_agent = next((a for a in self.agents if a.get_id() == target_id), None)
            if source_agent:
                source_agent.update_connections(self.connections.get_connections_for_agent(source_id))
            if target_agent:
                target_agent.update_connections(self.connections.get_connections_for_agent(target_id))
        else:
            raise KeyError(f"Connection {connection_id} not found.")

    def set_simulation_time(self, length: datetime.timedelta) -> None:
        self.simulation_length = length

    def start_simulation(self) -> None:
        for agent in self.agents:
          agent.set_state("Time", self.simulation_time)
          agent.handler()
          self.messages.extend(agent.get_message_out())
        while self.simulation_time < self.simulation_length:
            if not self.messages:
                self.simulation_time += self.minimum_step
                continue
            next_event_time = min(msg[2] for msg in self.messages)
            self.simulation_time = next_event_time
            messages_to_deliver = [msg for msg in self.messages if msg[2] <=( self.simulation_time)]
            self.messages = [msg for msg in self.messages if msg[2] > (self.simulation_time)]
        # Distribute messages to agents
            for msg in messages_to_deliver:
                conn_id, content, _ = msg
                if conn_id in self.connections.connections:
                    conn_info = self.connections.connections[conn_id]
                    target_agent_id = conn_info.get("target_device")
                    target_agent = next((a for a in self.agents if a.get_id() == target_agent_id), None)
                    if target_agent:
                        target_agent.add_message_to_queue(msg)
                else:
                    print(f"Connection {conn_id} not found.")

            # Collect agents that have messages to process
            agents_to_process = [agent for agent in self.agents if (len(agent.queue)>0)]
            # Call handler only on agents with messages
            for agent in agents_to_process:
                agent.handler()
                self.messages.extend(agent.get_message_out())
