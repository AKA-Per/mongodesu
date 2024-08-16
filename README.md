# MongoAPI Documentation

This documentation provides an overview of the MongoAPI and Model classes, designed to simplify CRUD operations and schema enforcement when interacting with MongoDB. The classes provide a Pythonic interface for managing MongoDB connections, defining collections, and enforcing data validation.

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [MongoAPI Class](#mongoapi-class)
4. [Model Class](#model-class)
5. [Field Classes](#field-classes)
   - [StringField](#stringfield)
   - [NumberField](#numberfield)
   - [ListField](#listfield)
   - [DateField](#datefield)
   - [BooleanField](#booleanfield)
   - [ForeignField](#foreignfield)
6. [Examples](#examples)

## Introduction

The MongoAPI and Model classes provide an abstraction layer on top of PyMongo, enabling easier management of MongoDB collections and documents. These classes also enforce schema validation, ensuring that data inserted into the database adheres to predefined rules.

## Installation

To use the MongoAPI and related classes, you need to install the following dependencies:

```bash
pip install mongodesu
```

## MongoAPI Class

The `MongoAPI` class is a wrapper for CRUD operations and connection logic for MongoDB.

### Methods

- **`__init__()`**: Initializes the MongoAPI instance and establishes a connection to the MongoDB database.
- **`connect()`**: A class method for establishing a connection to the MongoDB database.
- **`connect_one()`**: An instance method for establishing a connection to the MongoDB database.


## Model Class

The `Model` class is an abstraction over a MongoDB collection. It provides methods for defining the schema and interacting with the collection.

### Attributes

- **`connection`**: A reference to a `MongoAPI` instance, used to establish the connection.
- **`collection_name`**: The name of the MongoDB collection. If not provided, it defaults to the pluralized class name.
- **`collection`**: A reference to the MongoDB collection.

### Methods

- **`__init__()`**: Initializes the Model instance and sets up the MongoDB collection.
- **`find()`**: Finds a list of documents from the collection.
- **`find_one()`**: Finds a single document based on the provided filter.
- **`insert_many()`**: Inserts multiple documents into the collection.
- **`insert_one()`**: Inserts a single document into the collection.
- **`update_one()`**: Updates a single document based on the provided filter.
- **`update_many()`**: Updates multiple documents based on the provided filter.
- **`delete_one()`**: Deletes a single document based on the provided filter.
- **`delete_many()`**: Deletes multiple documents based on the provided filter.
- **`aggregate()`**: Performs aggregation operations on the collection.
- **`save()`**: Saves the current instance to the MongoDB collection.
- **`construct_model_name()`**: Constructs the collection name based on the class name.

## Field Classes

### StringField

A field that stores string data.

**Parameters:**

- `size`: The maximum size of the string.
- `required`: Whether the field is required.
- `unique`: Whether the field should be unique.
- `index`: Whether the field should be indexed.
- `default`: The default value of the field.

### NumberField

A field that stores numeric data.

**Parameters:**

- `required`: Whether the field is required.
- `unique`: Whether the field should be unique.
- `index`: Whether the field should be indexed.
- `default`: The default value of the field.

### ListField

A field that stores a list of items.

**Parameters:**

- `required`: Whether the field is required.
- `item_type`: The type of items in the list.
- `default`: The default value of the field.

### DateField

A field that stores date or datetime data.

**Parameters:**

- `required`: Whether the field is required.
- `unique`: Whether the field should be unique.
- `index`: Whether the field should be indexed.
- `default`: The default value of the field.

### BooleanField

A field that stores boolean data.

**Parameters:**

- `required`: Whether the field is required.
- `unique`: Whether the field should be unique.
- `index`: Whether the field should be indexed.
- `default`: The default value of the field.

### ForeignField

A field that stores a reference to another model.

**Parameters:**

- `model`: The model to which this field refers.
- `parent_field`: The field in the parent model to which this field refers.
- `required`: Whether the field is required.
- `default`: The default value of the field.
- `existance_check`: Whether to check the existence of the referenced document.

## Examples

### Connecting to MongoDB (Method I)

This will connect the db and all the operation will use this connection.

```python
from mongodesu.mongolib import MongoAPI
mongo_api = MongoAPI(uri="mongodb://localhost:27017", database="mydatabase")
```

### Connecting to the database (Methond II)

This will connect to the default mongo instance. And whatever model you will create. All the operation will use this connection by default.

```python
MongoAPI.connect(uri="mongodb://localhost:27017/python-db-test")
```

### Connecting to the database (Method III)

This is the same as the above methods.

```python
mongo = MongoAPI()
mongo.connect_one(uri="mongodb://localhost:27017/python-db-test")
```


### Defining a Model

```python
from mongodesu.mongolib import StringField, BooleanField, NumberField
class User(Model):
    name = StringField(required=True)
    age = NumberField(required=True)
    email = StringField(required=True, unique=True)
    is_active = BooleanField(default=True)

# Example usage
user = User(name="John Doe", age=30, email="john.doe@example.com")
user.save()
```

### Inserting a document

```python
user = User()
user.insert_one({"name":"John Doe", "age"28, "email":"john@example.com"})
```

### Inserting a list of documents

```python
user = User()
documents = [
    {"name":"John Doe", "age"28, "email":"john@example.com"},
    {"name":"Jack Doe", "age"28, "email":"jack@example.com"}
]
user.insert_many(documents)
```

### Finding one Document

```python
user = User()
result = user.find_one({"name": "John Doe"})
print(result)
```

### Finding list of documents

```python
user = User()
result = user.find({})
print(result)
```

### Updating Documents

```python
user = User()
user.update_one({"name": "John Doe"}, {"$set": {"age": 31}})
```

### Deleting Documents

```python
user = User()
user.delete_one({"name": "John Doe"})
```

### Count Documents

```python
user = User()
print(user.count_documents({"name": "John Doe"}))
```

### Using ForeignField

```python
class Post(Model):
    title = StringField(required=True)
    content = StringField(required=True)
    author = ForeignField(model=User, required=True, existance_check=True)

post = Post(title="My First Post", content="Hello, world!", author="ObjectId_of_User")
post.save()
```

### Creating multiple connection

This will create two connection and each model will be associated with the one connection and every operation will be perform for that connection over the connected database.

```python
from mongodesu.mongolib import MongoAPI, StringField, BooleanField, NumberField 

mongo1 = MongoAPI(host="localhost", port=27017, database="flaskdb")
mongo2 = MongoAPI(uri="mongodb://localhost:27017/python-db-test")

class Todo(Model):
        connection = mongo1
        collection_name = 'todos'
        
        # Fields description
        task = StringField(required=True, index=True)
        is_done = BooleanField(required=False)
        
    
class UserTodo(Model):
    connection = mongo2
    collection_name = 'user_todos'
    
    # Field description
    task = StringField(required=True, index=True)
    is_done = BooleanField(required=True)
    count_task = NumberField(required=False)

todo = Todo()
todo.insert_one({
    "task": "Fetch the car",
    "is_done": False
})

userTodo = UserTodo()
userTodo.insert_one({
    "task": "Paint",
    "is_done": False,
    "count_task": 1
})
```

This documentation provides a comprehensive guide to using the MongoAPI, Model, and Field classes. The classes are designed to simplify interaction with MongoDB while enforcing data integrity through schema validation.
