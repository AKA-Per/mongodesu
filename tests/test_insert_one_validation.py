from mongodesu.mongolib import Model, MongoAPI
from mongodesu.fields.types import StringField, NumberField, ForeignField

MongoAPI.connect(uri="mongodb://localhost:27017", database="test_mongodesu")

class User(Model):
    collection_name = 'users'
    name = StringField(required=True)
    age = NumberField(required=True)
    


if __name__ == '__main__':
    res = User.insert_one({"name": "Test User", "age": 30})
    print(res)