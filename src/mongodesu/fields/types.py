
from mongodesu.mongolib import Model
from typing import Any, Union, List
from datetime import date, datetime
from bson import ObjectId
from . import Field

class StringField(Field[str]):
    def __init__(self, size: int = -1, required: bool = False, unique: bool = False, index: bool = False, default: Union[str, None] = None) -> None:
        super().__init__()
        self.size = size if size > 0 else None
        self.required = required
        self.unique = unique
        self.index = index
        self.default = default
        
    def validate(self, value, field_name: str):
        if not self.required and self.default:
            # print(f"{field_name} value:= {self.default}")
            setattr(self, field_name, self.default)
            value = self.default # for subsequest error test
        if self.required and value is None and (self.default is not None):
            setattr(self, field_name, self.default)
            value = self.default
        if self.required and not value:
            raise ValueError(f"Field {field_name} marked as required and no value provided.")
        if not isinstance(value, str):
            raise ValueError(f"Field {field_name} -> String is expected.")
        if self.size and len(value) > self.size:
            raise ValueError(f"{field_name} size exceeded, max size {self.size}. Provided {len(value)}")
        
    
        
## Number field start
class NumberField(Field[Union[int, float]]):
    def __init__(self, required: bool = False, unique: bool = False, index: bool = False, default: Union[int, float, None] = None) -> None:
        super().__init__()
        self.required = required
        self.unique = unique
        self.index = index
        self.default = default
        
    
    def validate(self, value, field_name):
        if not self.required and not (self.default is None):
            setattr(self, field_name, self.default)
            value = self.default
        if self.required and value is None:
            raise ValueError(f"Field {field_name} marked as required. But does not provide any value")
        if ((not isinstance(value, int)) and (not isinstance(value, float))):
            raise ValueError(f"Field {field_name} Only number value accepted. integer and Float")
    
    

class ListField(Field[List[Any]]):
    def __init__(self, required: bool = False, item_type: Union[Any, None] = None, default: Union[List[Any], None] = None) -> None:
        super().__init__()
        self.required = required
        self.item_type = item_type
        self.default = default

    def validate(self, value, field_name):
        if not self.required and self.default:
            # print(f"{field_name} value:= {self.default}")
            setattr(self, field_name, self.default)
            value = self.default # for subsequest error test
        
        if self.required and not value:
            raise ValueError(f"Field {field_name} marked as required and no value provided.")
        if not isinstance(value, list):
            raise ValueError(f"{field_name} List value expected.")
        if self.item_type:
            for item in value:
                if not isinstance(item, self.item_type):
                    raise ValueError(f"{field_name} List items must be of type {self.item_type.__name__}.")




class DateField(Field):
    def __init__(self, required: bool = False, unique: bool = False, index: bool = False, default: Union[date, datetime, None] = None) -> None:
        super().__init__()
        self.required = required
        self.unique = unique
        self.index = index
        self.default = default

    def validate(self, value, field_name):
        if not self.required and self.default:
            # print(f"{field_name} value:= {self.default}")
            setattr(self, field_name, self.default)
            value = self.default # for subsequest error test
        
        if self.required and value is None:
            raise ValueError(f"Field {field_name} marked as required and no value provided.")
        if not isinstance(value, (date, datetime)):
            raise ValueError(f"{field_name} Date or datetime value expected.")



class BooleanField(Field[bool]):
    def __init__(self, required: bool = False, unique: bool = False, index: bool = False, default: Union[bool, None] = None) -> None:
        super().__init__()
        self.required = required
        self.unique = unique
        self.index = index
        self.default = default

    def validate(self, value, field_name):
        if not self.required and not (self.default is None):
            # print(f"{field_name} value:= {self.default}")
            setattr(self, field_name, self.default)
            value = self.default # for subsequest error test
        
        if self.required and value is None:
            raise ValueError(f"Field {field_name} marked as required and no value provided.")
        if not isinstance(value, bool):
            raise ValueError(f"{field_name} Boolean value expected.")



class ForeignField(Field[Union[str, ObjectId]]):
    def __init__(self, model: Model,  parent_field: str = "_id", required: bool = False, default: Union[str, ObjectId, None] = None, existance_check: bool = False) -> None:
        super().__init__()       
        self.foreign_model = model
        self.required = required
        self.parent_field = parent_field
        self.default = default
        self.existance_check = existance_check
        
        
    def validate(self, value, field_name):
        if not issubclass(self.foreign_model, Model):
            raise Exception("model should be a valid Model class.")
        
        if not self.required and not (self.default is None):
            # print(f"{field_name} value:= {self.default}")
            setattr(self, field_name, self.default)
            value = self.default # for subsequest error test
        
        if self.required and not value:
            raise ValueError(f"{field_name} marked as required. no value provided.")
        if not isinstance(value, str) and not isinstance(value, ObjectId):
            raise ValueError(f"{field_name} should be string or object id instance.")
        if not ObjectId.is_valid(value):
            raise ValueError(f"{field_name} is not a valid objectId")
        
        if self.existance_check is True:
            ## Check if the value is in the model
            model = self.foreign_model()
            exist_data = model.find_one({"_id": value})
            if not exist_data:
                raise ModuleNotFoundError(f"{field_name} equivalant data not found.")
            
 