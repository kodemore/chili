# Chili
Chili is an extensible dataclass support library.
It contains helper functions to simplify initialising and extracting complex dataclasses.
This might come handy when you want to transform your request's data to well-defined and easy to understand objects 
or when there is a need to hydrate database records.

Library also ensures type integrity and provides simple interface, which does not pollute your codebase
with unwanted abstractions.

## Features
- extensible and easy to use
- complex dataclass initialisation and extraction
- supports most python's types found in `typing` package (including generics)
- does not pollute your codebase

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

> This example shows how simply cast your dict to given dataclass and that type are ensured by the init_dataclass function.

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


boo = init_dataclass({"name": "Boo", "tags": ["hamster", "boo"], "tags_length": 0}, Pet)

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


### `typing.Generic

Only parametrised generic classes are supported, dataclasses that extends other Generic classes without parametrisation will fail.


### `typing.Union`

Limited support for Unions.


## API

**`chili.init_dataclass`**(**`value`**: _`dict`_, **`type_name`**: _`Type[T]`_) -> _`T`_

`init_dataclass` function is instantiating dataclass of specified `type_name` and will hydrate the instance 
with values passed in `value` dictionary. Each of the passed dictionary's keys must correspond to dataclass'
attributes in order to be properly interpreted. 

This function support complex and nested hydration, which means if your dataclass aggregates other dataclasses 
or defines complex typing, `init_dataclass` function will respect your type annotations and will cast values 
to match the defined types. 

If attributes in your dataclass do not specify the type value will be hydrated in to a newly created instance as is.

**`chili.asdict`**(**`value`**) -> _`Dict[str, typing.Any]`_

`asdict` is the opposite of `init_dataclass` function, it takes an instance of dataclass as argument, and
extracts its members to a dictionary, so the returned data can be stored as json object orn easily serialised 
to any other format.

> Please note `Chili` is not a data validation library, even thou `Chili` performs some validation and casting
> behind the scenes but only to ensure type and behaviour consistency.
