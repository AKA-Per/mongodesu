from mongodesu.mongolib import Model, MongoAPI
from mongodesu.fields.types import StringField, NumberField, ForeignField, ObjectId, BooleanField, DateField, ListField
from datetime import datetime
MongoAPI.connect(uri="mongodb://localhost:27017", database="test_mongodesu")

class User(Model):
    collection_name = 'users'
    name = StringField(required=True, default="User1")
    age = NumberField(required=True)
    is_active = BooleanField(required=True, default=True)
    created_at = DateField(required=True, default=lambda: datetime.utcnow())
    tags = ListField(item_type=str, default=["new","user"])
 
 

if __name__ == '__main__':
    user = User()
    user.age = 28
    print("User details:")
    print(f"Name: {user.name}")
    print(f"Age: {user.age}")
    print(f"Is Active: {user.is_active}")
    print(f"Created At: {user.created_at}")
    print(f"Tags: {user.tags}")
    
    # This should create a new user
    new_user_res = user.save()
    print("New User saved:")
    print(new_user_res)   
