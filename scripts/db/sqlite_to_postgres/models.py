from abc import ABC
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, date
import uuid


class TableTransferModel(ABC):
    pass


class FilmType(Enum):
    TV_SHOW = 'tv_show'
    MOVIE = 'movie'


@dataclass(frozen=True, kw_only=True)
class UUIDMixin:
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass(frozen=True, kw_only=True)
class TimeStampedMixin:
    created: datetime = field(default_factory=datetime.now)
    modified: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class Filmwork(TableTransferModel, UUIDMixin, TimeStampedMixin):
    title: str
    type: FilmType
    description: str = ''
    creation_date: date = None
    rating: float = None


@dataclass(frozen=True)
class Genre(TableTransferModel, UUIDMixin, TimeStampedMixin):
    name: str
    description: str = ''


@dataclass(frozen=True)
class Person(TableTransferModel, UUIDMixin, TimeStampedMixin):
    full_name: str


@dataclass(frozen=True)
class GenreFilmwork(TableTransferModel, UUIDMixin):
    genre_id: uuid.UUID
    film_work_id: uuid.UUID
    created: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class PersonFilmwork(TableTransferModel, UUIDMixin):
    person_id: uuid.UUID
    film_work_id: uuid.UUID
    role: str = None
    created: datetime = field(default_factory=datetime.now)


TABLE_NAMES = ('film_work', 'person', 'genre', 'person_film_work', 'genre_film_work',)


def get_table_transfer_model(table_name):
    return {
        'film_work': Filmwork,
        'person': Person,
        'genre': Genre,
        'person_film_work': PersonFilmwork,
        'genre_film_work': GenreFilmwork
    }[table_name]
