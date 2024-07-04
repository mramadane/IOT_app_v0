from core_module.StandardVariable import StandardVariable
from core_module.State import State
from core_module.Messgae import Message
from core_module.Port import Port
from core_module.Agent import Agent
from core_module.Scheduler import Scheduler
from core_module.IOTsystem import IOTSystem
import random
from Viz.viz import NetworkVisualization

class HeaterAgent(Agent):
    def __init__(self, id: int, target_temperature: float):
        super().__init__(id)
        self.target_temperature = target_temperature
        self.current_temperature = 20.0  # Initial room temperature
        self.heater_value = 0.0  # Heater value between 0 and 1

        # PID controller parameters
        self.kp = 0.1
        self.ki = 0.01
        self.kd = 0.01
        self.integral = 0.0
        self.previous_error = 0.0

        # Initialize the state
        self.states.add_state(StandardVariable({"type": "heater_value"}, self.heater_value))

    def execute(self):
        # Request the internal temperature from the room
        self.send_message(0, StandardVariable({"type": "temperature_request"}, 0.0), self.states.time.value)
        self.schedule_execution(self.states.time.value + 1)

    def handle_port_message(self, port_id: int, standard_variable: StandardVariable):
        if standard_variable.metadata["type"] == "internal_temperature":
            self.current_temperature = standard_variable.value

            # Measure the temperature with random error
            measured_temperature = self.current_temperature * (1 + random.uniform(-0.05, 0.05))
            error = self.target_temperature - measured_temperature

            # PID control
            self.integral += error
            derivative = error - self.previous_error
            self.heater_value += self.kp * error + self.ki * self.integral + self.kd * derivative
            self.heater_value = max(0, min(1, self.heater_value))  # Clamp between 0 and 1

            self.previous_error = error
            print(f"Heater {self.id} measured temperature: {measured_temperature:.2f}C, heater value: {self.heater_value:.2f}")

            # Update state
            self.states.add_state(StandardVariable({"type": "heater_value"}, self.heater_value))

            # Send the heater value to the room
            self.send_message(0, StandardVariable({"type": "heater_value"}, self.heater_value), self.states.time.value)
class RoomTemperatureAgent(Agent):
    def __init__(self, id: int, room_size: float, heat_loss_coefficient: float):
        super().__init__(id)
        self.room_size = room_size
        self.heat_loss_coefficient = heat_loss_coefficient
        self.external_temperatures = [0.0, 0.0, 0.0, 0.0]  # Temperatures on the four walls
        self.internal_temperature = 20.0  # Initial internal temperature
        self.heater_value = 0.0  # Heater value between 0 and 1

        # Initialize the state
        self.states.add_state(StandardVariable({"type": "internal_temperature"}, self.internal_temperature))

    def execute(self):
        # Update internal temperature based on external temperatures and heater value
        average_external_temp = sum(self.external_temperatures) / len(self.external_temperatures)
        heat_loss = self.heat_loss_coefficient * (self.internal_temperature - average_external_temp)
        heater_effect = self.heater_value * 35  # Maximum heater temperature effect

        # Update internal temperature
        self.internal_temperature -= heat_loss
        self.internal_temperature += 10*heater_effect
        print(f"Room {self.id} internal temperature: {self.internal_temperature:.2f}C")

        # Update state
        self.states.add_state(StandardVariable({"type": "internal_temperature"}, self.internal_temperature))
        self.schedule_execution(self.states.time.value + 1)

    def handle_port_message(self, port_id: int, standard_variable: StandardVariable):
        if standard_variable.metadata["type"] == "heater_value":
            self.heater_value = standard_variable.value
        elif standard_variable.metadata["type"] == "temperature_request":
            # Respond with the internal temperature
            self.send_message(port_id, StandardVariable({"type": "internal_temperature"}, self.internal_temperature), self.states.time.value)
        elif standard_variable.metadata["type"] == "external_temperature":
            self.external_temperatures[port_id] = standard_variable.value

    def set_external_temperature(self, wall_index: int, temperature: float):
        self.external_temperatures[wall_index] = temperature

    def get_internal_temperature(self) -> float:
        return self.internal_temperature

class ExternalTemperatureAgent(Agent):
    def __init__(self, id: int):
        super().__init__(id)
        self.daytime_temps = [2.0, 1.0, 0.5, 1.5]  # Daytime temperatures for the four walls
        self.nighttime_temps = [-2.0, -3.0, -4.0, -3.5]  # Nighttime temperatures for the four walls

        # Initialize the state
        self.states.add_state(StandardVariable({"type": "external_temperatures"}, self.daytime_temps))

    def execute(self):
        # Determine the time of day
        hour = (self.states.time.value + 8) % 24  # Simulation starts at 8 AM
        if 6 <= hour < 18:  # Daytime from 6 AM to 6 PM
            external_temperatures = self.daytime_temps
        else:  # Nighttime
            external_temperatures = self.nighttime_temps

        print(f"External temperatures updated to: {external_temperatures}")

        # Send the updated temperatures to the room agent
        for i, temp in enumerate(external_temperatures):
            self.send_message(i, StandardVariable({"type": "external_temperature"}, temp), self.states.time.value)

        # Schedule the next update in 5 hours
        self.schedule_execution(self.states.time.value + 5)

    def handle_port_message(self, port_id: int, standard_variable: StandardVariable):
        pass  # This agent only sends messages

iot_system = IOTSystem(start_time=0)

# Create the room temperature agent
room_agent = RoomTemperatureAgent(id=0, room_size=50.0, heat_loss_coefficient=1)
room_agent.add_port(Port(port_id=0, name="external_temperature_port_0", acceptable_variables=[StandardVariable({"type": "external_temperature"}, 0.0)]))
room_agent.add_port(Port(port_id=1, name="external_temperature_port_1", acceptable_variables=[StandardVariable({"type": "external_temperature"}, 0.0)]))
room_agent.add_port(Port(port_id=2, name="external_temperature_port_2", acceptable_variables=[StandardVariable({"type": "external_temperature"}, 0.0)]))
room_agent.add_port(Port(port_id=3, name="external_temperature_port_3", acceptable_variables=[StandardVariable({"type": "external_temperature"}, 0.0)]))
room_agent.add_port(Port(port_id=4, name="heater_value_port", acceptable_variables=[StandardVariable({"type": "heater_value"}, 0.0)]))
room_agent.add_port(Port(port_id=5, name="temperature_request_port", acceptable_variables=[StandardVariable({"type": "temperature_request"}, 0.0)]))

# Create the heater agent
heater_agent = HeaterAgent(id=1, target_temperature=22.0)
heater_agent.add_port(Port(port_id=0, name="internal_temperature_port", acceptable_variables=[StandardVariable({"type": "internal_temperature"}, 0.0)]))

# Create the external temperature agent
external_temp_agent = ExternalTemperatureAgent(id=2)
for i in range(4):
    external_temp_agent.add_port(Port(port_id=i, name=f"external_temperature_port_{i}", acceptable_variables=[StandardVariable({"type": "external_temperature"}, 0.0)]))

# Add agents to the system
iot_system.add_agent(room_agent)
iot_system.add_agent(heater_agent)
iot_system.add_agent(external_temp_agent)

# Connect room temperature agent ports to the heater agent
iot_system.add_connection(heater_agent.get_id(), 0, room_agent.get_id(), 5)  # Temperature request
iot_system.add_connection(room_agent.get_id(), 4, heater_agent.get_id(), 0)  # Heater value

# Connect external temperature agent ports to the room agent
for i in range(4):
    iot_system.add_connection(external_temp_agent.get_id(), i, room_agent.get_id(), i)  # External temperatures

# Run the simulation for a specified duration
iot_system.run_simulation(duration=24)

# Visualize the network
iot_system.visualize_network()