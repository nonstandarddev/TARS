import inspect
import numpy as np
from functools import wraps
from collections import defaultdict, deque
from typing import Any
from .tracking import Tracking
from .field import Field


def with_model_context(func):
    """
    Inject `model` context (state) into key-value arguments at runtime.
    """
    sig = inspect.signature(func)  

    @wraps(func)
    def wrapper(*args, **kwargs):  
        model = kwargs.pop("model", None)  
        if model is not None:
            for name in sig.parameters:  
                if name not in kwargs:
                    kwargs[name] = model.get(name)
        return func(*args, **kwargs)  
    return wrapper  


class Model:
    """
    Creates a 'model' for storing computational results and tracking computational dependencies.

    Note:

    * You may, at any time, access a log of all of the downstream dependencies associated with
      each field by calling on `Model.dependents`,

      ```
      [
          ('avg_severity', ['aal', 'simulated_losses']), 
          ('avg_n_claims', ['aal', 'simulated_losses'])
          ...
      ]
      ```

      In this instance, the input field `avg_severity` (which is decided by the client) is responsible 
      for the computation of the `aal` and `simulated_losses`. The same logic applies to `avg_n_claims`
    * In addition, a full list of fields registered to the model are available by calling on `Model.fields`
    """
    def __init__(self):
        self._fields = {}
        self._dependents = defaultdict(list)
        self._tracking: Tracking = Tracking()

    @property
    def fields(self):
        return self._fields
    
    @property
    def dependents(self):
        return self._dependents

    def register(
        self, 
        field: Field
    ) -> None:
        """
        Add a new field to the `model`
        """
        self._fields[field.name] = field

    def set(self, name, value):
        """
        Set the `value` of a given field (marked by `name`) in the model
        """
        field = self._fields[name]
        field.value = value

    def get(self, name):
        """
        Get the `value` of a given field (marked by `name`) in the model
        """
        field = self._fields[name]
        tracking = self._tracking

        if tracking.active:
            tracking.add_dependency(name)
            
        return field.value

    def _build_dependencies(self, field_name):
        """
        Build a dependency graph for a given `field_name`
        """
        field = self._fields[field_name]
        tracking = self._tracking

        if not field.compute:
            return

        # Enable tracking
        tracking.activate(field_name=field_name)

        # Execute compute once to discover dependencies
        value = field.compute(model=self)

        # Store value
        field.value = value

        # Register reverse dependencies
        for dep in tracking.current_dependencies:
            self._dependents[dep].append(field_name)

        # Reset tracking
        tracking.deactivate()

    def initialise(self):
        """
        Initialise the `model` post field registration - in particular, register the upstream 
        (reverse) dependencies associated with every output field
        """
        for name, field in self._fields.items():
            if field.compute:
                self._build_dependencies(name)

    def refresh(self, input_name: str, input_value: Any) -> dict[str, Any]:
        """
        Refresh all downstream outputs in the `model` that are associated with the input 
        specified by `input_name`

        :param input_name: the name of the affected input field
        :param input_value: the new value of the affected input field
        :return: a dictionary object containing key-value pairs for 'modified' output fields
        """
        delta = {}
        queue = deque(self._dependents[input_name])

        while queue:
            field_name = queue.popleft()
            field = self._fields[field_name]

            old_value = field.value

            self.set(input_name, input_value)
            new_value = field.compute(model=self)

            delta_condition = False
            if field.classification == "array":
                delta_condition = np.sum(old_value) != np.sum(new_value)
            else:
                delta_condition = (new_value != old_value)

            if delta_condition:
                field.value = new_value
                delta[field_name] = new_value
                queue.extend(self._dependents[field_name])

        return delta
