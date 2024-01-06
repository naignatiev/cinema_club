import uuid

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField(_('genre_name'), max_length=255, unique=True)
    description = models.TextField(_('genre_description'), blank=True)

    class Meta:
        db_table = "\"content\".\"genre\""
        verbose_name = _('Genre')
        verbose_name_plural = _('Genres')

    def __str__(self):
        return self.name


class GenreFilmwork(UUIDMixin):
    film_work = models.ForeignKey(
        'Filmwork',
        on_delete=models.CASCADE,
        verbose_name=_('Filmwork')
    )
    genre = models.ForeignKey('Genre', on_delete=models.CASCADE, verbose_name=_('Genre'))
    created = models.DateTimeField(_('created'), auto_now_add=True)

    class Meta:
        db_table = "content\".\"genre_film_work"
        unique_together = ('film_work', 'genre')


class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.CharField(_('person_full_name'), max_length=255)

    class Meta:
        db_table = "content\".\"person"
        verbose_name = _('Person')
        verbose_name_plural = _('Persons')

    def __str__(self):
        return self.full_name


class Filmwork(UUIDMixin, TimeStampedMixin):
    class FilmType(models.TextChoices):
        TV_SHOW = 'tv_show', _('TV Show')
        MOVIE = 'movie', _('Movie')

    title = models.CharField(_('film_work_title'), max_length=255)
    description = models.TextField(_('film_work_description'), blank=True)
    rating = models.FloatField(_('film_work_rating'), blank=True, null=True,
                               validators=[
                                    MinValueValidator(0),
                                    MaxValueValidator(100)
                               ])
    creation_date = models.DateField(_('film_work_creation_date'), null=True)
    type = models.CharField(_('film_work_type'), choices=FilmType.choices, max_length=255)

    genres = models.ManyToManyField(Genre, through='GenreFilmwork', verbose_name=_('Genres'))
    persons = models.ManyToManyField(Person, through='PersonFilmwork', verbose_name=_('Person'))

    class Meta:
        db_table = "content\".\"film_work"
        verbose_name = _('Filmwork')
        verbose_name_plural = _('Filmwork')

    def __str__(self):
        return self.title


class PersonFilmwork(UUIDMixin):
    film_work = models.ForeignKey(
        'Filmwork',
        on_delete=models.CASCADE,
        verbose_name=_('Filmwork')
    )
    person = models.ForeignKey('Person', on_delete=models.CASCADE, verbose_name=_('Person'))
    role = models.TextField(_('person_film_work_role'), null=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"person_film_work"
        unique_together = ('film_work', 'person', 'role')
