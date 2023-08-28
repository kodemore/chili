from chili import serializable, Serializer


@serializable(use_init=True)
class Pet:
    def __init__(self, name: str, age: int, breed: str):
        self.name = name
        self.age = age
        self.breed = breed
        self.age += 2


serializer = Serializer[Pet]()
pet = Pet("Max", 3, "Golden Retriever")

encoded = serializer.encode(pet)
decoded = serializer.decode(encoded)

assert encoded["age"] == 5
assert decoded.age == 7
