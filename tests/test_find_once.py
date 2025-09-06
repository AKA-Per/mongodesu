from mongodesu.mongolib import Model, MongoAPI
from mongodesu.fields.types import StringField, NumberField, ForeignField, ObjectId

MongoAPI.connect(uri="mongodb://localhost:27017", database="test_mongodesu")

class User(Model):
    collection_name = 'users'
    name = StringField(required=True, default="User1")
    age = NumberField(required=True)
    


if __name__ == '__main__':
    # pass
    res = User.find_one({"_id": ObjectId("68bb1dda7c66b31bbb4d940e")})
    print("From test-> find one printed")
    print(res)
    repr(res)
    # if res:
    #     print(res.name, res.age)
    #     res.age = 35
    #     res.name = "AkaUser2"
    #     new_res = res.save()
    #     print("From test-> update res printed")
    #     print(new_res)
    user = User()
    # user.name = "Another User"
    user.age = 20
    print("From test-> script end", user.name)
    # user2 = User(name="Another User2", age=25)
    # print("Test script:=> ", user2.name, user2.age)
    # This should create a new user
    # new_user_res = user.save()
    # print(new_user_res)