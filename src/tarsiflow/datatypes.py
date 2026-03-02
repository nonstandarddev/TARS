import numpy as np
from typing import Callable, Any


class Field:

    def __init__(
        self, 
        name: str, 
        compute: Callable | None = None,
        from_task: bool = False
    ):
        self.compute = compute
        self.from_task = from_task
        self.name = name

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, new_value: str):
        self._name = new_value.lower()
        

class Float(Field):

    def __init__(
        self,
        name: str, 
        compute: Callable | None = None,
        from_task: bool = False,
        default_value: float | None = None
    ):
        super().__init__(
            name=name,
            compute=compute,
            from_task=from_task
        )
        self.sentinel = float("nan")
        self.value = default_value

    @property
    def value(self) -> float:
        return self._value
    
    @value.setter
    def value(self, new_value: float | None):
        self._value = float(new_value) if new_value else self.sentinel

    def __repr__(self):
        return f"<Float {self.name}, value (float) = {self.value}>"
    

class Integer(Field):

    def __init__(
        self,
        name: str, 
        compute: Callable | None = None,
        from_task: bool = False,
        default_value: int | None = None
    ):
        super().__init__(
            name=name,
            compute=compute,
            from_task=from_task
        )
        self.sentinel = 0
        self.value = default_value

    @property
    def value(self) -> int:
        return self._value
    
    @value.setter
    def value(self, new_value: int | None):
        self._value = int(new_value) if new_value else self.sentinel

    def __repr__(self):
        return f"<Integer {self.name}, value (int) = {self.value}>"
    

class String(Field):

    def __init__(
        self,
        name: str, 
        compute: Callable | None = None,
        from_task: bool = False,
        default_value: str | None = None
    ):
        super().__init__(
            name=name,
            compute=compute,
            from_task=from_task
        )
        self.sentinel = ""
        self.value = default_value

    @property
    def value(self) -> str:
        return self._value
    
    @value.setter
    def value(self, new_value: str | None):
        self._value = str(new_value) if new_value else self.sentinel

    def __repr__(self):
        return f"<String {self.name}, value (str) = {self.value}>"
    

class Array(Field):

    def __init__(
        self,
        name: str, 
        compute: Callable | None = None,
        from_task: bool = False,
        default_value: np.ndarray | None = None
    ):
        super().__init__(
            name=name,
            compute=compute,
            from_task=from_task
        )
        self.sentinel = np.array([np.nan])
        self.value = default_value

    @property
    def length(self):
        return len(self.value)

    @property
    def value(self) -> np.ndarray:
        return self._value
    
    @value.setter
    def value(self, new_value: np.ndarray | None):
        self._value = np.array(new_value) if new_value is not None else self.sentinel

    def __repr__(self):
        return f"<Array (float) {self.name}, length={self.length}>"


class List(Field):

    def __init__(
        self,
        name: str, 
        compute: Callable | None = None,
        from_task: bool = False,
        default_value: list[Any] | None = None,
        classifier: Callable = dict
    ):
        super().__init__(
            name=name,
            compute=compute,
            from_task=from_task
        )
        self.sentinel = list()
        self.subclass = classifier
        self.value = default_value

    @property
    def length(self):
        return len(self.value)

    @property
    def value(self) -> list:
        return self._value
    
    @value.setter
    def value(self, new_value: list | None):
        self._value = [self.subclass(**item) for item in new_value] if len(new_value) > 0 else self.sentinel

    def __getitem__(self, index: int) -> Any:
        return self.value[index]
    
    def __setitem__(self, index: int, new_value: Any):
        self.value[index] = new_value

    def append(self, new_item: Any):
        classified = self.subclass(new_item)
        self.value.append(classified)

    def __repr__(self):
        return f"<List ({self.subclass}) {self.name}, length={self.length}>"


__all__ = [
    "Float",
    "Integer",
    "String",
    "Array",
    "List"
]


if __name__ == '__main__':
    pass