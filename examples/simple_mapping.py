from dataclasses import dataclass
from typing import List

import chili

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
    "petName": "name",  # `petName` will be renamed to `name`, which corresponds to `Pet.name` field
    "petAge": "age",
    "taggedWith": {  # `taggedWith` is a nested structure so its new name is defined in `__name__` key
        "__name__": "tags",
        "tagName": "name",  # `tagName` will be renamed to `name` which corresponds to `Pet.tags[{index}].name`
    }
}

bobik = chili.hydrate(input_data, Pet, mapping=mapping)
print(bobik)
