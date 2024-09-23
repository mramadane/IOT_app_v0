
from core_module.Agent import Agent
from core_module.Scenario import Scenario
from core_module.Checker import Checker
import datetime
import math
import random
import matplotlib.pyplot as plt
from typing import Any, Dict, List, Tuple, Set
from abc import ABC, abstractmethod
from example_module.scenarioClasses import EnvironmentAgent, ControllerAgent, SensorAgent, ActuatorAgent, ServerAgent

def plot_temperature_vs_time(temperature_data):
    """Plot temperature vs time."""
    # Extract time and temperature values from the data
    times = [data[0].total_seconds() / 3600 for data in temperature_data]  # Convert time to hours
    temperatures = [data[1] for data in temperature_data]

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(times, temperatures, marker='o', linestyle='-', color='b', label='Temperature (Celicius)')
    
    # Adding labels and title
    plt.xlabel('Time (hours)')
    plt.ylabel('Temperature (C)')
    plt.title('Room Temperature vs Time')
    plt.grid(True)
    plt.legend()
    
    # Display the plot
    plt.show()

def initialize_agent_states(agent, initial_states: Dict[str, Any]) -> None:
    """Initialize an agent's states with values from the provided dictionary."""
    for state_name, state_value in initial_states.items():
        agent.set_state(state_name, state_value)

def plot_cumulative_energy_vs_time(energy_data):
    """Plot cumulative energy consumption vs time."""
    times = [data[0].total_seconds() / 3600 for data in energy_data]  # Convert time to hours
    consumptions = [data[1] for data in energy_data]  # Power consumption at each time (in Watts)

    # Calculate cumulative energy consumption in kWh
    cumulative_consumption = []
    total_energy = 0
    for i in range(1, len(times)):
        # Time interval between two data points (in hours)
        time_interval = times[i] - times[i-1]
        
        # Energy = Power (W) * Time (hours) / 1000 to get kWh
        energy = consumptions[i-1] * time_interval / 1000
        total_energy += energy
        cumulative_consumption.append(total_energy)

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(times[1:], cumulative_consumption, marker='o', linestyle='-', color='r', label='Cumulative Energy (kWh)')
    
    # Adding labels and title
    plt.xlabel('Time (hours)')
    plt.ylabel('Cumulative Energy Consumption (kWh)')
    plt.title('Cumulative Energy Consumption vs Time')
    plt.grid(True)
    plt.legend()
    
    # Display the plot
    plt.show()



def main():
    # Define the dictionaries for each agent's initial states (matching the default values from the class definitions)
    reference_structure = {
    "metadata_schema": {
        "device_name": {"type": "string", "required": True},
        "manufacturer": {"type": "string", "required": True},
        "protocols": {"type": "dict", "required": False, "schema": {
            "WiFi": {
                "type": "dict",
                "schema": {
                    "supported_protocols": {"type": "list", "required": True},
                    "frequency": {"type": "number", "required": True},
                    "encryption": {"type": "string", "required": True},
                    "authentication_mechanism": {"type": "string", "required": True},
                    "signal_strength": {"type": "number", "required": False},
                    "bandwidth": {"type": "number", "required": False}
                }
            },
            "Zigbee": {
                "type": "dict",
                "schema": {
                    "supported_protocols": {"type": "list", "required": True},
                    "frequency": {"type": "number", "required": True},
                    "encryption": {"type": "string", "required": True},
                    "channel": {"type": "number", "required": False}
                }
            },
            "Bluetooth": {
                "type": "dict",
                "schema": {
                    "supported_protocols": {"type": "list", "required": True},
                    "encryption": {"type": "string", "required": True},
                    "pairing_mechanism": {"type": "string", "required": True},
                    "range": {"type": "number", "required": False},
                    "max_connections": {"type": "integer", "required": False}
                }
            },
            "Ethernet": {
                "type": "dict",
                "schema": {
                    "supported_protocols": {"type": "list", "required": True},
                    "cable_type": {"type": "string", "required": True},
                    "connector_type": {"type": "string", "required": True},
                    "speed": {"type": "number", "required": False},
                    "ip_address": {"type": "string", "required": False}
                }
            },
            "LoRaWAN": {
                "type": "dict",
                "schema": {
                    "supported_protocols": {"type": "list", "required": True},
                    "frequency_band": {"type": "number", "required": True},
                    "encryption": {"type": "string", "required": True},
                    "range": {"type": "number", "required": False},
                    "spreading_factor": {"type": "number", "required": False}
                }
            },
            "MQTT": {
                "type": "dict",
                "schema": {
                    "supported_protocols": {"type": "list", "required": True},
                    "broker_address": {"type": "string", "required": True},
                    "port": {"type": "integer", "required": True},
                    "authentication_mechanism": {"type": "string", "required": True},
                    "keep_alive_interval": {"type": "number", "required": False},
                    "qos": {"type": "integer", "required": False}
                }
            }
        }},
        "sensing": {"type": "dict", "required": False, "schema": {
            "*": {
                "type": "dict",
                "schema": {
                    "sensor_type": {"type": "string", "required": True},
                    "measurement_range": {"type": "tuple", "required": True},
                    "unit": {"type": "string", "required": True},
                    "resolution": {"type": "number", "required": False},
                    "accuracy": {"type": "number", "required": False},
                    "calibration_date": {"type": "string", "required": False}
                }
            }
        }},
        "actuating": {"type": "dict", "required": False, "schema": {
            "*": {
                "type": "dict",
                "schema": {
                    "actuator_type": {"type": "string", "required": True},
                    "control_signal": {"type": "string", "required": True},
                    "unit": {"type": "string", "required": True},
                    "load_capacity": {"type": "number", "required": False},
                    "response_time": {"type": "number", "required": False}
                }
            }
        }},
        "wired_connections": {"type": "dict", "required": False, "schema": {
            "cable_type": {"type": "string", "required": True},
            "connector_type": {"type": "string", "required": True},
            "speed": {"type": "number", "required": False},
            "ip_address": {"type": "string", "required": False}
        }},
        "custom_protocol": {"type": "string", "required": False}
    }
    }
    environment_initial_states = {
        "RoomTemperature": 10.0,               # Default room temperature in Celsius
        "WallInsideTemperature": 10.0,         # Default inside wall temperature in Celsius
        "WallOutsideTemperature": 5.0,         # Default outside wall temperature in Celsius
        "RoomVolume": 60,                      # Default room volume in cubic meters
        "WallArea": 19,                        # Default wall area in square meters
        "WallUValue": 0.081,                   # Default U-value for the wall (W/m^2·K)
        "WindowArea": 7,                       # Default window area in square meters
        "WindowUValue": 0.9,                   # Default U-value for the window (W/m^2·K)
        "AirDensity": 1.225,                   # Default air density in kg/m^3
        "AirSpecificHeat": 1007,               # Default air specific heat in J/kg·K
        "AirExchangeRate": 0.7,                # Default air changes per hour
        "OutsideTemperature": 0.0,             # Default outside temperature in Celsius
        "NominalHeatOutput": 2700,             # Default nominal heat output of the radiator in Watts
        "HeatingExponent": 1.3,                # Default heating exponent for the radiator
        "SupplyTemperature": 70.0,             # Default supply water temperature in Celsius
        "ReturnTemperature": 50.0,             # Default return water temperature in Celsius
        "ControlSignal": 1.0,                  # Default control signal (1 = full power)
        "InsideConvectionCoefficient": 8.0,    # Default inside convection coefficient (W/m^2·K)
        "OutsideConvectionCoefficient": 25.0,  # Default outside convection coefficient (W/m^2·K)
        "WallDensity": 2400,                   # Default wall material density in kg/m^3
        "WallSpecificHeat": 880,               # Default wall material specific heat capacity in J/kg·K
        "WallThickness": 0.25,                 # Default wall thickness in meters
        "Time": datetime.timedelta()           # Initial simulation time
    }

    sensor_initial_states = {
        "SamplingInterval": datetime.timedelta(minutes=1),  # Default sampling interval
        "Time": datetime.timedelta()                        # Initial simulation time
    }

    actuator_initial_states = {
        "ControlSignal": 1,                 # Default control signal for actuator (1 = full power)
        "Time": datetime.timedelta()        # Initial simulation time
    }

    controller_initial_states = {
        "TargetTemperature": 22.0,                  # Default target room temperature in Celsius
        "ControlInterval": datetime.timedelta(minutes=2),  # Default control interval
        "isSmart": False,                           # Default: Not in smart mode
        "ServerCommunicationTime": datetime.timedelta(hours=24),  # Default communication time with server
        "TemperatureData": [],                      # Empty list to store temperature data
        "LastControlTime": datetime.timedelta(),    # Default: Last control time
        "ControlData": [],                          # Empty list to store control signals
        "Time": datetime.timedelta()                # Initial simulation time
    }

    # Create the agents
    environment = EnvironmentAgent()
    sensor = SensorAgent()
    actuator = ActuatorAgent()
    controller = ControllerAgent()

    # Initialize the states for each agent using the respective dictionaries
    initialize_agent_states(environment, environment_initial_states)
    initialize_agent_states(sensor, sensor_initial_states)
    initialize_agent_states(actuator, actuator_initial_states)
    initialize_agent_states(controller, controller_initial_states)

    # Create a Scenario instance
    scenario = Scenario()

    # Add agents to the scenario
    for agent in [environment, sensor, actuator, controller]:
        scenario.add_agent(agent)

    # Setup connections between agents
    scenario.add_connection(environment.get_id(), sensor.get_id())
    scenario.add_connection(sensor.get_id(), environment.get_id())
    scenario.add_connection(sensor.get_id(), controller.get_id())
    scenario.add_connection(controller.get_id(), actuator.get_id())
    scenario.add_connection(actuator.get_id(), environment.get_id())

    # Set simulation parameters
    simulation_length = datetime.timedelta(days=2)  # Set simulation to 24 hours (can be changed)
    scenario.set_simulation_time(simulation_length)

    # Create a Checker instance (assuming we have a reference_structure)
    checker = Checker(reference_structure)

    # Validate metadata for each agent
    for agent in scenario.agents:
        is_valid, errors = checker.check_metadata(agent.metadata)
        if not is_valid:
            print(f"Invalid metadata for agent {agent.get_id()}:")
            for error in errors:
                print(f"- {error}")
            return  # Exit if any metadata is invalid

    # Run the simulation
    scenario.start_simulation()

    # After the simulation, analyze the results (e.g., print temperature data)
    controller_agent = next(agent for agent in scenario.agents if isinstance(agent, ControllerAgent))
    environment_agent = next(agent for agent in scenario.agents if isinstance(agent, EnvironmentAgent))
    temperature_data = controller_agent.get_state("TemperatureData")
    environment_data = environment_agent.get_state("CummulativeConsumption")
    print("envi data",environment_data)
    print("Temperature data collected by the controller:")
    #for time, temp in temperature_data:
     #   print(f"Time: {time}, Temperature: {temp}°C")
    plot_cumulative_energy_vs_time(environment_data)


if __name__ == "__main__":
    main()
