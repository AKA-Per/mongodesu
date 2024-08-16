from bson import ObjectId
from pymongo import MongoClient
from pymongo.results import InsertOneResult, InsertManyResult, UpdateResult, DeleteResult
from pymongo.cursor import Cursor
from pymongo.command_cursor import CommandCursor
from typing import Dict, Any, Iterable, Mapping, Optional, TypedDict, List, Union
from datetime import date, datetime
import inflect
from pymongo.bulk import RawBSONDocument
from pymongo.client_session import ClientSession
from pymongo.typings import _Pipeline, _CollationIn, Sequence
from pymongo.collection import _IndexKeyHint, _DocumentType
from pymongo.collection import abc, Collection
import logging

class AttributeDict(TypedDict):
    type: str
    required: bool
    enum: Any
    unique: bool
    default: Any


class MongoAPI:
    """A wraper for all the main crud operation and connection logic for the mongodb.
    """
    def __init__(self, 
                 host: Union[str, None] = None, 
                 port: Union[int, None] = 27017,
                 uri: Union[str, None] = None,
                 database: Union[str, None] = None) -> None:
        logging.info("MongoAPI instance cretaed")
        if host or uri:
            self.connect_one(host=host, port=port, uri=uri, database=database)        
    
    @classmethod
    def connect(cls, 
                host: Union[str, None] = None, 
                port: Union[int, None] = 27017,
                uri: Union[str, None] = None,
                database: Union[str, None] = None):
        logging.info("Calling the class method connect")
        if uri:
            logging.info(f"Connecting with the URI: {uri}")
            cls.client = MongoClient(host=uri)

        if host:
            logging.info(f"Connecting with the HOST: {host} and PORT: {port}")
            cls.client = MongoClient(host=host, port=port)
        
        if database:
                cls.db = cls.client.get_database(database)
        else:
            cls.db = cls.client.get_database()
            

    
    def connect_one(self,
                host: Union[str, None] = None, 
                port: Union[int, None] = 27017,
                uri: Union[str, None] = None,
                database: Union[str, None] = None):
        logging.info("Calling the instance method connect_one")
        if uri:
            logging.info(f"Connecting with the URI: {uri}")
            self.client = MongoClient(host=uri)

        if host:
            logging.info(f"Connecting with the HOST: {host} and PORT: {port}")
            self.client = MongoClient(host=host, port=port)
        
        if database:
                self.db = self.client.get_database(database)
        else:
            self.db = self.client.get_database()
            logging.info(self.db)              



## NEW WAY TO DEFINE COLLECTION AND MODEL
class Model(MongoAPI):
    connection: Union[MongoAPI, None]
    
    def __init__(self, **kwargs) -> None:
        if not hasattr(self, 'connection') or not self.connection:
            if self.db is None:
                super().__init__()
        else:
            self.db = self.connection.db
            self.client = self.connection.client
            
        for key, value in kwargs.items():
            setattr(self, key, value)
        # print(self.__class__.__dict__.items())
        if (not hasattr(self, 'collection_name')) or self.collection_name is None or self.collection_name == '':
            self.collection_name = self.construct_model_name() # Here I want to get the inherited class name as the collection name.
            
        self.collection = Collection(self.db, self.collection_name)
        logging.info(self.collection)
        # Create the collection in the mongo db with the field rules
        items = self.__class__.__dict__.items()
        for key, value in items:
            if isinstance(value, Field):
                ## Extract the rulw
                kwargs = {}
                if hasattr(value, 'unique') and getattr(value, 'unique') is True:
                    kwargs['unique'] = getattr(value, 'unique')
                if kwargs or (hasattr(value, 'index') and getattr(value, 'index') is True):
                    self.collection.create_index(keys=key, **kwargs)
                    
                    

    def find(self, *args, **kwargs)-> Cursor:
        """Finds the list of documents from the collection set in the model

        Returns:
            Cursor: The cursor object of the documents
        """
        return self.collection.find(*args, **kwargs)
    
    def find_one(self, filter: Union[Any, None] = None, *args, **kwargs) -> Optional[_DocumentType]:
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
        
        _data = documents
        
        if bypass_document_validation is False:
            _data = self.validate_on_docs(documents)
        
        return self.collection.insert_many(_data, ordered, bypass_document_validation, session, comment)
    
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
        _data = document
        if bypass_document_validation is False:
            _data = self.validate_on_docs(document)
        
        return self.collection.insert_one(_data, bypass_document_validation, session, comment)
    
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
            _data = self.validate_on_docs(update)
        
        return self.collection.update_one(filter, _data, upsert, bypass_document_validation, collation, array_filters, hint, session, let, comment)

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
        _data = update
        if bypass_document_validation is False:
            _data = self.validate_on_docs(update)
            
        return self.collection.update_many(filter, _data, upsert, array_filters, bypass_document_validation, collation, hint, session, let, comment)

    
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
    
    def aggregate(self,
        pipeline: _Pipeline,
        session: Optional[ClientSession] = None,
        let: Optional[Mapping[str, Any]] = None,
        comment: Optional[Any] = None,
        **kwargs: Any,
    ) -> CommandCursor[_DocumentType]:
        return self.collection.aggregate(pipeline, session, let, comment, **kwargs)
    
    def count_documents(
        self, 
        filter: Mapping[str, Any],
        session: Optional[ClientSession] = None,
        comment: Optional[Any] = None,
        **kwargs: Any,
        )-> int:
        return self.collection.count_documents(filter=filter, session=session, comment=comment, **kwargs)
    
    def validate_on_docs(self, data):
        _data = list()
        if isinstance(data, List):
            for index, doc in enumerate(data):
                _data.append(self.validate_data(doc))
            return _data
        else:
            return self.validate_data(data)
    
    def validate_data(self, data):
        for _key, value in data.items():
            setattr(self, _key, value)
            
        _data = {}
        for key, value in self.__class__.__dict__.items():
            if isinstance(value, Field):
                if hasattr(self, key):
                    value.validate(getattr(self, key), key)
                    _data[key] = getattr(self, key)
                else:
                    if hasattr(value, 'default'):
                        dvalue = getattr(value, 'default')
                        value.validate(value=dvalue, field_name=key)
                        _data[key] = dvalue
                    else:
                        value.validate(value=None, field_name=key)
        
        return _data
    
    # End of the validate data function
    
    def save(self):
        items = self.__class__.__dict__.items()
        data: Dict[str, Any] = {}
        for key, value in items:
            if isinstance(value, Field):
                print(f"Checking {key} {hasattr(self, key)}")
                if hasattr(self, key):
                    data[key] = getattr(self, key)
                else:
                    if hasattr(value, 'default'):
                        value.validate(getattr(value, 'default'), key)
                        data[key] = getattr(value, 'default')
                    else:
                        value.validate(None, key) # This will throw an error
        
        if not data:
            raise ValueError('No value provided.')
        
        return self.insert_one(document=data)
        
    
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
    def __init__(self, size: int = -1, required: bool = False, unique: bool = False, index: bool = False, default: Union[str, None] = None) -> None:
        super().__init__()
        self.size = size if size > 0 else None
        self.required = required
        self.unique = unique
        self.index = index
        self.default = default
        
    def validate(self, value, field_name):
        if not self.required and self.default:
            # print(f"{field_name} value:= {self.default}")
            setattr(self, field_name, self.default)
            value = self.default # for subsequest error test
        if self.required and not value:
            raise ValueError(f"Field {field_name} marked as required and no value provided.")
        if not isinstance(value, str):
            raise ValueError(f"Field {field_name} -> String is expected.")
        if self.size and len(value) > self.size:
            raise ValueError(f"{field_name} size exceeded, max size {self.size}. Provided {len(value)}")
        
    
        
## Number field start
class NumberField(Field):
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
    
    

class ListField(Field):
    def __init__(self, required: bool = False, item_type: Union[Any, None] = None, default: Union[list, None] = None) -> None:
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



class BooleanField(Field):
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



class ForeignField(Field):
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
            
        
    
        
        