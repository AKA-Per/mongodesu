from mongodesu.mongolib import Model, MongoAPI, StringField, NumberField, ForeignField, Field
from bson.json_util import loads, dumps
from bson import ObjectId

## Example usage

mongo = MongoAPI()
mongo.connect_one(host="mongodb://localhost:27017", database="flaskdb")

class Address(Model):
    connection = mongo
    collection_name = 'address'
    address_line1 = StringField(required=True)
    address_line2 = StringField(required=False)
    city = StringField(required=True)
    
    def __str__(self) -> str:
        return f"{self.address_line1} {self.address_line2} {self.city}"


class User(Model):
    connection = mongo
    collection_name = 'users'
    first_name = StringField(size=20, required=True)
    age = NumberField(required=True)
    email = StringField(required=True, unique=True)
    address = ForeignField(model=Address, required=True, existance_check=True)
        
    def __str__(self) -> str:
        return f"{self.first_name} {self.age}"
        

# class Book(Model):
    
#     def __init__(self) -> None:
#         super().__init__()
   
class TestCls(Field):
    def __init__(self) -> None:
        address = Address()

if __name__ == '__main__':
    # MongoAPI.connect(host="mongodb://localhost:27017", database="flaskdb")
    
    address = Address()
    print(address.find())
    # address.address_line1 = "Barasat"
    # address.address_line2 = "Barasat"
    # address.city = "Kolkata"
    
    # addressRes = address.save()
    # print(f"Address Id: {addressRes.inserted_id}")
    # user = User(first_name="Babai", age=29, email="babai@mailinator.com", address=addressRes.inserted_id)
    # user.save()
    
    # user = User()
    # userData = user.find()
    
    # for _user in userData:
    #     print(_user.get('address'))
    
    user = User()
    
    userData = user.aggregate([
        {
            "$lookup": {
                "from":"address",
                "localField": "address",
                "foreignField": "_id",
                "as": "userAddress"
                
            }
        }
    ])
    
    while userData._has_next():
        currUser = userData.next()
        print(f"Name:=> {currUser.get('first_name')}, Address:=> {currUser.get('userAddress')[0].get('address_line1')}")
    
    # aaa = TestCls()
    
    # cursor = user.find_one({"_id": ObjectId("669a0eb349e32ff4f29e0aae")})
    # print(loads(dumps(cursor)))
    
    


