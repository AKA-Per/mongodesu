from mongodesu.mongolib import MongoAPI, Model, StringField, NumberField

if __name__ == '__main__':
    MongoAPI.connect(uri="mongodb://localhost:27017/python-db-test")
    class User(Model):
        title = StringField(required=False, default="Mr.")
        name = StringField(required=True, default="Aka")
        age = NumberField(required=False, default=0)
        
    
    user = User()
    # user.name = "Aka Das"
    # user.save()
    
    # user.insert_one({"name": "Babai"})
    user.insert_many([
        {"name": "Rakesh"},
        {"name": "Ani", "title": "MR.", "age": 29}
    ])