from core_module.Agent import Agent
from core_module.Scenario import Scenario
from core_module.Checker import Checker
import datetime
import math
import random
import matplotlib.pyplot as plt
from typing import Any, Dict, List, Tuple, Set
from abc import ABC, abstractmethod

class EnvironmentAgent(Agent):
    def __init__(self):
        super().__init__()
        # Room and wall properties
        self.set_state("RoomTemperature", 10.0)  # Initial room temperature in Celsius
        self.set_state("WallInsideTemperature", 10.0)  # Initial inside wall temperature in Celsius
        self.set_state("WallOutsideTemperature", 5.0)  # Initial outside wall temperature in Celsius
        self.set_state("RoomVolume", 60)  # Room volume in m^3
        self.set_state("WallArea", 19)  # Wall area in m^2
        self.set_state("WallUValue", 0.081)  # U-value for the wall (W/m^2·K)
        self.set_state("WindowArea", 7)  # Window area in m^2
        self.set_state("WindowUValue", 0.9)  # U-value for the window (W/m^2·K)
        
        # Air properties
        self.set_state("AirDensity", 1.225)  # Air density in kg/m^3
        self.set_state("AirSpecificHeat", 1007)  # Air specific heat in J/kg·K
        self.set_state("AirExchangeRate", 0.7)  # Air changes per hour

        # Environment properties
        self.set_state("OutsideTemperature", 0.0)  # Outside temperature in Celsius        
        # Time tracking
        self.set_state("Time", datetime.timedelta())  # Current simulation time

        # Heating system properties
        self.set_state("NominalHeatOutput", 2700)  # Nominal heat output of the radiator in Watts
        self.set_state("HeatingExponent", 1.3)  # Heating exponent for the radiator
        self.set_state("SupplyTemperature", 70.0)  # Supply water temperature in Celsius
        self.set_state("ReturnTemperature", 50.0)  # Return water temperature in Celsius
        self.set_state("ControlSignal", 1.0)        
        # Convection coefficients (W/m^2·K)
        self.set_state("InsideConvectionCoefficient", 8.0)  # W/m^2·K for inside convection
        self.set_state("OutsideConvectionCoefficient", 25.0)  # W/m^2·K for outside convection

        # Wall material properties
        self.set_state("WallDensity", 2400)  # Density of the wall material (kg/m^3)
        self.set_state("WallSpecificHeat", 880)  # Specific heat capacity of the wall material (J/kgK)
        self.set_state("WallThickness", 0.25)  # Thickness of the wall in meters
        self.set_state("CummulativeConsumption",[])
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
            message = self.queue.pop(0)
            conn_id_r, content, msg_time = message

            if isinstance(content, dict):
                if "sensing" in content and content["sensing"].get("message_type") == "request":
                    self.update_room_temperature(msg_time)
                    temperature = self.get_state("RoomTemperature")
                    for conn_id, conn_info in self.connections.items():
                        target_agent_meta = conn_info["metadata_target"]
                        if target_agent_meta.get("device_name") == "TempSensor":
                            self.send_message((conn_id, {"sensing": {"temperature": temperature}}, msg_time))
            if isinstance(content, dict):
                if "actuating" in content:
                    self.update_room_temperature(msg_time)
                    control_signal=content["actuating"].get("ControlSignal")
                    control_signal = max(0, min(control_signal, 1)) if 0 < control_signal < 1 else control_signal
                    self.set_state("ControlSignal",control_signal)
            self.set_state("Time", msg_time)

    def update_room_temperature(self, current_time: datetime.timedelta):
        # Calculate time elapsed since last update
        last_update = self.get_state("Time")
        dt_total = (current_time - last_update).total_seconds()

        if dt_total > 0:
            # Split the total time step into 1-second increments
            dt_step = 1  # 1-second time step
            time_remaining = dt_total

            # Loop over each 1-second interval until we reach dt_total
            while time_remaining > 0:
                # Calculate dt for this iteration (either 1 second or the remaining time if less than 1 second)
                dt = min(dt_step, time_remaining)
                time_remaining -= dt

                # Get current temperatures and other properties
                room_temp = self.get_state("RoomTemperature")
                wall_inside_temp = self.get_state("WallInsideTemperature")
                outside_temp = self.get_state("OutsideTemperature")
                heating_power = self.calculate_heating_power()

                # Cap heating power to prevent negative or complex values
                if isinstance(heating_power, complex):
                    print("CRITICAL ERROR")
                    heating_power = max(0, heating_power.real)
                else:
                    heating_power = max(0, heating_power)

                # Calculate internal convection (room air to wall inside surface)
                inside_convection_coefficient = self.get_state("InsideConvectionCoefficient")
                wall_area = self.get_state("WallArea")
                Q_in_convection = inside_convection_coefficient * wall_area * (room_temp - wall_inside_temp)

                # Calculate ventilation heat loss
                air_volume_flow = self.get_state("RoomVolume") * self.get_state("AirExchangeRate") / 3600  # m^3/s
                air_density = self.get_state("AirDensity")
                air_specific_heat = self.get_state("AirSpecificHeat")
                H_V = air_density * air_specific_heat * air_volume_flow
                Q_ventilation = H_V * (room_temp - outside_temp)

                # Calculate net heat flow (including heating power)
                Q_net = heating_power - (Q_in_convection + Q_ventilation)  # Adjusted to ensure heat lost is subtracted

                # Calculate temperature change in the room
                thermal_mass_air = air_density * air_specific_heat * self.get_state("RoomVolume")
                temp_change = (Q_net / thermal_mass_air) * dt

                # Apply sanity checks for temperature
                if abs(temp_change) > 100:
                    print("WARNING: Large temperature change detected. Check time step or heat flow.")
                    temp_change = 0

                # Update room temperature
                new_room_temp = room_temp + temp_change
                self.set_state("RoomTemperature", new_room_temp)

                # Calculate wall volume based on thickness and area
                wall_thickness = self.get_state("WallThickness")
                wall_density = self.get_state("WallDensity")
                wall_specific_heat = self.get_state("WallSpecificHeat")
                wall_volume = wall_area * wall_thickness  # Volume of the wall (m^3)

                # Update inside wall temperature based on thermal mass and heat transfer
                dT_AW = (Q_in_convection * dt) / (wall_volume * wall_density * wall_specific_heat)
                new_wall_inside_temp = wall_inside_temp + dT_AW
                self.set_state("WallInsideTemperature", new_wall_inside_temp)

            # Once we have iterated over all time steps, update the simulation time
            #print(f"NEW ROOM TEMPERATRE {new_room_temp}")            
            #print(f"QNET {Q_net}")            
            #print(f"Q_vent {Q_ventilation}")            
            #print(f"Q_TRANS {Q_in_convection}")            
            #print(f"HEATING POWER {heating_power}")
            self.set_state("Time", current_time)

    def calculate_heating_power(self):
        # Calculate the heating power based on supply and return water temperatures
        supply_temp = self.get_state("SupplyTemperature")
        return_temp = self.get_state("ReturnTemperature")
        room_temp = self.get_state("RoomTemperature")
        nominal_output = self.get_state("NominalHeatOutput")
        heating_exponent = self.get_state("HeatingExponent")
        control_signal=self.get_state("ControlSignal")
        # Calculate DeltaTOperation using LMTD (log mean temperature difference)
        delta_t_operation = ((supply_temp - return_temp)) / (math.log((supply_temp - room_temp) / (return_temp - room_temp)))

        # Calculate actual heating power
        heating_power = control_signal*nominal_output * (delta_t_operation / 49.8) ** heating_exponent
        cummulative_port=self.get_state("CummulativeConsumption")
        cummulative_port.append((self.get_state("Time"),heating_power))
        self.set_state("CummulativeConsumption",cummulative_port)
        # Store heating power in the state and return it
        self.set_state("HeatingPower", heating_power)
        return heating_power







class SensorAgent(Agent):
    def __init__(self):
        super().__init__()
        self.set_state("SamplingInterval", datetime.timedelta(minutes=1))
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
        self.set_state("ControlSignal", 1)
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
            control_signal = bluetooth_data.get("ControlSignal")
            if control_signal is not None:
                # Update supply and return temperatures based on control signal
                # This is a simplification; in reality, you'd have a more complex model
                self.set_state("ControlSignal", control_signal)

                # Send actuation command to environment
                for conn_id in self.connections:
                    self.send_message((conn_id, {"actuating": {
                        "ControlSignal": self.get_state("ControlSignal"),
                    }}, msg_time))
        self.set_state("Time", msg_time)

class ControllerAgent(Agent):
    def __init__(self):
        super().__init__()
        self.set_state("TargetTemperature", 22.0)  # Target room temperature in Celsius
        self.set_state("Time", datetime.timedelta())  # Last time the handler was called
        self.set_state("LastControlTime", datetime.timedelta())  # Last time a control signal was sent
        self.set_state("ControlInterval", datetime.timedelta(minutes=5))  # Control interval
        self.set_state("TemperatureData", [])  # List to store (time, temperature) pairs
        self.set_state("isSmart",False)
        self.set_state("ServerCommunicationTime", datetime.timedelta(hours=24))  # Next communication with server
        self.set_state("OccupancySchedule", [1] * 48)  # Default schedule (home all the time)
        self.set_state("ControlData",[])
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
         return "Bluetooth" in target_metadata.get("protocols", {}) or "WiFi" in target_metadata.get("protocols", {})

    def handler(self):
        while self.queue:
            message = self.queue.pop(0)
            conn_id, content, msg_time = message
            if isinstance(content, dict) and "protocols" in content:
                if "Bluetooth" in content["protocols"]:
                  bluetooth_data = content["protocols"].get("Bluetooth", {})
                  temperature = bluetooth_data.get("temperature")
                  if temperature is not None:
                      # Store temperature data
                      temp_data = self.get_state("TemperatureData")
                      temp_data.append((msg_time, temperature))
                      self.set_state("TemperatureData", temp_data)

                      # Check if it's time to compute a new control signal
                      if msg_time - self.get_state("LastControlTime") >= self.get_state("ControlInterval"):
                          control_signal = self.compute_control_signal(temperature)
                          control_data=self.get_state("ControlData")
                          control_data.append((msg_time,control_signal))
                          self.set_state("ControlData",control_data)
                          # Send control signal to actuator
                          for conn_id in self.connections:
                              self.send_message((conn_id, {
                                  "protocols": {
                                      "Bluetooth": {
                                          "ControlSignal": control_signal
                                      }
                                  }
                              }, msg_time))

                          self.set_state("LastControlTime", msg_time)
                if "WiFi" in content["protocols"] and (self.get_state("IsSmart") and msg_time >= self.get_state("ServerCommunicationTime")):
                    if "schedule" in content["protocols"]["WiFi"]:
                        # We've received a schedule from the server
                        new_schedule = content["protocols"]["WiFi"]["schedule"]
                        self.set_state("OccupancySchedule", new_schedule)
            self.set_state("Time", msg_time)

    def compute_control_signal(self, current_temperature: float) -> int:
        """On/Off controller logic"""
        target_temp = self.get_state("TargetTemperature")

        # On/Off control logic: if the current temperature is below target, turn on the heating (ControlSignal = 1)
        if current_temperature < target_temp:
            control_signal = 1  # Turn on heating
        else:
            control_signal = 0  # Turn off heating

        return control_signal

class ServerAgent(Agent):
    def __init__(self):
        super().__init__()
        self.set_state("Time", datetime.timedelta())  # Track server time
        self.metadata = {
            "device_name": "Server",
            "manufacturer": "ScheduleServerCo",
            "protocols": {
                "WiFi": {
                    "supported_protocols": ["802.11n"],
                    "encryption": "WPA2",
                }
            }
        }

    def connector(self, target_metadata: Dict[str, Any]) -> bool:
        return "WiFi" in target_metadata.get("protocols", {})

    def handler(self):
        while self.queue:
            message = self.queue.pop(0)
            conn_id_r, content, msg_time = message

            # Check for a WiFi protocol request to send the schedule
            if isinstance(content, dict) and "protocols" in content and "WiFi" in content["protocols"]:
                if content["protocols"]["WiFi"].get("request_schedule"):
                    # The controller requested the schedule via WiFi
                    print("Request received. Generating schedule...")
                    schedule = self.generate_schedule()
                    # Send schedule to the controller via WiFi
                    self.send_message((conn_id_r, {
                        "protocols": {
                            "WiFi": {
                                "schedule": schedule
                            }
                        }
                    }, msg_time))
            self.set_state("Time", msg_time)

    def generate_schedule(self):
        # Schedule: binary array (48 intervals of 30 minutes over 24 hours)
        schedule = np.ones(48)  # Initially, assume occupants are home
        
        # Generate realistic patterns for 7 days
        for day in range(5):  # For weekdays
            not_home_hours = np.random.normal(loc=10, scale=1)  # Average 10 hours not home, with some variance
            not_home_intervals = int(not_home_hours * 2)  # Convert hours to 30-minute intervals
            start_interval = random.randint(0, 48 - not_home_intervals)
            schedule[start_interval:start_interval + not_home_intervals] = 0  # Mark not-home periods as 0

        for day in range(2):  # For weekends
            not_home_hours = np.random.normal(loc=4, scale=0.5)  # Average 4 hours not home, with some variance
            not_home_intervals = int(not_home_hours * 2)  # Convert hours to 30-minute intervals
            start_interval = random.randint(0, 48 - not_home_intervals)
            schedule[start_interval:start_interval + not_home_intervals] = 0  # Mark not-home periods as 0

        return schedule.astype(int).tolist() 
