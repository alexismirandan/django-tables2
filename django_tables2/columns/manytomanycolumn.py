# coding: utf-8
from __future__ import absolute_import, unicode_literals

from django.db import models
from django.utils.encoding import force_text
from django.utils.html import conditional_escape, mark_safe

from django_tables2.utils import ucfirst

from .base import Column, library


@library.register
class ManyToManyColumn(Column):
    '''
    Display the list of objects from a `ManyRelatedManager`

    Ordering is disabled for this column.

    Arguments:
        transform: callable to transform each item to text, it gets an item as argument
            and must return a string-like representation of the item.
            By default, it calls `~django.utils.force_text` on each item.
        filter: callable to filter, limit or order the QuerySet, it gets the
            `ManyRelatedManager` as first argument and must return.
            By default, it returns `all()``
        separator: separator string to join the items with. default: ', '

    For example, when displaying a list of friends with their full name::

        # models.py
        class Person(models.Model):
            first_name = models.CharField(max_length=200)
            last_name = models.CharField(max_length=200)
            friends = models.ManyToManyField(Person)

            @property
            def name(self):
                return '{} {}'.format(self.first_name, self.last_name)

        # tables.py
        class PersonTable(tables.Table):
            name = tables.Column(order_by=('last_name', 'first_name'))
            friends = tables.ManyToManyColumn(transform=lambda user: u.name)

    '''
    def __init__(self, transform=None, filter=None, separator=', ', *args, **kwargs):
        if transform is not None:
            self.transform = transform
        if filter is not None:
            self.filter = filter
        self.separator = separator

        kwargs.setdefault('orderable', False)

        super(ManyToManyColumn, self).__init__(*args, **kwargs)

    def transform(self, obj):
        '''
        Transform is applied to each item of the list of objects from the ManyToMany relation.
        '''
        return force_text(obj)

    def filter(self, qs):
        '''
        Filter is called on the ManyRelatedManager to allow ordering, filtering or limiting
        on the set of related objects.
        '''
        return qs.all()

    def render(self, value):
        # if value is None or not value.exists():
        if not value.exists():
            return '-'

        return mark_safe(
            conditional_escape(self.separator).join(
                map(conditional_escape, map(self.transform, self.filter(value)))
            )
        )

    @classmethod
    def from_field(cls, field):
        if isinstance(field, models.ManyToManyField):
            return cls(verbose_name=ucfirst(field.verbose_name))
