from django.contrib.postgres.aggregates import ArrayAgg
from django.core.paginator import EmptyPage
from django.db import connection, reset_queries
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView

from movies.models import Filmwork


MOVIE_FIELDS = ('id', 'title', 'description', 'creation_date', 'rating', 'type')


class MoviesApiMixin:
    model = Filmwork
    http_method_names = ['get']

    def get_queryset(self):
        qs = (Filmwork.objects.all().prefetch_related('persons', 'genres').
              values(*MOVIE_FIELDS).
              annotate(
                  genres=ArrayAgg('genres__name', distinct=True),
                  actors=ArrayAgg('persons__full_name',
                                  filter=Q(personfilmwork__role='actor'), distinct=True),
                  directors=ArrayAgg('persons__full_name',
                                     filter=Q(personfilmwork__role='director'), distinct=True),
                  writers=ArrayAgg('persons__full_name',
                                   filter=Q(personfilmwork__role='writer'), distinct=True)).
              order_by('id')
              )
        return qs

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class MoviesListApi(MoviesApiMixin, BaseListView):
    paginate_by = 50  # 50

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = self.get_queryset()
        paginator, page, queryset, is_paginated = self.paginate_queryset(
            queryset,
            self.paginate_by
        )

        try:
            prev_page_number = page.previous_page_number()
        except EmptyPage:
            prev_page_number = None
        try:
            next_page_number = page.next_page_number()
        except EmptyPage:
            next_page_number = None
        query_as_list = list(queryset)

        return {
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'prev': prev_page_number,
            'next': next_page_number,
            'results': query_as_list,
            'sql_connections': len(connection.queries)
        }


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):
    def get_context_data(self, *, object_list=None, **kwargs):
        return kwargs['object']
