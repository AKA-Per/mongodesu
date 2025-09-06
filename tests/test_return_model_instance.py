from mongodesu.mongolib import Model, MongoAPI
from mongodesu.fields.types import StringField, NumberField, ForeignField

MongoAPI.connect(uri="mongodb://localhost:27017", database="test_mongodesu")

class User(Model):
    collection_name = 'users'
    name = StringField(required=True)
    age = NumberField(required=True)
    

if __name__ == '__main__':
    user = User()
    user.name = "Test User"
    user.age = 30
    new_user = user.save()
    print(f"New User ID: {user._id}")
    # user2 = User()
    updatedone = User.update_one({"_id": user._id}, {"$set": {"age": 31}})
    print(updatedone)
    
    data = User.find()
    print(data)
    
    