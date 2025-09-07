from pymongo import MongoClient
from pymongo.results import InsertOneResult, InsertManyResult, UpdateResult, DeleteResult
from pymongo.cursor import Cursor
from pymongo.command_cursor import CommandCursor
from typing import Dict, Any, Iterable, Mapping, Optional, TypedDict, List, Union, Type, TypeVar
import inflect
from pymongo.bulk import RawBSONDocument
from pymongo.client_session import ClientSession
from pymongo.typings import _Pipeline, _CollationIn, Sequence
from pymongo.collection import _IndexKeyHint, _DocumentType
from pymongo.collection import abc, Collection
import logging

from mongodesu.fields.base import Field 
from mongodesu.serializable import Serializable

class AttributeDict(TypedDict):
    type: str
    required: bool
    enum: Any
    unique: bool
    default: Any

M = TypeVar('M', bound='Model')

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
class Model(MongoAPI, Serializable):
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
                    
                    
    @classmethod
    def find(cls: Type[M], *args, **kwargs) -> List[M]:
        """Finds the list of documents from the collection set in the model

        Returns:
            # Cursor: The cursor object of the documents
            List[_DocumentType]: The list of model instances
        """
        cls.collection = getattr(cls, "collection", Collection(cls.db, cls.collection_name))
        cursor = cls.collection.find(*args, **kwargs)
        resulted_list: List[M] = []
        for doc in cursor:
            instance = cls(**doc)
            resulted_list.append(instance)
            
        return resulted_list
    
    @classmethod
    def find_one(cls: Type[M], filter: Union[Any, None] = None, *args, **kwargs) -> Optional[M]:
        """Finds one data from the mongodb based on the filter provided. If no filter provided then the first docs will be returned

        Args:
            filter (Union[Any, None], optional): The filter for to apply in the query of mongodb collection. Defaults to None.

        Returns:
            Cursor: The cursor object of the document returned
        """
        cls.collection = getattr(cls, "collection", Collection(cls.db, cls.collection_name))
        data = cls.collection.find_one(filter, *args, **kwargs)
        if data is None:
            return data
        return cls(**data) # Return the class instance
    
    @classmethod
    def insert_many(cls: Type[M], 
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
        _current_self = cls()
        if not isinstance(documents, abc.Iterable):
            raise ValueError('documents should be an iterable of raybson or documenttype')
        
        _data = documents
        
        if bypass_document_validation is False:
            _data = _current_self.validate_on_docs(documents)
        
        return _current_self.collection.insert_many(_data, ordered, bypass_document_validation, session, comment)
    
    @classmethod
    def insert_one(cls: Type[M], document: Union[Any, RawBSONDocument], bypass_document_validation: bool = False, 
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
        _current_self = cls()
        _data = document
        if bypass_document_validation is False:
            _data = _current_self.validate_on_docs(data=document)
        return _current_self.collection.insert_one(_data, bypass_document_validation, session, comment)
    
    @classmethod
    def update_one(
        cls: Type[M],
        filter: Mapping[str, Any],
        update: Union[Mapping[str, Any], _Pipeline],
        upsert: bool = False,
        bypass_document_validation: bool = True, # This will be true as in case of update we will not provide all the fields
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
        _current_self = cls()
        _data = update
        if bypass_document_validation is False:
            _data = _current_self.validate_on_docs(data=update)
        return _current_self.collection.update_one(filter, _data, upsert, bypass_document_validation, collation, array_filters, hint, session, let, comment)

    @classmethod
    def update_many(
        cls: Type[M],
        filter: Mapping[str, Any],
        update: Union[Mapping[str, Any], _Pipeline],
        upsert: bool = False,
        array_filters: Optional[Sequence[Mapping[str, Any]]] = None,
        bypass_document_validation: Optional[bool] = True,
        collation: Optional[_CollationIn] = None,
        hint: Optional[_IndexKeyHint] = None,
        session: Optional[ClientSession] = None,
        let: Optional[Mapping[str, Any]] = None,
        comment: Optional[Any] = None,
    ) -> UpdateResult:
        _current_self = cls()
        _data = update
        if bypass_document_validation is False:
            _data = _current_self.validate_on_docs(update)
        return _current_self.collection.update_many(filter, _data, upsert, array_filters, bypass_document_validation, collation, hint, session, let, comment)

    @classmethod
    def delete_one(
        cls: Type[M],
        filter: Mapping[str, Any],
        collation: Optional[_CollationIn] = None,
        hint: Optional[_IndexKeyHint] = None,
        session: Optional[ClientSession] = None,
        let: Optional[Mapping[str, Any]] = None,
        comment: Optional[Any] = None,
    ) -> DeleteResult:
        cls.collection = getattr(cls, "collection", Collection(cls.db, cls.collection_name))
        return cls.collection.delete_one(filter, collation, hint, session, let, comment)
    
    @classmethod
    def delete_many(
        cls: Type[M],
        filter: Mapping[str, Any],
        collation: Optional[_CollationIn] = None,
        hint: Optional[_IndexKeyHint] = None,
        session: Optional[ClientSession] = None,
        let: Optional[Mapping[str, Any]] = None,
        comment: Optional[Any] = None,
    ) -> DeleteResult:
        cls.collection = getattr(cls, "collection", Collection(cls.db, cls.collection_name))
        return cls.collection.delete_many(filter, collation, hint, session, let, comment)
    
    @classmethod
    def aggregate(cls: Type[M],
        pipeline: _Pipeline,
        session: Optional[ClientSession] = None,
        let: Optional[Mapping[str, Any]] = None,
        comment: Optional[Any] = None,
        **kwargs: Any,
    ) -> CommandCursor[_DocumentType]:
        cls.collection = getattr(cls, "collection", Collection(cls.db, cls.collection_name))
        return cls.collection.aggregate(pipeline, session, let, comment, **kwargs)
    
    @classmethod
    def count_documents(
        cls: Type[M], 
        filter: Mapping[str, Any],
        session: Optional[ClientSession] = None,
        comment: Optional[Any] = None,
        **kwargs: Any,
        )-> int:
        cls.collection = getattr(cls, "collection", Collection(cls.db, cls.collection_name))
        return cls.collection.count_documents(filter=filter, session=session, comment=comment, **kwargs)
    
    def validate_on_docs(self, data):
        _data = list()
        if isinstance(data, List):
            for index, doc in enumerate(data):
                _data.append(self.validate_data(data=doc))
            return _data
        else:
            return self.validate_data(data=data)
    
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
                # print(f"Checking {key} {hasattr(self, key)}")
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
        
        # New fix for calling save on the existing instance will update the record 
        if hasattr(self, '_id'):
            filter = {'_id': getattr(self, '_id')}
            # Calls to the update_on on the collection to keep the flow intact from class method
            updated = self.collection.update_one(filter, {"$set": data}, upsert=False, bypass_document_validation=False)
            return updated
        # Calling the insert_one on the collection itself not the classmethod to keep the reference from breaking
        inserted = self.collection.insert_one(document=data)
        setattr(self, '_id', inserted.inserted_id)
        return inserted # This will return the mongo inserted result instance. But after updating the current instance
        
    
    def construct_model_name(self):
        inflector = inflect.engine()
        class_name = self.__class__.__name__
        return inflector.plural(class_name.lower())
    
    # Feature Implementation toDict
    def to_dict(self):
        data = {}
        for key, value in self.__class__.__dict__.items():
            if isinstance(value, Field):
                if hasattr(self, key):
                    data[key] = getattr(self, key)
                else:
                    if hasattr(value, 'default'):
                        data[key] = getattr(value, 'default')
                    else:
                        data[key] = None
        if hasattr(self, '_id'):
            data['_id'] = getattr(self, '_id')
        return data
    
    def __str__(self):
        return super().__str__() + " " + str(self.to_dict())
    
    

        
        