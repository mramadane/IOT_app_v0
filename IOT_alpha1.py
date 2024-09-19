
from core_module.Agent import Agent
from core_module.Scenario import Scenario
from core_module.Checker import Checker
from typing_extensions import ParamSpecKwargs
import datetime
import math
import random
import matplotlib.pyplot as plt
from typing import Any, Dict, List, Tuple, Set
from abc import ABC, abstractmethod

class EnvironmentAgent(Agent):
    def __init__(self):
        super().__init__()
        self.set_state("RoomTemperature", 20.0)  # Initial room temperature in Celsius
        self.set_state("DeltaTOperation", 39.15)  # Initial delta T operation
        self.set_state("RoomVolume", 60)  # Room volume in m^3
        self.set_state("WallArea", 19)  # Wall area in m^2
        self.set_state("WindowArea", 7)  # Window area in m^2
        self.set_state("WallUValue", 0.081)  # U-value for the wall
        self.set_state("WindowUValue", 0.9)  # U-value for the window
        self.set_state("AirDensity", 1.225)  # kg/m^3
        self.set_state("AirSpecificHeat", 1007)  # J/kg·K
        self.set_state("AirExchangeRate", 0.7)  # Air changes per hour
        self.set_state("OutsideTemperature", 5.0)  # Outside temperature in Celsius
        self.set_state("HeatingPower", 0.0)  # Initial heating power in Watts
        self.set_state("Time", datetime.timedelta())  # Current simulation time
        self.set_state("NominalHeatOutput", 3761)  # Nominal heat output of the radiator in Watts
        self.set_state("HeatingExponent", 1.3)  # Heating exponent for the radiator
        self.set_state("SupplyTemperature", 70.0)  # Supply water temperature in Celsius
        self.set_state("ReturnTemperature", 50.0)  # Return water temperature in Celsius

        self.metadata = {
            "device_name": "Room",
            "manufacturer": "",
            "sensing": {
                "temperature": {
                    "sensor_type": "Thermistor",
                    "measurement_range": (-20, 50),
                    "unit": "Celsius",
                    "resolution": 0.1
                }
            },
            "actuating": {
                "heating": {
                    "actuator_type": "Rotary actuator",
                    "control_signal": "Analog",
                    "unit": "Watts"
                }
            }
        }

    def connector(self, target_metadata: Dict[str, Any]) -> bool:
        return "sensing" in target_metadata or "actuating" in target_metadata

    def handler(self):
        while self.queue:
            message=self.queue.pop(0)
            conn_id_r, content, msg_time = message
            self.update_room_temperature(msg_time)
            if isinstance(content, dict):
                if "sensing" in content:
                    if content["sensing"].get("message_type") == "request":
                        temperature = self.get_state("RoomTemperature")
                        for conn_id,conn_info in self.connections.items():
                          source_agent_id=conn_info["source_device"]
                          source_agent_meta=conn_info["metadata_source"]                          
                          target_agent_id = conn_info["target_device"]
                          target_agent_meta = conn_info["metadata_target"]
                          if target_agent_meta.get("device_name") == "TempSensor":
                            self.send_message((conn_id, {"sensing": {"temperature": temperature}}, msg_time))
                elif "actuating" in content:
                  pass
                    # Update supply and return temperatures based on actuator input
                    #self.set_state("SupplyTemperature", content["actuating"].get("supply_temperature", self.get_state("SupplyTemperature")))
                    #self.set_state("ReturnTemperature", content["actuating"].get("return_temperature", self.get_state("ReturnTemperature")))
            self.set_state("Time", msg_time)



    def update_room_temperature(self, current_time: datetime.timedelta):
        last_update = self.get_state("Time")
        dt = (current_time - last_update).total_seconds()
        
        if dt > 0:
            room_temp = self.get_state("RoomTemperature")
            outside_temp = self.get_state("OutsideTemperature")
            heating_power = self.calculate_heating_power()

            # Calculate transmission heat loss
            H_T = (self.get_state("WallArea") * self.get_state("WallUValue") + 
                   self.get_state("WindowArea") * self.get_state("WindowUValue"))
            Q_transmission = H_T * (room_temp - outside_temp)

            # Calculate ventilation heat loss
            air_volume_flow = self.get_state("RoomVolume") * self.get_state("AirExchangeRate") / 3600  # m^3/s
            H_V = self.get_state("AirDensity") * self.get_state("AirSpecificHeat") * air_volume_flow
            Q_ventilation = H_V * (room_temp - outside_temp)

            # Calculate net heat flow
            Q_net = heating_power - Q_transmission - Q_ventilation

            # Calculate temperature change
            thermal_mass = self.get_state("AirDensity") * self.get_state("AirSpecificHeat") * self.get_state("RoomVolume")
            temp_change = (Q_net / thermal_mass) * dt

            # Update room temperature
            new_temp = room_temp + temp_change
            self.set_state("RoomTemperature", new_temp)

    def calculate_heating_power(self):
        supply_temp = self.get_state("SupplyTemperature")
        return_temp = self.get_state("ReturnTemperature")
        room_temp = self.get_state("RoomTemperature")
        nominal_output = self.get_state("NominalHeatOutput")
        heating_exponent = self.get_state("HeatingExponent")

        # Calculate DeltaTOperation using LMTD
        delta_t_operation = (supply_temp - return_temp) / math.log((supply_temp - room_temp) / (return_temp - room_temp))

        # Calculate actual heating power
        heating_power = nominal_output * (delta_t_operation / 49.8) ** heating_exponent

        self.set_state("HeatingPower", heating_power)
        return heating_power

class SensorAgent(Agent):
    def __init__(self):
        super().__init__()
        self.set_state("SamplingInterval", datetime.timedelta(minutes=15))
        self.set_state("Time", datetime.timedelta())
        self.metadata = {
            "device_name": "TempSensor",
            "manufacturer": "SensorCo",
            "sensing": {
                "temperature": {
                    "sensor_type": "Thermistor",
                    "measurement_range": (-20, 50),
                    "unit": "Celsius",
                    "resolution": 0.1
                }
            },
            "protocols": {
                "Bluetooth": {
                    "supported_protocols": ["BLE 4.2"],
                    "encryption": "AES-128",
                    "pairing_mechanism": "Passkey"
                }
            }
        }

    def connector(self, target_metadata: Dict[str, Any]) -> bool:
        return ("sensing" in target_metadata or 
                "Bluetooth" in target_metadata.get("protocols", {}))

    def handler(self):
      if(len(self.queue)==0):
        for conn_id, conn_info in self.connections.items():
          if conn_info["source_device"] == self.get_id():
              target_agent_id = conn_info["target_device"]
              target_agent_meta = conn_info["metadata_target"]
              if target_agent_meta.get("device_name") == "Room":
                  self.send_message((conn_id, {"sensing": {"message_type": "request"}}, self.get_state("SamplingInterval")+self.get_state("Time")))
                  break
      else:
        while self.queue:
            message=self.queue.pop(0)
            conn_id_r, content, msg_time = message
            if isinstance(content, dict):
                if "sensing" in content:
                    temperature = content["sensing"].get("temperature")
                    if temperature is not None:
                        # Send temperature data to controller via Bluetooth
                        for conn_id,conn_info in self.connections.items():
                          source_agent_id=conn_info["source_device"]
                          source_agent_meta=conn_info["metadata_source"]                          
                          target_agent_id = conn_info["target_device"]
                          target_agent_meta = conn_info["metadata_target"]
                          #print("the con names",target_agent_meta.get("device_name"))
                          if target_agent_meta.get("device_name") == "TempController":
                             self.send_message((conn_id, {"protocols": {"Bluetooth": {"temperature": temperature}}}, msg_time))
            for conn_id,conn_info in self.connections.items():
              source_agent_id=conn_info["source_device"]
              source_agent_meta=conn_info["metadata_source"]                          
              target_agent_id = conn_info["target_device"]
              target_agent_meta = conn_info["metadata_target"]
              #print("the con names",target_agent_meta.get("device_name"))
              if target_agent_meta.get("device_name") == "Room":                       
                next_sample_time = msg_time + self.get_state("SamplingInterval")
                self.send_message((conn_id, {"sensing": {"message_type": "request"}}, next_sample_time))
        
            # Update the Time state at the end
            self.set_state("Time", msg_time)




class ActuatorAgent(Agent):
    def __init__(self):
        super().__init__()
        self.set_state("SupplyTemperature", 70.0)
        self.set_state("ReturnTemperature", 50.0)
        self.set_state("Time", datetime.timedelta())
        self.metadata = {
            "device_name": "TempActuator",
            "manufacturer": "ActuatorCo",
            "protocols": {
                "Bluetooth": {
                    "supported_protocols": ["BLE 4.2"],
                    "encryption": "AES-128",
                    "pairing_mechanism": "Passkey"
                }
            },
            "actuating": {
                "heating": {
                    "actuator_type": "Rotary actuator",
                    "control_signal": "Analog",
                    "unit": "Celsius"
                }
            }
        }

    def connector(self, target_metadata: Dict[str, Any]) -> bool:
        return ("Bluetooth" in target_metadata.get("protocols", {}) or 
                "actuating" in target_metadata)

    def handler(self):
      while self.queue:
        message=self.queue.pop(0)
        conn_id, content, msg_time = message
        if isinstance(content, dict) and "protocols" in content:
            bluetooth_data = content["protocols"].get("Bluetooth", {})
            control_signal = bluetooth_data.get("control_signal")
            if control_signal is not None:
                # Update supply and return temperatures based on control signal
                # This is a simplification; in reality, you'd have a more complex model
                self.set_state("SupplyTemperature", 70 + control_signal / 100)
                self.set_state("ReturnTemperature", 50 + control_signal / 200)
                
                # Send actuation command to environment
                for conn_id in self.connections:
                    self.send_message((conn_id, {"actuating": {
                        "supply_temperature": self.get_state("SupplyTemperature"),
                        "return_temperature": self.get_state("ReturnTemperature")
                    }}, msg_time))
        self.set_state("Time", msg_time)

class ControllerAgent(Agent):
    def __init__(self):
        super().__init__()
        self.set_state("TargetTemperature", 22.0)  # Target room temperature in Celsius
        self.set_state("Time", datetime.timedelta())  # Last time the handler was called
        self.set_state("LastControlTime", datetime.timedelta())  # Last time a control signal was sent
        self.set_state("ControlInterval", datetime.timedelta(minutes=5))  # Control interval
        self.set_state("Kp", 5)  # Proportional gain
        self.set_state("TemperatureData", [])  # List to store (time, temperature) pairs
        self.metadata = {
            "device_name": "TempController",
            "manufacturer": "ControlCo",
            "protocols": {
                "Bluetooth": {
                    "supported_protocols": ["BLE 4.2"],
                    "encryption": "AES-128",
                    "pairing_mechanism": "Passkey"
                }
            }
        }

    def connector(self, target_metadata: Dict[str, Any]) -> bool:
        return "Bluetooth" in target_metadata.get("protocols", {})

    def handler(self):
      while self.queue:
          message=self.queue.pop(0)
          conn_id, content, msg_time = message
          if isinstance(content, dict) and "protocols" in content:
              bluetooth_data = content["protocols"].get("Bluetooth", {})
              temperature = bluetooth_data.get("temperature")
              if temperature is not None:
                  # Store temperature data
                  temp_data = self.get_state("TemperatureData")
                  temp_data.append((msg_time, temperature))
                  self.set_state("TemperatureData", temp_data)

                  # Check if it's time to compute a new control signal
                  if msg_time - self.get_state("LastControlTime") >= self.get_state("ControlInterval"):
                      supply_temperature = self.compute_control_signal(temperature)
                      
                      # Send control signal to actuator
                      for conn_id in self.connections:
                          self.send_message((conn_id, {
                              "protocols": {
                                  "Bluetooth": {
                                      "control_signal": supply_temperature
                                  }
                              }
                          }, msg_time))
                      
                      self.set_state("LastControlTime", msg_time)
          self.set_state("Time", msg_time) 

    def compute_control_signal(self, current_temperature: float) -> float:
        target_temp = self.get_state("TargetTemperature")
        error = target_temp - current_temperature
        
        # Simple proportional control
        supply_temperature = 75 + self.get_state("Kp") * error
        
        # Limit supply temperature between 50°C and 100°C
        supply_temperature = max(50, min(supply_temperature, 100))
        
        return supply_temperature
def create_agents() -> Tuple[EnvironmentAgent, SensorAgent, ActuatorAgent, ControllerAgent]:
    environment = EnvironmentAgent()
    sensor = SensorAgent()
    actuator = ActuatorAgent()
    controller = ControllerAgent()
    return environment, sensor, actuator, controller

def main():
    # Create a Scenario instance
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
    scenario = Scenario()

    # Create agents
    environment, sensor, actuator, controller = create_agents()
    # Add agents to the scenario
    for agent in [environment, sensor, actuator, controller]:
        scenario.add_agent(agent)

    # Setup connections between agents
    scenario.add_connection(environment.get_id(), sensor.get_id())
    scenario.add_connection(sensor.get_id(),environment.get_id())
    scenario.add_connection(sensor.get_id(), controller.get_id())
    scenario.add_connection(controller.get_id(), actuator.get_id())
    scenario.add_connection(actuator.get_id(), environment.get_id())

    # Set simulation parameters
    simulation_length = datetime.timedelta(hours=2)
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

    # After the simulation, you can analyze the results
    # For example, print the temperature data collected by the controller
    controller_agent = next(agent for agent in scenario.agents if isinstance(agent, ControllerAgent))
    temperature_data = controller_agent.get_state("TemperatureData")
    print("Temperature data collected:")
    for time, temp in temperature_data:
        print(f"Time: {time}, Temperature: {temp} C")

    # You can add more analysis or data visualization here

if __name__ == "__main__":
    main()