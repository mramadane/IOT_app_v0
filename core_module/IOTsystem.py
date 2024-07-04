from .Agent import Agent
from .Scheduler import Scheduler
from typing import List
from Viz.viz import NetworkVisualization

class IOTSystem:
    def __init__(self, start_time: float = 0):
        self.agents = []
        self.connections = {}
        self.scheduler = Scheduler(start_time)
        self.time = start_time
        self.visualization = NetworkVisualization()

    def add_agent(self, agent: Agent):
        agent.set_id(len(self.agents))
        agent.set_scheduler(self.scheduler)
        self.agents.append(agent)
        self.scheduler.add_agent(agent)
        self.visualization.add_agent(agent.get_id(), type(agent).__name__)

    def add_connection(self, agent1_id: int, port1_index: int, agent2_id: int, port2_index: int):
        connection = ((agent1_id, port1_index), (agent2_id, port2_index))
        if agent1_id in self.connections:
            self.connections[agent1_id].append((port1_index, agent2_id, port2_index))
        else:
            self.connections[agent1_id] = [(port1_index, agent2_id, port2_index)]
        self.check_connections()
        self.visualization.add_connection(
            agent1_id, self.agents[agent1_id].ports[port1_index].name,
            agent2_id, self.agents[agent2_id].ports[port2_index].name
        )

    def delete_connection(self, connection):
        ((agent1_id, port1_index), (agent2_id, port2_index)) = connection
        if agent1_id in self.connections:
            self.connections[agent1_id] = [
                conn for conn in self.connections[agent1_id] if conn != (port1_index, agent2_id, port2_index)
            ]

    def check_connections(self):
        for agent1_id, connections in self.connections.items():
            agent1 = self.agents[agent1_id]
            for port1_index, agent2_id, port2_index in connections:
                agent2 = self.agents[agent2_id]
                if not (0 <= port1_index < len(agent1.ports) and 0 <= port2_index < len(agent2.ports)):
                    raise ValueError("Invalid port index in connection")

    def initialize_system(self):
        for agent in self.agents:
            agent.schedule_execution(self.time)

    def run_simulation(self, duration: float):
        self.initialize_system()
        self.scheduler.run()

    def visualize_network(self):
        self.visualization.draw_network()
