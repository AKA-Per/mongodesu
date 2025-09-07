from typing import TypeVar, Generic
from inspect import isfunction

T = TypeVar('T')

class Field(Generic[T]):
    """
    Base Field class to be inherited by specific field types.
    Handles setting and getting attribute values with validation.
    """
    
    def __init__(self) -> None:
        self.value = None

    def __set_name__(self, owner, name):
        self.private_name = '_' + name
        self.name = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.private_name, self.__get_default_value())

    def __set__(self, obj, value: T):
        if value is None and hasattr(self, "default") and self.default is not None:
            value = self.default if not isfunction(self.default) else self.default()
        
        self.validate(value, self.name)
        setattr(obj, self.private_name, value)

    def validate(self, value: T, field_name: str):
        raise NotImplementedError("Subclasses must implement the validate method.")
    
    def get_distinct_list(self, list1, list2):
        set1 = set(list1)
        set2 = set(list2)
        
        distinct_elements = set2 - set1
        return list(distinct_elements)
    
    def __get_default_value(self):
        if hasattr(self, "default"):
            return self.default if not isfunction(self.default) else self.default()
        return None
    
