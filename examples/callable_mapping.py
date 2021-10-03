from dataclasses import dataclass
from typing import List, Tuple

import chili


def map_pet_tags(value: List) -> List:
    return [{"name": item["tagName"]} for item in value]


input_data = {
    "petName": "Bobik",
    "petAge": "12",
    "taggedWith": [
        {"tagName": "smart"},
        {"tagName": "dog"},
        {"tagName": "happy"},
    ]
}


@dataclass
class Pet:
    name: str
    age: int
    tags: List[dict]


mapping = {
    "name": "petName",
    "age": lambda value: value["petAge"],  # first returned value is the new field name, the second is its value ,
    "tags": chili.KeyMapper("taggedWith", map_pet_tags),
}

bobik = chili.hydrate(input_data, Pet, mapping=chili.Mapper(mapping))
print(bobik)  # Pet(name='Bobik', age=12, tags=[{'name': 'smart'}, {'name': 'dog'}, {'name': 'happy'}])
