from typing import Dict, Union
class StandardVariable:
    def __init__(self, metadata: Dict[str, Union[str, float, int]], value: Union[str, float, int]):
        self.metadata = metadata
        self.value = value
