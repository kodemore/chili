import typing
from dataclasses import dataclass

import chili


@dataclass
class ArtistNew:
    name: str


@dataclass
class CollectionResponse:
    items: typing.List[typing.Any]


@dataclass
class ArtistResponse(ArtistNew):
    artist_id: str


@dataclass
class ArtistCollectionResponse(CollectionResponse):
    items: typing.List["ArtistResponse"]


def test_can_extract_forward_references() -> None:
    # given
    artist_collection = ArtistCollectionResponse(
        items=[
            ArtistResponse(name="Various Artists", artist_id="21"),
            ArtistResponse(name="Led Zeppelin", artist_id="22"),
            ArtistResponse(name="Frank Zappa & Captain Beefheart", artist_id="23"),
        ],
    )

    # when
    extracted_data = chili.extract(artist_collection)

    # then
    assert isinstance(extracted_data["items"][0], dict)
