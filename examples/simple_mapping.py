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


scheme_map = {
    "name": "petName",  # `petName` will be renamed to `name`, which corresponds to `Pet.name` field
    "age": "petAge",
    "tags": chili.KeyMapper("taggedWith", {  # `taggedWith` is a nested structure so we have to use KeyMapper
        "name": "tagName",  # `tagName` will be renamed to `name` which corresponds to `Pet.tags[{index}].name`
    })
}

bobik = chili.hydrate(input_data, Pet, mapping=chili.Mapper(scheme_map))
print(bobik)
