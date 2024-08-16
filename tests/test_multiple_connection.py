from bson.json_util import loads, dumps
from mongodesu.mongolib import MongoAPI, Model, StringField, NumberField, BooleanField
import logging

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
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
    print("AL DONE")
    
   