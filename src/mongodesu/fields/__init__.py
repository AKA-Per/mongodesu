
class Field:
    
    def __init__(self) -> None:
        self.value = None

    def __set_name__(self, owner, name):
        self.private_name = '_' + name
        self.name = name

    def __get__(self, obj, objtype=None):
        return getattr(obj, self.private_name)

    def __set__(self, obj, value):
        self.validate(value, self.name)
        setattr(obj, self.private_name, value)

    def validate(self, value, field_name):
        raise NotImplementedError("Subclasses must implement the validate method.")
    
    def get_distinct_list(self, list1, list2):
        set1 = set(list1)
        set2 = set(list2)
        
        distinct_elements = set2 - set1
        return list(distinct_elements)
    
