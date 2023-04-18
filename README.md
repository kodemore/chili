# Chili 
[![PyPI version](https://badge.fury.io/py/chili.svg)](https://pypi.org/project/chili) [![codecov](https://codecov.io/gh/kodemore/chili/branch/main/graph/badge.svg?token=TCG7SRQFD5)](https://codecov.io/gh/kodemore/chili) [![CI](https://github.com/kodemore/chili/actions/workflows/main.yaml/badge.svg?branch=main)](https://github.com/kodemore/chili/actions/workflows/main.yaml) [![Release](https://github.com/kodemore/chili/actions/workflows/release.yml/badge.svg)](https://github.com/kodemore/chili/actions/workflows/release.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Chili is an extensible library which provides a simple and efficient way to encode and decode complex Python objects to and from their dictionary representation.

It offers complete coverage for the `typing` package; including generics, and supports custom types, allowing you to extend the library to handle your specific needs. 

With support for nested data structures, default values, forward references, and data mapping and transformation, Chili is designed to be both easy to use and powerful enough to handle complex data structures.

# Installation

To install the library, simply use pip:

```shell
pip install chili
```

```shell
poetry add chili
```

# Usage

The library provides three main classes for encoding and decoding objects, `chili.Encoder` and `chili.Decoder`, and `chili.Serializer`, which combines both functionalities.

Convinient functions are also provided for encoding and decoding objects, `chili.encode` and `chili.decode`.

Additionally, library by default supports json serialization and deserialization, so you can use `chili.JsonDecoder`, and `chili.JsonDecoder`, and `chili.JsonSerializer` or its functional replacement `chili.json_encode` and `chili.json_decode` to serialize and deserialize objects to and from json.

## Defining encodable/decodable properties
To define the properties of a class that should be encoded and decoded, you need to define them with type annotations. 
The `@encodable`, `@decodable`, or `@serializable` decorator should also be used to mark the class as encodable/decodable or serializable.

```python
from chili import encodable

@encodable
class Pet:
    name: str
    age: int
    breed: str

    def __init__(self, name: str, age: int, breed: str):
        self.name = name
        self.age = age
        self.breed = breed
```


## Encoding
To encode an object, you need to create an instance of the `chili.Encoder` class, and then call the `encode` method, passing the object to be encoded as an argument.

> Note: The `chili.Encoder` class is a generic class, and you need to pass the type of the object to be encoded as a type argument.

```python
from chili import Encoder

encoder = Encoder[Pet]()

my_pet = Pet("Max", 3, "Golden Retriever")
encoded = encoder.encode(my_pet)

assert encoded == {"name": "Max", "age": 3, "breed": "Golden Retriever"}
```

## Decoding
To decode an object, you need to create an instance of the `chili.Decoder` class, and then call the `decode` method, passing the dictionary to be decoded as an argument.


> Note: The `chili.Decoder` class is a generic class, and you need to pass the type of the object to be decoded as a type argument.

```python
from chili import Decoder

decoder = Decoder[Pet]()

data = {"name": "Max", "age": 3, "breed": "Golden Retriever"}
decoded = decoder.decode(data)

assert isinstance(decoded, Pet)
```

## Missing Properties
If a property is not present in the dictionary when decoding, the `chili.Decoder` class will not fill in the property value, unless there is a default value defined in the type annotation. Similarly, if a property is not defined on the class, the `chili.Encoder` class will hide the property in the resulting dictionary.

## Using Default Values
To provide default values for class properties that are not present in the encoded dictionary, you can define the properties with an equal sign and the default value. For example:

```python
from typing import List
from chili import Decoder, decodable

@decodable
class Book:
    name: str
    author: str
    isbn: str = "1234567890"
    tags: List[str] = []

book_data = {"name": "The Hobbit", "author": "J.R.R. Tolkien"}
decoder = Decoder[Book]()

book = decoder.decode(book_data)

assert book.tags == []
assert book.isbn == "1234567890"
```

> Note: When using default values with mutable objects, such as lists or dictionaries, be aware that the default value is shared among all instances of the class that do not have that property defined in the encoded dictionary. However, if the default value is empty (e.g. `[]` for a list, `{}` for a dictionary), it is not shared among instances.

## Custom Type Encoders
You can also specify custom type encoders by defining a class that implements the `chili.TypeEncoder` protocol and passing it as a dictionary to the `encoders` argument of the Encoder constructor.

```python
from chili import Encoder, TypeEncoder

class MyCustomEncoder(TypeEncoder[MyCustomType, str]):
    def encode(self, value: MyCustomType) -> str:
        return value.encode()

    
type_encoders = {MyCustomType: MyCustomEncoder()}
encoder = Encoder[Pet](encoders=type_encoders)
```

## Custom Type Decoders
You can also specify custom type decoders by defining a class that implements the `chili.TypeDecoder` protocol and passing it as a dictionary to the `decoders` argument of the Decoder constructor.

```python
from chili import Decoder, TypeDecoder

class MyCustomDecoder(TypeDecoder[str, MyCustomType]):
    def decode(self, value: str) -> MyCustomType:
        return MyCustomType.decode(value)

type_decoders = {MyCustomType: MyCustomDecoder()}
decoder = Decoder[Pet](decoders=type_decoders)
```

## Convenient Functions
The library also provides convenient functions for encoding and decoding objects. The encode function takes an object and an optional type hint and returns a dictionary. The decode function takes a dictionary, a type hint, and optional custom decoders and returns an object.

```python
from chili import encode, decode

my_pet = Pet("Max", 3, "Golden Retriever")

encoded = encode(my_pet)
decoded = decode(encoded, Pet)
```

## Serialization
If your object is both encodable and decodable, you can use the `@serializable` decorator to mark it as such. You can then use the `chili.Serializer` class to encode and decode objects.

```python
from chili import Serializer, serializable

@serializable
class Pet:
    name: str
    age: int
    breed: str

    def __init__(self, name: str, age: int, breed: str):
        self.name = name
        self.age = age
        self.breed = breed

my_pet = Pet("Max", 3, "Golden Retriever")
serializer = Serializer[Pet]()

encoded = serializer.encode(my_pet)
decoded = serializer.decode(encoded)
```

> Note: that you should only use the `@serializable` decorator for objects that are both encodable and decodable.


## JSON Serialization
The library also provides classes for encoding and decoding objects to and from JSON formats. The `chili.JsonEncoder` and `chili.JsonDecoder` classes provide JSON serialization.

```python
from chili import JsonEncoder, JsonDecoder, JsonSerializer

# JSON Serialization
encoder = JsonEncoder[Pet]()
decoder = JsonDecoder[Pet]()
serializer = JsonSerializer[Pet]()

my_pet = Pet("Max", 3, "Golden Retriever")
encoded = encoder.encode(my_pet)
decoded = decoder.decode(encoded)
```

The `encoded` value will be a json string:

```json
{"name": "Max", "age": 3, "breed": "Golden Retriever"}
```

The `decoded` value will be an instance of a Pet object.

> Functional interface is also available through the `chili.json_encode`, `chili.json_decode` functions.

## Mapping

Mapping allows you to remap keys, apply functions to the values, and even change the structure of the input dictionary. This is particularly useful when you need to convert data from one format to another, such as when interacting with different APIs or data sources that use different naming conventions.

### Simple mapping
Here's an example of how to use the `chili.Mapper` class from the library with a Pet class:

```python
from chili import Mapper

# Create a Mapper instance with the specified scheme
mapper = Mapper({
    "pet_name": "name",
    "pet_age": "age",
    "pet_tags": {
        "tag_name": "tag",
        "tag_type": "type",
    },
})

data = {
    "pet_name": "Max",
    "pet_age": 3,
    "pet_tags": [
        {"tag_name": "cute", "tag_type": "description"},
        {"tag_name": "furry", "tag_type": "description"},
    ],
}

# Apply the mapping to your input data
mapped_data = mapper.map(data)

print(mapped_data)
```

The `mapped_data` output would be:

```python
{
    "name": "Max",
    "age": 3,
    "pet_tags": [
        {"tag": "cute", "type": "description"},
        {"tag": "furry", "type": "description"},
    ],
}
```

### Using KeyScheme

`KeyScheme` can be used to define mapping rules for nested structures more explicitly. 
It allows you to specify both the old key and the nested mapping scheme in a single, concise object. This can be particularly useful when you want to map a nested structure but need to maintain clarity in your mapping scheme.

Here's an example of how to use `chili.KeyScheme` with the `chili.Mapper` class:

```python
from chili import Mapper, KeyScheme

# Create a Mapper instance with the specified scheme
mapper = Mapper({
    "pet_name": "name",
    "pet_age": "age",
    "pet_tags": KeyScheme("tags", {
        "tag_name": "tag",
        "tag_type": "type",
    }),
})

pet_dict = {
    "pet_name": "Max",
    "pet_age": 3,
    "pet_tags": [
        {"tag_name": "cute", "tag_type": "description"},
        {"tag_name": "furry", "tag_type": "description"},
    ],
}

# Apply the mapping to your input data
mapped_data = mapper.map(pet_dict)

print(mapped_data)
```

The `mapped_data` output would be:

```python
{
    "name": "Max",
    "age": 3,
    "tags": [
        {"tag": "cute", "type": "description"},
        {"tag": "furry", "type": "description"},
    ],
}
```

### Using wildcards in mapping

The `chili.Mapper` supports using `...` (Ellipsis) as a wildcard for keys that you want to include in the mapping but do not want to explicitly define. This can be useful when you want to map all keys in the input data, or when you want to map specific keys and leave the remaining keys unchanged.

You can use a lambda function with the `...` wildcard to apply a transformation to the keys or values that match the wildcard.

Here's an example of how to use the `...` wildcard with the `chili.Mapper` class:

```python
from chili import Mapper

# Create a Mapper instance with the specified scheme containing a wildcard ...
mapper = Mapper({
    "pet_name": "name",
    "pet_age": "age",
    ...: lambda k, v: (f"extra_{k}", v.upper() if isinstance(v, str) else v),
})

pet_dict = {
    "pet_name": "Max",
    "pet_age": 3,
    "pet_color": "white",
    "pet_breed": "Golden Retriever",
    "pet_tags": [
        {"tag": "cute", "type": "description"},
        {"tag": "furry", "type": "description"},
    ],
}

# Apply the mapping to your input data
mapped_data = mapper.map(pet_dict)

print(mapped_data)
```

The `mapped_data` output would be:

```python
{
    "pet_name": "Fluffy",
    "pet_age": 3,
    "extra_color": "WHITE",
    "extra_breed": "POODLE",
    "extra_tags": [
        {
            "tag": "cute",
            "type": "description",
        },
        {
            "tag": "furry",
            "type": "description",
        },
    ],
}
```

## Error handling
The library raises errors if an invalid type is passed to the Encoder or Decoder, or if an invalid dictionary is passed to the Decoder.

```python
from chili import Encoder, EncoderError, Decoder, DecoderError

# Invalid Type
encoder = Encoder[MyInvalidType]()  # Raises EncoderError.invalid_type

decoder = Decoder[MyInvalidType]()  # Raises DecoderError.invalid_type

# Invalid Dictionary
decoder = Decoder[Pet]()
invalid_data = {"name": "Max", "age": "three", "breed": "Golden Retriever"}
decoded = decoder.decode(invalid_data)  # Raises DecoderError.invalid_input
```
