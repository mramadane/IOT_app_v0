from typing_extensions import ParamSpecKwargs
import datetime
import math
import random
import matplotlib.pyplot as plt
from typing import Any, Dict, List, Tuple, Set
from abc import ABC, abstractmethod

class Connections:
    def __init__(self):
        self.connections = {}
        self.connection_id=1
    def add_connection(self, source_id: int,target_id:int, metadata_source: Dict[str, Any],metadata_target:Dict[str, Any],connection_type=None):
        self.connections[self.connection_id] = {
            "source_device":source_id,
            "target_device":target_id,
            "metadata_source": metadata_source,
            "metadata_target":metadata_target,
            "Connection type":connection_type
        }
        self.connection_id=self.connection_id+1

    def get_connections_for_agent(self, agent_id: int) -> Dict[int, Dict[str, Any]]:
      return {
            conn_id: conn_info
            for conn_id, conn_info in self.connections.items()
            if conn_info.get("source_device") == agent_id or conn_info.get("target_device") == agent_id
            }

    def delete_connection(self, connection_id: int):
        if connection_id in self.connections:
            del self.connections[connection_id]
        else:
            raise KeyError(f"Connection {connection_id} not found.")

    def return_all_connections(self) -> List[int]:
        return list(self.connections.keys())
    
    def return_connection(self, target_id: int) -> Dict[str, Any]:
        if target_id in self.connections:
            return self.connections[target_id]
        else:
            raise KeyError(f"Connection with id {target_id} not found.")
