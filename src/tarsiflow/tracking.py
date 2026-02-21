class Tracking:

    def __init__(
        self, 
        active: bool = False, 
        current_field: str | None = None, 
        current_dependencies: set = set()
    ):
        self._active = active
        self._current_field = current_field
        self._current_dependencies = current_dependencies

    @property
    def active(self):
        return self._active
    
    @property
    def current_dependencies(self):
        return self._current_dependencies

    def activate(self, field_name: str):
        self._active = True
        self._current_field = field_name
    
    def deactivate(self):
        self._active = False
        self._current_field = None
        self._current_dependencies = set()

    def add_dependency(self, field_name: str):
        self._current_dependencies.add(field_name)
    