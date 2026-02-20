import inspect
import numpy as np
from functools import wraps
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Callable, Any


@dataclass
class TrackingState:

    active: bool = False
    current_field: str | None = None
    current_dependencies: set = field(default_factory=set)


@dataclass
class Field:

    name: str
    value: Any | None = None
    compute: Callable | None = None

    @property
    def classification(self):
        if isinstance(self.value, (list, np.ndarray)):
            return "array"
        else:
            return "value"

    def __repr__(self):
        if self.classification == "array":
            # Print only the shape/length, not full contents
            try:
                length = len(self.value)
            except TypeError:
                length = "?"
            return f"<Array {self.name}, value length={length}>"
        return f"<Field {self.name}, value={self.value}>"


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

    * We invoke `defaultdict(list)` to create a dictionary of lists. This is used to track the 
      reverse dependencies associated with each field. It might look something like this:

      ```
      [
          ('avg_severity', ['aal', 'simulated_losses']), 
          ('avg_n_claims', ['aal', 'simulated_losses'])
          ...
      ]
      ```

      So the input field `avg_severity` (which is decided by the client) is responsible for the
      computation of the `aal` and `simulated_losses`. The same logic applies to `avg_n_claims`
    * The `tracking_state` attribute is used to (temporarily) log which dependencies are relied
      on in order to calculate each output field
    """
    def __init__(self):
        self.fields = {}
        self.dependents = defaultdict(list)
        self.tracking_state: TrackingState = TrackingState()

    def register(self, field):
        self.fields[field.name] = field

    def set(self, name, value):
        field = self.fields[name]
        field.value = value

    def get(self, name):
        field = self.fields[name]
        if self.tracking_state.active:
            self.tracking_state.current_dependencies.add(name)
        return field.value

    def _build_dependencies(self, field_name):
        field = self.fields[field_name]

        if not field.compute:
            return

        # Enable tracking
        self.tracking_state.active = True
        self.tracking_state.current_field = field_name

        # Execute compute once to discover dependencies
        value = field.compute(model=self)

        # Disable tracking
        self.tracking_state.active = False

        # Store value
        field.value = value

        # Register reverse dependencies
        for dep in self.tracking_state.current_dependencies:
            self.dependents[dep].append(field_name)

        # Reset tracking state
        self.tracking_state = TrackingState()

    def initialise(self):
        
        for name, field in self.fields.items():
            if field.compute:
                self._build_dependencies(name)

    def refresh(self, field_name):
        delta = {}
        queue = deque(self.dependents[field_name])

        while queue:
            field_name = queue.popleft()
            field = self.fields[field_name]

            old_value = field.value
            new_value = field.compute(model=self)

            delta_condition = False
            if field.classification == "array":
                delta_condition = np.sum(old_value) != np.sum(new_value)
            else:
                delta_condition = (new_value != old_value)

            if delta_condition:
                field.value = new_value
                delta[field_name] = new_value
                queue.extend(self.dependents[field_name])

        return delta
