from app import People, Author
from bson.json_util import loads, dumps

if __name__ == '__main__':
    people = People()
    documents = people.read()
    print(loads(dumps(documents)))
    print("Insert one doc")
    author = Author()
    insertData = author.insertOne({'name': "Bankim Chandra", 'books': 12})
    print(insertData.inserted_id)
    authorData = author.read()
    print(loads(dumps(authorData)))