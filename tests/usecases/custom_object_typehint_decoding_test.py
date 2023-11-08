from chili import Decoder, Encoder


def test_can_decode_complex_typehinted_object() -> None:
    # given
    class PetName:
        value: str

        def __init__(self, value: str) -> None:
            self.value = value

    class PetAddress:
        street_name: str
        city: str

        def __init__(self, street_name: str, city: str):
            self._street_name = street_name
            self._city = city

        @property
        def street_name(self):
            return self._street_name

        @property
        def city(self):
            return self._city

    class Pet:
        address: PetAddress
        name: PetName

        def __init__(self, name: PetName, address: PetAddress) -> None:
            self._address = address
            self._name = name

        @property
        def address(self) -> PetAddress:
            return self._address

        @property
        def name(self) -> PetName:
            return self._name

    data = {
        "name": {
            "value": "Bobik",
        },
        "address": {
            "city": "Bobikowo",
            "street_name": "Bobiczna 69",
        },
    }

    decoder = Decoder[Pet]()

    # when
    pet = decoder.decode(data)

    # then
    assert isinstance(pet, Pet)
    assert isinstance(pet.address, PetAddress)
    assert isinstance(pet.name, PetName)


def test_can_encode_complex_typehinted_object() -> None:
    # given
    class PetName:
        value: str

        def __init__(self, value: str) -> None:
            self.value = value

    class PetAddress:
        street_name: str
        city: str

        def __init__(self, street_name: str, city: str):
            self._street_name = street_name
            self._city = city

        @property
        def street_name(self):
            return self._street_name

        @property
        def city(self):
            return self._city

    class Pet:
        address: PetAddress
        name: PetName

        def __init__(self, name: PetName, address: PetAddress) -> None:
            self._address = address
            self._name = name

        @property
        def address(self) -> PetAddress:
            return self._address

        @property
        def name(self) -> PetName:
            return self._name

    pet = Pet(PetName("Bobik"), PetAddress("Bobiczna 69", "Bobikowo"))

    encoder = Encoder[Pet]()

    # when
    data = encoder.encode(pet)

    # then
    assert data == {"address": {"street_name": "Bobiczna 69", "city": "Bobikowo"}, "name": {"value": "Bobik"}}
