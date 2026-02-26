import numpy as np
from typing import Any, Callable


class Field:
    """
    Create a `Field`, which represents a 'node' in the computational graph governed
    by an instance of `tarsiflow.Model`

    :param name: the name of the field
    :param default_value: default value for the field (defaults to `None` if not specified)
    :param compute: a callable function with parameters named in accordance to other `Field` objects
    :param from_task: a boolean indicating whether this field is computed from a `task` or not
    """
    def __init__(
        self, 
        name: str, 
        compute: Callable | None = None,
        default_value: Any | None = None, 
        type: str = "value",
        from_task: bool = False
    ):
        self._name = name
        self._value = default_value
        self._compute = compute
        self._from_task = from_task
        self._type = type

    @property
    def sentinel(self):
        return float("nan") if self._type == "value" else np.array([np.nan])

    @property
    def from_task(self):
        return self._from_task

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
        return self._type

    def __repr__(self):
        if self.classification == "array":
            try:
                length = len(self.value)
            except TypeError:
                length = "?"
            return f"<Array {self.name}, length={length}>"
        return f"<Field {self.name}, value={self.value}>"
    