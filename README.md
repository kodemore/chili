# Chili 
[![PyPI version](https://badge.fury.io/py/chili.svg)](https://pypi.org/project/chili) [![codecov](https://codecov.io/gh/kodemore/chili/branch/main/graph/badge.svg?token=TCG7SRQFD5)](https://codecov.io/gh/kodemore/chili) [![CI](https://github.com/kodemore/chili/actions/workflows/main.yaml/badge.svg?branch=main)](https://github.com/kodemore/chili/actions/workflows/main.yaml) [![Release](https://github.com/kodemore/chili/actions/workflows/release.yml/badge.svg)](https://github.com/kodemore/chili/actions/workflows/release.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Chili is an extensible library which provides a simple and efficient way to encode and decode complex Python objects to and from their dictionary representation.

It offers complete coverage for the `typing` package; including generics, and supports custom types, allowing you to extend the library to handle your specific needs. 

With support for nested data structures, default values, forward references, and data mapping and transformation, Chili is designed to be both easy to use and powerful enough to handle complex data structures.

> Note: Chili is not a validation library, although it ensures the type integrity. 

# Installation

To install the library, simply use pip:

```shell
pip install chili
```

or poetry:

```shell
poetry add chili
```

# Usage

The library provides three main classes for encoding and decoding objects, `chili.Encoder` and `chili.Decoder`, and `chili.Serializer`, which combines both functionalities.
Functional interface is also provided through `chili.encode` and `chili.decode` functions.

Additionally, library by default supports json serialization and deserialization, so you can use `chili.JsonDecoder`, and `chili.JsonDecoder`, and `chili.JsonSerializer` or its functional replacement `chili.json_encode` and `chili.json_decode` to serialize and deserialize objects to and from json.

## Defining encodable/decodable properties
To define the properties of a class that should be encoded and decoded, you need to define them with type annotations. 
The `@encodable`, `@decodable`, or `@serializable` decorator should also be used to mark the class as encodable/decodable or serializable.

> Note: Dataclasses are supported automatically, so you don't need to use the decorator.

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
To encode an object, you need to create an instance of the `chili.Encoder` class, and then call the `encode()` method, passing the object to be encoded as an argument.

> Note: The `chili.Encoder` class is a generic class, and you need to pass the type of the object to be encoded as a type argument.

```python
from chili import Encoder

encoder = Encoder[Pet]()

my_pet = Pet("Max", 3, "Golden Retriever")
encoded = encoder.encode(my_pet)

assert encoded == {"name": "Max", "age": 3, "breed": "Golden Retriever"}
```

## Decoding
To decode an object, you need to create an instance of the `chili.Decoder` class, and then call the `decode()` method, passing the dictionary to be decoded as an argument.


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

class MyCustomEncoder(TypeEncoder):
    def encode(self, value: MyCustomType) -> str:
        return value.encode()

    
type_encoders = {MyCustomType: MyCustomEncoder()}
encoder = Encoder[Pet](encoders=type_encoders)
```

## Custom Type Decoders
You can also specify custom type decoders by defining a class that implements the `chili.TypeDecoder` protocol and passing it as a dictionary to the `decoders` argument of the Decoder constructor.

```python
from chili import Decoder, TypeDecoder

class MyCustomDecoder(TypeDecoder):
    def decode(self, value: str) -> MyCustomType:
        return MyCustomType.decode(value)

type_decoders = {MyCustomType: MyCustomDecoder()}
decoder = Decoder[Pet](decoders=type_decoders)
```

## Convenient Functions
The library also provides convenient functions for encoding and decoding objects. 

The `chili.encode` function takes an object and an optional type hint and returns a dictionary. 

The `chili.decode` function takes a dictionary, a type hint, and returns an object.

```python
from chili import encode, decode

my_pet = Pet("Max", 3, "Golden Retriever")

encoded = encode(my_pet)
decoded = decode(encoded, Pet)
```

> To specify custom type encoders and decoders, you can pass them as keyword arguments to the `chili.encode` and `chili.decode` functions.

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

## Supported types

The following section lists all the data types supported by the library and explains how they are decoded and encoded. The supported data types include built-in Python types like `bool`, `dict`, `float`, `int`, `list`, `set`, `str`, and `tuple`, as well as more complex types like `collections.namedtuple`, `collections.deque`, `collections.OrderedDict`, `datetime.date`, `datetime.datetime`, `datetime.time`, `datetime.timedelta`, `decimal.Decimal`, `enum.Enum`, `enum.IntEnum`, and various types defined in the typing module.

### Simple types

Simple type are handled by a ProxyEncoder and ProxyDecoder. These types are decoded and encoded by casting the value to the specified type.


> For more details please refer to [chili.encoder.ProxyEncoder](chili/encoder.py#L50) and [chili.decoder.ProxyDecoder](chili/decoder.py#L65).

#### `bool`

Passed value is automatically cast to a boolean with python's built-in `bool` type during decoding and encoding process.

#### `int`

Passed value is automatically cast to an int with python's built-in `int` type during decoding and encoding process.

#### `float`

Passed value is automatically cast to float with python's built-in `float` type during decoding and encoding process.


#### `str`

Passed value is automatically cast to string with python's built-in `str` during encoding and decoding process.


#### `set`

Passed value is automatically cast to either `set` during decoding process or `list` during encoding process.


#### `frozenset`

Passed value is automatically cast to either `frozenset` during decoding process or `list` during encoding process.

#### `list`

Passed value is automatically cast to list with python's built-in `list` during encoding and decoding process.

#### `tuple`

Passed value is automatically cast either to `tuple` during decoding process or to `list` during encoding process.


#### `dict`

Passed value is automatically cast to dict with python's built-in `dict` during encoding and decoding process.

### Complex types

Complex types are handled by corresponding Encoder and Decoder classes. 

#### `collections.namedtuple`

Passed value is automatically cast to either `collections.namedtuple` during decoding process or `list` during encoding process.

> Please refer to [chili.encoder.NamedTupleEncoder](chili/encoder.py#L226) and [chili.decoder.NamedTupleDecoder](chili/decoder.py#L307) for more details.

#### `collections.deque`

Passed value is automatically cast to either `collections.deque` during decoding process or `list` during encoding process.

> Please refer to [chili.encoder.DequeEncoder](chili/encoder.py#L187) and [chili.decoder.DequeDecoder](chili/decoder.py#L268) for more details.

#### `collections.OrderedDict`

Passed value is automatically cast to either `collections.OrderedDict` during decoding process or `list` where each item is a `list` of two elements corresponding to `key` and `value`, during encoding process.

#### `datetime.date`

Passed value must be valid ISO-8601 date string, then it is automatically hydrated to an instance of `datetime.date` 
class and extracted to ISO-8601 format compatible string.

#### `datetime.datetime`

Passed value must be valid ISO-8601 date time string, then it is automatically hydrated to an instance of `datetime.datetime` 
class and extracted to ISO-8601 format compatible string.

#### `datetime.time`

Passed value must be valid ISO-8601 time string, then it is automatically hydrated to an instance of `datetime.time` 
class and extracted to ISO-8601 format compatible string.

#### `datetime.timedelta`

Passed value must be valid ISO-8601 duration string, then it is automatically hydrated to an instance of `datetime.timedelta`
class and extracted to ISO-8601 format compatible string.

#### `decimal.Decimal`

Passed value must be a string containing valid decimal number representation, for more please read python's manual
about [`decimal.Decimal`](https://docs.python.org/3/library/decimal.html#decimal.Decimal), on extraction value is
extracted back to string.

#### `enum.Enum`

Supports hydration of all instances of `enum.Enum` subclasses as long as value can be assigned
to one of the members defined in the specified `enum.Enum` subclass. During extraction the value is
extracted to value of the enum member.

#### `enum.IntEnum`

Same as `enum.Enum`.

### Typing module support

#### `typing.Any`

Passed value is unchanged during hydration and extraction process.

#### `typing.AnyStr`

Same as `str`

#### `typing.Deque`

Same as `collection.dequeue` with one exception, if subtype is defined, eg `typing.Deque[int]` each item inside queue
is hydrated accordingly to subtype.

#### `typing.Dict`

Same as `dict` with exception that keys and values are respectively hydrated and extracted to match
annotated type.

#### `typing.FrozenSet`

Same as `frozenset` with exception that values of a frozen set are respectively hydrated and extracted to
match annotated type.

#### `typing.List`

Same as `list` with exception that values of a list are respectively hydrated and extracted to match annotated type.

#### `typing.NamedTuple`

Same as `namedtuple`.

#### `typing.Set`

Same as `set` with exception that values of a set are respectively hydrated and extracted to match annotated type.

#### `typing.Tuple`

Same as `tuple` with exception that values of a set are respectively hydrated and extracted to match annotated types.
Ellipsis operator (`...`) is also supported.

#### `typing.TypedDict`

Same as `dict` but values of a dict are respectively hydrated and extracted to match annotated types. 


#### `typing.Generic`

Only parametrised generic classes are supported, dataclasses that extends other Generic classes without parametrisation will fail.


#### `typing.Optional`

Optional types can carry additional `None` value which chili's hydration process will respect, so for example 
if your type is `typing.Optional[int]` `None` value is not hydrated to `int`.


#### `typing.Union`

Limited support for Unions.





