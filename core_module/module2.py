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
