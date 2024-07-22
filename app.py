from mongolib import Model, StringField, NumberField
from bson.json_util import loads, dumps
from bson import ObjectId
## Example usage
class User(Model):
    collection_name = 'users'
    first_name = StringField(size=20, required=True)
    age = NumberField(required=True)
    email = StringField(required=True)
        
    def __str__(self) -> str:
        return f"{self.first_name} {self.age}"
        


class Book(Model):
    
    def __init__(self) -> None:
        super().__init__()
   


if __name__ == '__main__':
    user = User()
    user.insert_many([{
        "first_name": "Babai",
        "age": 29
    }])
    # user.save()
    
    # cursor = user.find_one({"_id": ObjectId("669a0eb349e32ff4f29e0aae")})
    # print(loads(dumps(cursor)))
    
    


