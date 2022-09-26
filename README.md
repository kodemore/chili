# Chili 
[![PyPI version](https://badge.fury.io/py/chili.svg)](https://pypi.org/project/chili) [![codecov](https://codecov.io/gh/kodemore/chili/branch/main/graph/badge.svg?token=TCG7SRQFD5)](https://codecov.io/gh/kodemore/chili) [![CI](https://github.com/kodemore/chili/actions/workflows/main.yaml/badge.svg?branch=main)](https://github.com/kodemore/chili/actions/workflows/main.yaml) [![Release](https://github.com/kodemore/chili/actions/workflows/release.yml/badge.svg)](https://github.com/kodemore/chili/actions/workflows/release.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Chili is an extensible data class support library. Its primary focus is on simplifying tasks related to initialising and extracting data classes.

Chili ensures type integrity and provides a simple interface to keep your codebase clean from unwanted abstractions.

## Features
- no dependencies besides typing_extensions
- supports nested data structures
- understands lists, sets, collections, unions, etc
- ensures type integrity 
- support for default values
- almost complete coverage for `typing` package (including generics)
- supports forward references out of the box
- might be extended with custom types
- data mapping/transformation with `chili.Mapping`
- fields hiding from serialisation and deserialisation with python's `field` function
- mapping from json data and to json data

## Installation

With pip,
```shell
pip install chili
```
or through poetry
```shell
poetry add chili
```

# Usage

## Initialising a dataclass

```python
from dataclasses import dataclass
from typing import List
from chili import init_dataclass

@dataclass
class Tag:
    id: str
    name: str

@dataclass
class Pet:
    name: str
    tags: List[Tag]
    age: int

pet = init_dataclass({"name": "Bobik", "tags": [{"name": "dog", "id": "12"}]}, Pet)
assert isinstance(pet, Pet)
assert isinstance(pet.tags, List)
assert isinstance(pet.tags[0], Tag)
```

> This example shows how can you cast your dict to a given data class. During data class initialisation, the type integrity is ensured automatically

## Transforming dataclass back to a dict

```python
from chili import asdict
from dataclasses import dataclass

@dataclass
class Money:
    currency: str
    amount: float

some_pounds = Money("GBP", "100.00")

some_pounds_dict = asdict(some_pounds)

assert isinstance(some_pounds_dict, dict)
assert isinstance(some_pounds_dict["amount"], float)
```

> Chili works with wide commonly used python types, but not every type can be simply transformed back and forth, 
> so make sure you familiarise yourself with supported types.

## Working with json data

```python
from dataclasses import dataclass
from typing import List
from chili import from_json, as_json

@dataclass
class Tag:
    id: str
    name: str

@dataclass
class Pet:
    name: str
    tags: List[Tag]

pet_json = '{"name": "Bobik", "tags": [{"id": "12", "name": "dog"}]}'
    
pet = from_json(pet_json, Pet)
assert isinstance(pet, Pet)
assert isinstance(pet.tags, List)
assert isinstance(pet.tags[0], Tag)

assert pet_json == as_json(pet)
```

## Using default values

```python
from dataclasses import dataclass, field
from typing import List
from chili import init_dataclass


@dataclass
class Pet:
    name: str
    tags: List[str] = field(default_factory=lambda: ["pet"])


boo = init_dataclass({"name": "Boo"}, Pet)

assert isinstance(boo, Pet)
assert boo.tags == ['pet']
```

In the above example tags attribute was not available in the dict object, so default value set 
in dataclass is being used instead.


> Please note `dataclasses` module does not allow mutable values in `default` argument of the `field` function, 
> so this example is using `default_factory` instead. More details about dataclasses' `default` and `default_factory` 
> arguments are available in the [python's documentation](https://docs.python.org/3/library/dataclasses.html#dataclasses.field).

## Hiding fields from hydration/deserialisation

There might be scenarios where not all dataclass' fields should be hydrated. In this scenario use built-in python's `dataclasses` module `field` function, like in the example below:

```python
from chili import init_dataclass
from dataclasses import dataclass, field
from typing import List


@dataclass
class Pet:
    name: str
    tags: List[str]
    tags_length: int = field(init=False)

    def __post_init__(self):
        self.tags_length = len(self.tags)


boo = init_dataclass({"name": "Boo", "tags": ["hamster", "boo"]}, Pet)

assert isinstance(boo, Pet)
assert boo.tags_length == 2
```

In the above example length of the `tags` attribute is recalculated everytime we initialise the class 
and hydrating it might be superfluous.


## Hiding fields from extraction/serialisation

To hide attributes of dataclass from being extracted into dict simply use `field` function with `repr` attribute set to `False`

```python
from dataclasses import dataclass, field
from typing import List

from chili import asdict


@dataclass
class Pet:
    name: str
    tags: List[str] = field(repr=False)


boo = Pet(name="Boo", tags=["pet", "hamster", "powerful!"])

boo_dict = asdict(boo)

assert "tags" not in boo_dict
```

## Data mapping

Sometimes you might run into scenarios that data coming from different sources needs to be remapped 
before you can hydrate it to your dataclass. There might be several reasons for that:
- input data is using camelCase convention
- input data is using different naming
- input data is missing values

In all those cases you can pass `mapping` attribute to `init_dataclass/hydrate` or `asdict/extract` functions to perform
mapping before hydration or after extraction dataclass.

### Simple mapping
Please consider the following example of simple name mapping:

```python
from dataclasses import dataclass
from typing import List

import chili

input_data = {
    "petName": "Bobik",
    "age": "12",
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


mapping = chili.Mapper({
    "name": "petName",  # `petName` will be renamed to `name`, which corresponds to `Pet.name` field
    "age": True,  # we just pass true value to include field "as is"
    "tags": chili.KeyMapper("taggedWith", {  # `taggedWith` is a complex structure we want to map, so we have to use KeyMapper 
        "name": "tagName",  # `tagName` will be renamed to `name` which corresponds to `Pet.tags[{index}].name`
    }),
})

bobik = chili.hydrate(input_data, Pet, mapping=mapping)
print(bobik)  # Pet(name='Bobik', age=12, tags=[{'name': 'smart'}, {'name': 'dog'}, {'name': 'happy'}])
```

### Mappings with custom behaviour

We can also use lambdas and functions in mapping to achieve the same result as in the previous example.

```python
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


mapping = chili.Mapper({
    "name": "petName",
    "age": lambda value: value["petAge"],  # callables will always receive current's scope data as input 
    "tags": chili.KeyMapper("taggedWith", map_pet_tags)
})

bobik = chili.hydrate(input_data, Pet, mapping=mapping)
print(bobik)  # Pet(name='Bobik', age=12, tags=[{'name': 'smart'}, {'name': 'dog'}, {'name': 'happy'}])
```
## Mapping with key persistence

You can use the `chili.mapping.PersistentMapper` to keep all keys and their values. 
> Please not that this will keep all keys, including the nested ones even when using `chili.KeyMapper`. Using a `Callable` is an exception.

```python
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
    taggedWith: List[dict]
    petAge: str
    petName: str


mapping_nested_persistence = chili.PersistentMapper({
    "name": "petName",
    "age": lambda value: value["petAge"],  # callables will always receive current's scope data as input 
    "tags": chili.KeyMapper("taggedWith", {"name": "tagName"})
})

bobik = chili.hydrate(input_data, Pet, mapping=mapping)
print(bobik)  # Pet(name='Bobik', age=12, tags=[{'name': 'smart', 'tagName': 'smart'}, {'name': 'dog', 'tagName': 'dog'}, {'name': 'happy', 'tagName': 'happy'}], taggedWith=[{'tagName': 'smart'}, {'tagName': 'dog'}, {'tagName': 'happy'}], petAge='12', petName='Bobik')


mapping_no_nested_persistence = chili.PersistentMapper({
    "name": "petName",
    "age": lambda value: value["petAge"],  # callables will always receive current's scope data as input 
    "tags": chili.KeyMapper("taggedWith", map_pet_tags)  # using a callable won't persist old nested keys and values
})

bobik = chili.hydrate(input_data, Pet,   mapping=mapping_no_nested_persistence)
print(bobik)  # Pet(name='Bobik', age=12, tags=[{'name': 'smart'}, {'name': 'dog'}, {'name': 'happy'}], taggedWith=[{'tagName': 'smart'}, {'tagName': 'dog'}, {'tagName': 'happy'}], petAge='12', petName='Bobik')
```
## Declaring custom hydrators

If you work with types that are neither dataclasses nor directly supported by `Chili`, you can define your own
hydrator to customise how the type is initialised and how it should be de-initialised by declaring a subclass of
`chili.hydration.HydrationStrategy` and registering it, like below:

```python
from chili import hydrate, registry, extract, HydrationStrategy
import  typing

class MyType:
    def __init__(self, value):
        self.value = value

class MyHydrator(HydrationStrategy):
    def extract(self, value):  # value will be instance of MyType
        return value.value
        
    def hydrate(self, value):
        return MyType(value)

# register our custom type in the hydration registry    
registry.add(MyType, MyHydrator())

# usage
assert isinstance(hydrate("hello", MyType), MyType)
assert isinstance(hydrate("hello", typing.Optional[MyType]), MyType) # this will work as well with optional types

assert extract(MyType("hello")) == "hello"
```


## Working with `Generic` types

`Chili` support most of python's generic types like; `typing.List`, `typing.Tuple`, `typing.Dict`, etc. 
Support is also provided for generic types defined by user (to some extent).

```python
from dataclasses import dataclass
from typing import Generic, List, TypeVar
from chili import init_dataclass

T = TypeVar("T")

@dataclass
class Pet:
    name: str

@dataclass
class Animal:
    name: str

@dataclass
class CustomList(Generic[T]):
    list: List[T]


pet_list = init_dataclass(
    {"list": [
        {"name": "Boo"},
        {"name": "Bobek"},
    ]},
    CustomList[Pet]
)

assert isinstance(pet_list, CustomList)
for pet in pet_list.list:
    assert isinstance(pet, Pet)


animal_list = init_dataclass(
    {"list": [
        {"name": "Boo"},
        {"name": "Bobek"},
    ]},
    CustomList[Animal]
)

assert isinstance(pet_list, CustomList)
for animal in animal_list.list:
    assert isinstance(animal, Animal)
```

In the above example there are three definitions of dataclasses: `Pet`, `Animal` and `CustomList`. 
`Pet` and `Animal` are just ordinary dataclasses but `CustomList` is a generic class, parametrised with `T` parameter. 
This means we can have subtypes, like: `CustomList[Pet]`, `CustomList[Animal]` or even `CustomList[Dict]`.

`init_dataclass` function understands that passed type is a generic type, and can handle it as suspected. 

Hydration of dataclass inheriting from another generic dataclasses is also supported, 
only if that dataclass specifies the parameters:

```python
from dataclasses import dataclass
from typing import Generic, List, TypeVar
from chili import init_dataclass

T = TypeVar("T")

@dataclass
class Pet:
    name: str

@dataclass
class Animal:
    name: str

@dataclass
class CustomList(Generic[T]):
    list: List[T]

@dataclass
class ExtendedGenericList(CustomList, Generic[T]):
    ...

@dataclass
class ExtendedList(CustomList[Pet]):
    ...

# this will work
pet_list = init_dataclass(
    {"list": [
        {"name": "Boo"},
        {"name": "Bobek"},
    ]},
    ExtendedGenericList[Pet]
)

# this will fail
failed_pet_list = init_dataclass(
    {"list": [
        {"name": "Boo"},
        {"name": "Bobek"},
    ]},
    ExtendedList
)
```

In the above example `ExtendedList` will fail during initialisation, the reason for that is information 
required to parametrise this class and probably its subclasses or any other classes aggregated by this class is lost. 
For now this behaviour is not supported for auto-hydration mode. `ExtendedGenericList[Pet]` will work as expected.

## Supported data types

### `bool`

Passed value is automatically hydrated to boolean with python's built-in `bool` on hydration and extraction.

### `dict`

Passed value is automatically hydrated to dict with python's built-in `dict` on hydration and extraction.

### `float`

Passed value is automatically hydrated to float with python's built-in `float` on hydration and extraction.

### `frozenset`

Passed value is automatically hydrated to frozen set with python's built-in `frozenset` and extracted to `list`.

### `int`

Passed value is automatically hydrated to int with python's built-in `int` on hydration and extraction.

### `list`

Passed value is automatically hydrated to list with python's built-in `list` on hydration and extraction.

### `set`

Passed value is automatically hydrated to set with python's built-in `set` and extracted to `list`.

### `str`

Passed value is automatically hydrated to string with python's built-in `str` on hydration and extraction.

### `tuple`

Passed value is automatically hydrated to tuple with python's built-in `tuple` and extracted to `list`.

### `collections.namedtuple`

Passed value is automatically hydrated to named tuple and extracted to `list`.

### `collections.deque`

Passed value is automatically hydrated to an instance of `collections.deque` and extracted to `list`.

### `collections.OrderedDict`

Passed value is automatically hydrated to an instance of `collections.OrderedDict` and extracted to `dict`.

### `datetime.date`

Passed value must be valid ISO-8601 date string, then it is automatically hydrated to an instance of `datetime.date` 
class and extracted to ISO-8601 format compatible string.

### `datetime.datetime`

Passed value must be valid ISO-8601 date time string, then it is automatically hydrated to an instance of `datetime.datetime` 
class and extracted to ISO-8601 format compatible string.

### `datetime.time`

Passed value must be valid ISO-8601 time string, then it is automatically hydrated to an instance of `datetime.time` 
class and extracted to ISO-8601 format compatible string.

### `datetime.timedelta`

Passed value must be valid ISO-8601 duration string, then it is automatically hydrated to an instance of `datetime.timedelta`
class and extracted to ISO-8601 format compatible string.

### `decimal.Decimal`

Passed value must be a string containing valid decimal number representation, for more please read python's manual
about [`decimal.Decimal`](https://docs.python.org/3/library/decimal.html#decimal.Decimal), on extraction value is
extracted back to string.

### `enum.Enum`

Supports hydration of all instances of `enum.Enum` subclasses as long as value can be assigned
to one of the members defined in the specified `enum.Enum` subclass. During extraction the value is
extracted to value of the enum member.

### `enum.IntEnum`

Same as `enum.Enum`.

### `typing.Any`

Passed value is unchanged during hydration and extraction process.

### `typing.AnyStr`

Same as `str`

### `typing.Deque`

Same as `collection.dequeue` with one exception, if subtype is defined, eg `typing.Deque[int]` each item inside queue
is hydrated accordingly to subtype.

### `typing.Dict`

Same as `dict` with exception that keys and values are respectively hydrated and extracted to match
annotated type.

### `typing.FrozenSet`

Same as `frozenset` with exception that values of a frozen set are respectively hydrated and extracted to
match annotated type.

### `typing.List`

Same as `list` with exception that values of a list are respectively hydrated and extracted to match annotated type.

### `typing.NamedTuple`

Same as `namedtuple`.

### `typing.Optional`

Optional types can carry additional `None` value which chili's hydration process will respect, so for example 
if your type is `typing.Optional[int]` `None` value is not hydrated to `int`.

### `typing.Set`

Same as `set` with exception that values of a set are respectively hydrated and extracted to match annotated type.

### `typing.Tuple`

Same as `tuple` with exception that values of a set are respectively hydrated and extracted to match annotated types.
Ellipsis operator (`...`) is also supported.

### `typing.TypedDict`

Same as `dict` but values of a dict are respectively hydrated and extracted to match annotated types. 


### `typing.Generic`

Only parametrised generic classes are supported, dataclasses that extends other Generic classes without parametrisation will fail.


### `typing.Union`

Limited support for Unions.

## API

#### **`chili.hydrate`**(**`value`**: _`typing.Any`_, **`type_name`**: _`Type[T]`_, **`strict`**: _`bool`_ = `False`, **`mapping`**: _`chili.Mapper`_ = `None`) -> _`T`_

Hydrates given value into instance of passed type. If hydration fails, it returns passed value as a result, 
if strict mode is set to `True` it raises `InvalidValueError`.

#### **`chili.extract`**(**`value`**: _`typing.Any`_, **`strict`**: _`bool`_ = `False`, **`mapping`**: _`chili.Mapper`_ = `None`) -> _`typing.Any`_

Extracts given value into primitive or set of primitives. If extraction fails, it returns passed value as a result, if
strict mode is set to `True` it raises `InvalidValueError`.

#### **`chili.init_dataclass`**(**`value`**: _`dict`_, **`type_name`**: _`Type[T]`_, **`mapping`**: _`chili.Mapper`_ = `None`) -> _`T`_

`init_dataclass` function is instantiating dataclass of specified `type_name` and will hydrate the instance 
with values passed in `value` dictionary. Each of the passed dictionary's keys must correspond to dataclass'
attributes in order to be properly interpreted. This rule can be broken if valid mapping is passed to the 
function.

This function support complex and nested hydration, which means if your dataclass aggregates other dataclasses 
or defines complex typing, `init_dataclass` function will respect your type annotations and will cast values 
to match the defined types. 

If attributes in your dataclass do not specify the type value will be hydrated in to a newly created instance as is.
#### **`chili.asdict`**(**`value`**, **`mapping`**: _`chili.Mapper`_ = `None`) -> _`Dict[str, typing.Any]`_

`asdict` is the opposite of `init_dataclass` function, it takes an instance of dataclass as argument, and
extracts its members to a dictionary, so the returned data can be stored as json object or easily serialised 
to any other format. Additionally, `mapping` argument allows changing data representation on the fly.

> Please note `Chili` is not a data validation library, although `Chili` performs some validation and casting
> behind the scenes it does it only to ensure type consistency.

