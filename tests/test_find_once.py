from mongodesu.mongolib import Model, MongoAPI
from mongodesu.fields.types import StringField, NumberField, ForeignField, ObjectId

MongoAPI.connect(uri="mongodb://localhost:27017", database="test_mongodesu")

class User(Model):
    collection_name = 'users'
    name = StringField(required=True)
    age = NumberField(required=True)
    


if __name__ == '__main__':
    res = User.find_one({"_id": ObjectId("68bb1dda7c66b31bbb4d940e")})
    print(res)
    if res:
        print(res.name, res.age)
        res.age = 35
        res.name = "AkaUser2"
        new_res = res.save()
        print(new_res)
    user = User()
    user.name = "Another User"
    user.age = 20
    # This should create a new user
    new_user_res = user.save()
    print(new_user_res)