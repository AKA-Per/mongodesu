from pymongo import MongoClient
from pymongo.results import InsertOneResult, InsertManyResult, UpdateResult, DeleteResult
from pymongo.cursor import Cursor, CursorType
from typing import Dict, Any, Iterable, Mapping, Optional, TypedDict, List, Union
from datetime import date, datetime
import inflect
from pymongo.bulk import RawBSONDocument
from pymongo.client_session import ClientSession
from pymongo.typings import _Pipeline, _CollationIn, Sequence
from pymongo.collection import _IndexKeyHint, _DocumentType
from pymongo.collection import abc

class AttributeDict(TypedDict):
    type: str
    required: bool
    enum: Any
    unique: bool
    default: Any


class MongoAPI:
    """A wraper for all the main crud operation and connection logic for the mongodb.
    """
    def __init__(self) -> None:
        self.client = MongoClient("mongodb://localhost:27017")
        self.db = self.client['flaskdb']
        self.db.users.insert_many()
        
    def find(self, *args, **kwargs)-> Cursor:
        """Finds the list of documents from the collection set in the model

        Returns:
            Cursor: The cursor object of the documents
        """
        return self.collection.find(*args, **kwargs)
    
    def find_one(self, filter: Union[Any, None] = None, *args, **kwargs) -> Cursor:
        """Finds one data from the mongodb based on the filter provided. If no filter provided then the first docs will be returned

        Args:
            filter (Union[Any, None], optional): The filter for to apply in the query of mongodb collection. Defaults to None.

        Returns:
            Cursor: The cursor object of the document returned
        """
        return self.collection.find_one(filter, *args, **kwargs)
    
    def insert_many(self, 
                    documents: Iterable[Union[_DocumentType, RawBSONDocument]], 
                    ordered: bool = True,
                    bypass_document_validation: bool = False,
                    session: Union[ClientSession, None] = None,
                    comment: Union[Any, None] = None) -> InsertManyResult:
        """Insert List of documents to the mongodb collection
            
            >>> db.test.count_documents({})
            0
            >>> result = db.test.insert_many([{'x': i} for i in range(2)])
            >>> result.inserted_ids
            [ObjectId('54f113fffba522406c9cc20e'), ObjectId('54f113fffba522406c9cc20f')]
            >>> db.test.count_documents({})
            2
            
        Args:
            documents (Iterable[Union[_DocumentType, RawBSONDocument]]): The List of dictionary or RawBOSN type document to insert
            ordered (bool, optional): Flag to weather enable the ordered insertion. Defaults to True.
            bypass_document_validation (bool, optional): Flag to disable the validation check. The validation check is defined in the fields of the model. Defaults to False.
            session (Union[ClientSession, None], optional): The transaction session of the mongodb. Defaults to None.
            comment (Union[Any, None], optional): An user defined comment attached to this command. Defaults to None.

        Raises:
            ValueError: If the document provided is not an instance of the `Iterable`

        Returns:
            InsertManyResult: An instance of the `InsertManyResult`
        """
        if not isinstance(documents, abc.Iterable):
            raise ValueError('documents should be an iterable of raybson or documenttype')
        if bypass_document_validation is False:
            self.validate_on_docs(documents)
        return self.collection.insert_many(documents, ordered, bypass_document_validation, session, comment)
    
    def insert_one(self, document: Union[Any, RawBSONDocument], bypass_document_validation: bool = False, 
                   session: Union[ClientSession, None] = None, comment: Union[Any, None] = None) -> InsertOneResult:
        """Insert a document in the mongodb

        Args:
            document (Union[Any, RawBSONDocument]): The document to insert
            bypass_document_validation (bool, optional): The flag to disable the validation. Defaults to False.
            session (Union[ClientSession, None], optional): The transaction session for the insert. Defaults to None.
            comment (Union[Any, None], optional): An user defined comment attached to the command. Defaults to None.

        Returns:
            InsertOneResult: The instance of the `InsertOneResult`
        """
        if bypass_document_validation is False:
            self.validate_on_docs(document)
        return self.collection.insert_one(document, bypass_document_validation, session, comment)
    
    def update_one(
        self,
        filter: Mapping[str, Any],
        update: Union[Mapping[str, Any], _Pipeline],
        upsert: bool = False,
        bypass_document_validation: bool = False,
        collation: Union[_CollationIn, None] = None,
        array_filters: Union[Sequence[Mapping[str, Any]], None] = None,
        hint: Union[_IndexKeyHint, None] = None,
        session: Union[ClientSession, None] = None,
        let: Union[Mapping[str, Any], None] = None,
        comment: Union[Any, None] = None
        ) -> UpdateResult:
        """Update the document based on the filter

        Args:
            filter (Mapping[str, Any]): The filter to add to the query
            update (Union[Mapping[str, Any], _Pipeline]): the data to be updated in the document
            upsert (bool, optional): If set to true then if no data is found then a new document will be created. Defaults to False.
            bypass_document_validation (bool, optional): If set to true to disable the validation check on the data. Defaults to False.
            collation (Union[_CollationIn, None], optional): _description_. Defaults to None.
            array_filters (Union[Sequence[Mapping[str, Any]], None], optional): _description_. Defaults to None.
            hint (Union[_IndexKeyHint, None], optional): _description_. Defaults to None.
            session (Union[ClientSession, None], optional): _description_. Defaults to None.
            let (Union[Mapping[str, Any], None], optional): _description_. Defaults to None.
            comment (Union[Any, None], optional): _description_. Defaults to None.

        Returns:
            UpdateResult: _description_
        """
        if bypass_document_validation is False:
            self.validate_on_docs(update)
        return self.collection.update_one(filter, update, upsert, bypass_document_validation, collation, array_filters, hint, session, let, comment)

    def update_many(
        self,
        filter: Mapping[str, Any],
        update: Union[Mapping[str, Any], _Pipeline],
        upsert: bool = False,
        array_filters: Optional[Sequence[Mapping[str, Any]]] = None,
        bypass_document_validation: Optional[bool] = None,
        collation: Optional[_CollationIn] = None,
        hint: Optional[_IndexKeyHint] = None,
        session: Optional[ClientSession] = None,
        let: Optional[Mapping[str, Any]] = None,
        comment: Optional[Any] = None,
    ) -> UpdateResult:
        if bypass_document_validation is False:
            self.validate_on_docs(update)
            
        return self.collection.update_many(filter, update, upsert, array_filters, bypass_document_validation, collation, hint, session, let, comment)

    
    def delete_one(
        self,
        filter: Mapping[str, Any],
        collation: Optional[_CollationIn] = None,
        hint: Optional[_IndexKeyHint] = None,
        session: Optional[ClientSession] = None,
        let: Optional[Mapping[str, Any]] = None,
        comment: Optional[Any] = None,
    ) -> DeleteResult:
        
        return self.collection.delete_one(filter, collation, hint, session, let, comment)
    
    def delete_many(
        self,
        filter: Mapping[str, Any],
        collation: Optional[_CollationIn] = None,
        hint: Optional[_IndexKeyHint] = None,
        session: Optional[ClientSession] = None,
        let: Optional[Mapping[str, Any]] = None,
        comment: Optional[Any] = None,
    ) -> DeleteResult:
        
        return self.collection.delete_many(filter, collation, hint, session, let, comment)
    
    def validate_on_docs(self, data):
        if isinstance(data, List):
            for doc in data:
                self.validate_data(doc)
        else:
            self.validate_data(data)
    
    def validate_data(self, data):
        for _key, value in data.items():
            setattr(self, _key, value)
        for key, value in self.__class__.__dict__.items():
            if isinstance(value, Field):
                if hasattr(self, key):
                    value.validate(getattr(self, key), key)
                else:
                    value.validate(value=None, field_name=key)


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
                if hasattr(self, key):
                    data[key] = getattr(self, key)
                else:
                    value.validate(None, key) # This will throw an error
                    
            
        if not data:
            raise ValueError('No value provided.')
        self.insert_one(data=data)
        
    
    def construct_model_name(self):
        inflector = inflect.engine()
        class_name = self.__class__.__name__
        return inflector.plural(class_name.lower())
    


class Field:
    
    def __init__(self) -> None:
        self.value = None

    def __set_name__(self, owner, name):
        self.private_name = '_' + name
        self.name = name

    def __get__(self, obj, objtype=None):
        return getattr(obj, self.private_name)

    def __set__(self, obj, value):
        self.validate(value, self.name)
        setattr(obj, self.private_name, value)

    def validate(self, value, field_name):
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
        
    def validate(self, value, field_name):
        if self.required and not value:
            raise ValueError(f"Field {field_name} marked as required and no value provided.")
        if not isinstance(value, str):
            raise ValueError(f"Field {field_name} -> String is expected.")
        if self.size and len(value) > self.size:
            raise ValueError(f"{field_name} size exceeded, max size {self.size}. Provided {len(value)}")
        
    
        
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
        
    
    def validate(self, value, field_name):
        if self.required and value is None:
            raise ValueError(f"Field {field_name} marked as required. But does not provide any value")
        if ((not isinstance(value, int)) and (not isinstance(value, float))):
            raise ValueError(f"Field {field_name} Only number value accepted. integer and Float")
    
    

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

    def validate(self, value, field_name):
        if self.required and not value:
            raise ValueError(f"Field {field_name} marked as required and no value provided.")
        if not isinstance(value, list):
            raise ValueError(f"{field_name} List value expected.")
        if self.item_type:
            for item in value:
                if not isinstance(item, self.item_type):
                    raise ValueError(f"{field_name} List items must be of type {self.item_type.__name__}.")




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

    def validate(self, value, field_name):
        if self.required and value is None:
            raise ValueError(f"Field {field_name} marked as required and no value provided.")
        if not isinstance(value, (date, datetime)):
            raise ValueError(f"{field_name} Date or datetime value expected.")



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

    def validate(self, value, field_name):
        if self.required and value is None:
            raise ValueError(f"Field {field_name} marked as required and no value provided.")
        if not isinstance(value, bool):
            raise ValueError(f"{field_name} Boolean value expected.")
