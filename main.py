from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Callable


@dataclass
class TrackingState:

    active: bool = False
    current_field: str | None = None
    current_dependencies: set = field(default_factory=set)


@dataclass
class Field:

    name: str
    value: any | None = None
    compute: Callable | None = None


class Model:

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
        value = field.compute(self)

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

    def refresh_dependents(self, input_field):
        delta = {}
        queue = deque(self.dependents[input_field])

        while queue:
            field_name = queue.popleft()
            field = self.fields[field_name]

            old_value = field.value
            new_value = field.compute(self)

            if new_value != old_value:
                field.value = new_value
                delta[field_name] = new_value
                queue.extend(self.dependents[field_name])

        return delta
    

if __name__ == "__main__":
    
    def compute_aal(model: Model) -> float:
        return model.get("avg_severity") * model.get("avg_n_claims")
    
    model = Model()

    model.register(Field("avg_severity", 500_000))
    model.register(Field("avg_n_claims", 5))
    model.register(Field("aal", compute=compute_aal))

    model.initialise()

    model.set("avg_severity", 400_000)
    model.refresh_dependents(input_field="avg_severity")

