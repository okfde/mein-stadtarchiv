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

import time
import json
from flask import (Flask, Blueprint, render_template, current_app, request, flash, url_for, redirect, session, abort,
                   jsonify, send_from_directory)
from ..common.response import json_response
from ..models import Category
from ..extensions import es, csrf
from .RechercheHelper import *

recherche = Blueprint('recherche', __name__, template_folder='templates')


@recherche.route('/recherche')
def recherche_main():
    categories = []
    for category_raw in Category.objects(parent__exists=False).all():
        categories.append({
            'id': str(category_raw.id),
            'title': category_raw.title,
            'children': category_get_children(category_raw.id)
        })
    return render_template('recherche.html', categories=categories)

def category_get_children(category_id):
    categories = []
    for category_raw in Category.objects(parent=category_id).all():
        category = {
            'id': str(category_raw.id),
            'title': category_raw.title
        }
        children = category_get_children(category_raw.id)
        if len(children):
            category['children'] = children
        categories.append(category)
    return categories



@recherche.route('/api/search', methods=['POST'])
@csrf.exempt
def recherche_api():
    start_time = time.time()
    skip = request.form.get('skip', 0, type=int)
    limit = request.form.get('limit', 10, type=int)
    order_by = request.form.get('o', 'random')
    search_string = request.form.get('q', '')
    facets = request.form.get('fq', '{}')
    file_min = request.form.get('fc', 0, type=int)
    help_required = request.form.get('hc', 0, type=int)
    year_start = request.form.get('ys', False, type=int)
    year_end = request.form.get('ye', False, type=int)
    random_seed = request.form.get('rs', False)

    if skip < 0:
        abort(403)
    if order_by not in ['random', '_score', 'title.sort:asc', 'title.sort:desc', 'date_sort:asc', 'date_sort:desc']:
        abort(403)
    if not random_seed and order_by == 'random':
        abort(500)

    facets = json.loads(facets)

    query_parts = []
    filter_categories(query_parts, facets)
    filter_file_min(query_parts, file_min)
    filter_help_required(query_parts, help_required)
    filter_search_string(query_parts, search_string)
    filter_year(query_parts, year_start, year_end)

    aggs_query =  {
        'categories': {
            'nested': {
                'path': 'category'
            },
            'aggs': {
                'id': {
                    'terms': {
                        'field': 'category.id',
                        'missing': 'keine Angabe',
                        'size': 2048
                    },
                    'aggs': {
                        'title': {
                            'terms': {
                                'field': 'category.title',
                                'missing': 'keine Angabe',
                                'size': 2048
                            }
                        }
                    }
                }
            }
        }
    }

    query = {
        'query': {
            'bool': {
                'must': query_parts
            }
        },
        'aggs': aggs_query
    }

    if order_by == 'random':
        query = {
            'query': {
                'function_score': {
                    'query': query['query'],
                    'random_score': {
                        'seed': random_seed
                    }
                }
            },
            'aggs': aggs_query
        }
        order_by = '_score'

    result_raw = es.search(
        index=current_app.config['ELASTICSEARCH_DOCUMENT_INDEX'] + '-latest',
        doc_type='document',
        body= query,
        sort=order_by,
        _source='id,order_id,created,modified,title,description,note,origination,help_required,category,tags,files,category_full,date,date_begin,date_end,date_sort',
        size=limit,
        from_=skip
    )

    aggs_raw = es.search(
        index=current_app.config['ELASTICSEARCH_DOCUMENT_INDEX'] + '-latest',
        doc_type='document',
        body={
            'query': {},
            'aggs': aggs_query
        },
        _source='',
        size=0,
    )

    result = []
    for item in result_raw['hits']['hits']:
        result.append(item['_source'])
    terms = {
        'categories': {}
    }
    for item in aggs_raw['aggregations']['categories']['id']['buckets']:
        terms['categories'][item['key']] = {
            'count': 0,
            'title': item['title']['buckets'][0]['key']
        }
    for item in result_raw['aggregations']['categories']['id']['buckets']:
        if item['key'] in terms['categories']:
            terms['categories'][item['key']]['count'] = item['doc_count']
        else:
            print('wtf, %s not found' % item['key'])

    result = {
        'data': result,
        'terms': terms,
        'duration': round((time.time() - start_time) * 1000),
        'pagination': {
            'totalElements': result_raw['hits']['total']
        },
        'status': 0
    }
    return json_response(result)



@recherche.route('/api/live-search', methods=['GET', 'POST'])
@csrf.exempt
def live_search():
    start_time = time.time()
    search_string = request.args.get('q', '')
    facets = request.args.get('fq', '{}')
    file_min = request.args.get('fc', 0, type=int)

    facets = json.loads(facets)

    query_parts = []
    filter_categories(query_parts, facets)
    filter_file_min(query_parts, file_min)
    #filter_search_string_complete(query_parts, search_string)

    result_raw = es.search(
        index=current_app.config['ELASTICSEARCH_DOCUMENT_INDEX'] + '-latest',
        doc_type='document',
        body={
            'query': {
                'bool': {
                    'must': query_parts
                }
            },
            'suggest': {
                'autocomplete': {
                    'text': search_string,
                    'completion': {
                        'field': 'autocomplete',
                        'size': 200
                    }
                }
            }
        },
        size=0
    )
    result = {}
    for search_result in result_raw['suggest']['autocomplete'][0]['options']:
        if search_result['text'] not in result.keys():
            result[search_result['text']] = search_result['_score']
        else:
            result[search_result['text']] += search_result['_score']
    result = {
        'data': sorted(result, key=result.get, reverse=True)[0:10],
        'duration': round((time.time() - start_time) * 1000),
        'status': 0
    }
    return json_response(result)