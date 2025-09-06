import json
from typing import Any, Dict, Type, TypeVar
T = TypeVar("T", bound="Serializable")

class Serializable:
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert object attributes to a dictionary.
        Subclasses should override if they need custom serialization.
        """
        return self.__dict__

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """
        Create an instance of the class from a dictionary.
        Subclasses should override if they need custom deserialization.
        """
        obj = cls.__new__(cls)  # create instance without calling __init__
        obj.__dict__.update(data)
        return obj

    def to_json(self) -> str:
        """Serialize object to JSON string."""
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls: Type[T], data: str) -> T:
        """Deserialize JSON string to object."""
        return cls.from_dict(json.loads(data))