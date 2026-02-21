import numpy as np
from typing import Any, Callable


class Field:

    def __init__(self, name: str, default_value: Any | None = None, compute: Callable | None = None):
        self._name = name
        self._value = default_value
        self._compute = compute

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, new_value: str):
        self._name = new_value

    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, new_value: Any | None):
        self._value = new_value

    @property
    def compute(self):
        return self._compute
    
    @compute.setter
    def compute(self, new_value: Callable):
        self._compute = new_value

    @property
    def classification(self):
        if isinstance(self.value, (list, np.ndarray)):
            return "array"
        else:
            return "value"

    def __repr__(self):
        if self.classification == "array":
            try:
                length = len(self.value)
            except TypeError:
                length = "?"
            return f"<Array {self.name}, length={length}>"
        return f"<Field {self.name}, value={self.value}>"
    