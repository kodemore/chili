from dataclasses import dataclass
from typing import List, Tuple

import chili


def map_pet_tags(value: List, _) -> Tuple[str, List]:
    return "tags", [{"name": item["tagName"]} for item in value]


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
    "petName": "name",
    "petAge": lambda value, _: ("age", value),  # first returned value is the new field name, the second is its value ,
    "taggedWith": map_pet_tags,
}

bobik = chili.hydrate(input_data, Pet, mapping=mapping)
print(bobik)  # Pet(name='Bobik', age=12, tags=[{'name': 'smart'}, {'name': 'dog'}, {'name': 'happy'}])
