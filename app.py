from mongolib import Model, StringField, NumberField

## Example usage
class User(Model):
    collection_name = 'users'
    first_name = StringField(size=20, required=True)
    age = NumberField(required=True)
        
    def __str__(self) -> str:
        return f"{self.first_name} {self.age}"
        


class Book(Model):
    
    def __init__(self) -> None:
        super().__init__()
   


if __name__ == '__main__':
    user = User(first_name="Hello", age=25)
    user.save()
    
    


