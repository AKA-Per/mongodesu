from mongodesu import MongoAPI, Model
from mongodesu.fields import StringField, NumberField, DateField

if __name__ == '__main__':
    MongoAPI.connect(uri="mongodb://localhost:27017/python-db-test")
    class User(Model):
        title = StringField(required=False, default=None)
        name = StringField(required=True, default="Aka")
        age = NumberField(required=False, default=0)
        created_at = DateField(required=False, default=None)
        
    
    # user = User()
    # user.name = "Aka Das"
    # user.save()
    
    # user.insert_one({"name": "Babai"})
    # User.insert_many([
    #     {"name": "Rakshit", "title": "Tgrigger"},
    #     {"name": "Hari", "title": "MR.", "age": 29, "created_at": "2025-01-05"}
    # ])
    
    user = User(
        title="",
        name="Anik"
    )
    user.save()