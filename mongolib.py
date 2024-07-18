from pymongo import MongoClient
from pymongo.results import InsertOneResult, InsertManyResult, UpdateResult,DeleteResult
from pymongo.cursor import Cursor, CursorType
from typing import Dict, Any, TypedDict, List, Union
from datetime import date, datetime
import inflect

class AttributeDict(TypedDict):
    type: str
    required: bool
    enum: Any
    unique: bool
    default: Any


class MongoAPI:
    def __init__(self) -> None:
        self.client = MongoClient("mongodb://localhost:27017")
        self.db = self.client['flaskdb']
        
    def read(self)-> Cursor:
        return self.collection.find({})
    
    def insertOne(self, data: Dict[str, Any]) -> InsertOneResult:
        return self.collection.insert_one(data)
    



## NEW WAY TO DEFINE COLLECTION AND MODEL

class Model(MongoAPI):
    def __init__(self, **kwargs) -> None:
        super().__init__()
        for key, value in kwargs.items():
            setattr(self, key, value)
        # print(self.__class__.__dict__.items())
        if self.collection_name is None or self.collection_name == '':
            self.collection_name = self.construct_model_name() # Here I want to get the inherited class name as the collection name.
            
        self.collection = self.db[self.collection_name]

    def save(self):
        items = self.__class__.__dict__.items()
        data: Dict[str, Any] = {}
        for key, value in items:
            if isinstance(value, Field):
                data[key] = getattr(self, key)
        self.insertOne(data=data)
        
    
    def construct_model_name(self):
        inflector = inflect.engine()
        class_name = self.__class__.__name__
        return inflector.plural(class_name.lower())
        

class Field:
    
    def __init__(self) -> None:
        self.value = None

    def __set_name__(self, owner, name):
        self.private_name = '_' + name

    def __get__(self, obj, objtype=None):
        return getattr(obj, self.private_name)

    def __set__(self, obj, value):
        self.validate(value)
        setattr(obj, self.private_name, value)

    def validate(self, value):
        raise NotImplementedError("Subclasses must implement the validate method.")
    
    def get_distinct_list(self, list1, list2):
        set1 = set(list1)
        set2 = set(list2)
        
        distinct_elements = set2 - set1
        return list(distinct_elements)
    
        

class StringField(Field):
    def __init__(self, **kwargs) -> None:
        super().__init__()
        keys = ['size', 'required', 'unique']
        passed_keys = kwargs.keys()
        distinct = self.get_distinct_list(keys, passed_keys)
        if not distinct:
            pass
        else:
            # Some values are present in the list that are not allowed
            message = ', '.join(distinct)
            raise Exception(f"{message} are not allowed")
        
        self.size = kwargs.get('size', None)
        self.required = kwargs.get('required', None)
        self.unique = kwargs.get('unique', False)
        
    def validate(self, value):
        if not isinstance(value, str):
            raise ValueError("String is expected.")
        if self.size and len(value) > self.size:
            raise ValueError(f"String size exceeded, max size {self.size}. Provided {len(value)}")
        if self.required and not value:
            raise ValueError(f"Field marked as required and no value provided.")
        
    
        
## Number field start
class NumberField(Field):
    def __init__(self, **kwargs) -> None:
        super().__init__()
        keys = ['required']
        passed_keys = kwargs.keys()
        distinct = self.get_distinct_list(keys, passed_keys)
        if not distinct:
            pass
        else:
            message = ', '.join(distinct)
            raise Exception(f"{message} are not allowed")
        
        self.required = kwargs.get('required', None)
        
    
    def validate(self, value):
        if (not isinstance(value, int)) and (not isinstance(value, float)):
            raise ValueError("Only number value accepted. integer and Float")
        if self.required and value is None:
            raise ValueError("Field is marked as required. But does not provide any value")
    
    

class ListField(Field):
    def __init__(self, **kwargs) -> None:
        super().__init__()
        keys = ['required', 'item_type']
        passed_keys = kwargs.keys()
        distinct = self.get_distinct_list(keys, passed_keys)
        if distinct:
            message = ', '.join(distinct)
            raise Exception(f"{message} are not allowed")

        self.required = kwargs.get('required', None)
        self.item_type = kwargs.get('item_type', None)

    def validate(self, value):
        if not isinstance(value, list):
            raise ValueError("List value expected.")
        if self.required and not value:
            raise ValueError("Field marked as required and no value provided.")
        if self.item_type:
            for item in value:
                if not isinstance(item, self.item_type):
                    raise ValueError(f"List items must be of type {self.item_type.__name__}.")




class DateField(Field):
    def __init__(self, **kwargs) -> None:
        super().__init__()
        keys = ['required']
        passed_keys = kwargs.keys()
        distinct = self.get_distinct_list(keys, passed_keys)
        if distinct:
            message = ', '.join(distinct)
            raise Exception(f"{message} are not allowed")

        self.required = kwargs.get('required', None)

    def validate(self, value):
        if not isinstance(value, (date, datetime)):
            raise ValueError("Date or datetime value expected.")
        if self.required and value is None:
            raise ValueError("Field marked as required and no value provided.")



class BooleanField(Field):
    def __init__(self, **kwargs) -> None:
        super().__init__()
        keys = ['required', 'unique']
        passed_keys = kwargs.keys()
        distinct = self.get_distinct_list(keys, passed_keys)
        if distinct:
            message = ', '.join(distinct)
            raise Exception(f"{message} are not allowed")

        self.required = kwargs.get('required', None)
        self.unique = kwargs.get('unique', False)

    def validate(self, value):
        if not isinstance(value, bool):
            raise ValueError("Boolean value expected.")
        if self.required and value is None:
            raise ValueError("Field marked as required and no value provided.")
