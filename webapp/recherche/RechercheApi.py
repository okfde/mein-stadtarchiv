# encoding: utf-8

"""
Copyright (c) 2017, Ernesto Ruge
All rights reserved.
Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""


from flask import current_app
from ..common.response import json_response
from ..common.elastic_request import ElasticRequest
from .RechercheForm import SearchForm, CategorySearchForm
from ..models import Category

from .RechercheController import recherche


@recherche.route('/api/documents', methods=['GET', 'POST'])
def api_search():
    elastic_request = ElasticRequest(
        current_app.config['ELASTICSEARCH_DOCUMENT_INDEX'] + '-latest',
        'document'
    )
    form = SearchForm()
    if form.fulltext.data:
        elastic_request.query_parts_must.append({
            'bool': {
                'should': [
                    {
                        'query_string': {
                            'fields': ['title.fulltext'],
                            'query': form.fulltext.data,
                            'default_operator': 'and',
                            'boost': 50
                        }
                    },
                    {
                        'query_string': {
                            'fields': ['description.fulltext'],
                            'query': form.fulltext.data,
                            'default_operator': 'and',
                            'boost': 20
                        }
                    },
                    {
                        'query_string': {
                            'fields': ['extra_field_text.fulltext'],
                            'query': form.fulltext.data,
                            'default_operator': 'and',
                            'boost': 25
                        }
                    }
                ]
            }
        })
    if form.year_start.data:
        elastic_request.set_range_limit('date_sort', 'gte', '%s-01-01' % form.year_start.data)
    if form.year_end.data:
        elastic_request.set_range_limit('date_sort', 'lte', '%s-01-01' % form.year_end.data)
    if form.help_required.data:
        elastic_request.set_range_limit('help_required', 'gte', 1)
    if form.files_required.data:
        elastic_request.set_range_limit('file_count', 'gte', 1)
    if form.category.data and form.category.data != 'all':
        elastic_request.set_fq('category_with_parents', form.category.data)

    elastic_request.source = [
        'id',
        'title',
        'description',
        'category_full',
        'origination',
        'note',
        'date_begin',
        'date_end',
        'date_text',
        'help_required',
        'file_count'
    ]

    elastic_request.set_random_seed(form.random_seed.data)
    elastic_request.set_skip(current_app.config['ITEMS_PER_PAGE'] * (form.page.data - 1))
    elastic_request.set_sort_field(form.sort_field.data)
    elastic_request.set_sort_order(form.sort_order.data)

    elastic_request.query()
    return json_response({
        'status': 0,
        'documents': elastic_request.get_results(),
        'count': elastic_request.get_result_count()
    })


@recherche.route('/api/search/category', methods=['POST'])
def api_search_category():
    form = CategorySearchForm()
    if form.validate_on_submit():
        if form.category.data == 'all':
            children = []
            for archive in Category.objects(parent__exists=False).order_by('+title').all():
                children.append(archive.to_dict())
            return json_response({
                'status': 0,
                'parent': None,
                'children': children
            })

        category = Category.get(form.category.data)
        result = {
            'status': 0,
            'children': category.get_dict_with_children()['children']
        }
        if category.parent:
            result['parent'] = category.parent.to_dict()
        else:
            result['parent'] = {
                'id': 'all',
                'title': 'Alle Archive'
            }
        return json_response(result)
    return json_response({
        'status': -1
    })
