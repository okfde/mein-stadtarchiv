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


from flask import Blueprint, current_app, render_template, request

from webapp.common.elastic_request import ElasticRequest
from ..recherche.RechercheHelper import get_category_data
from ..common.response import json_response
from .MapForm import SearchForm

map = Blueprint('map', __name__, template_folder='templates')


@map.route('/map')
def map_main():
    form = SearchForm()

    return render_template('map.html', form=form,  category_data=get_category_data(request.args.get('category')))


@map.route('/api/geojson', methods=['GET', 'POST'])
def map_api():
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
    if form.files_required.data:
        elastic_request.set_range_limit('file_count', 'gte', 1)
    if form.category.data and form.category.data != 'all':
        elastic_request.set_fq('category_with_parents', form.category.data)
    elastic_request.set_limit(10000)
    elastic_request.set_range_limit('lat', 'gt', 0)
    elastic_request.set_range_limit('lon', 'gt', 0)
    elastic_request.source = ['id', 'lat', 'lon', 'title', 'files.id', 'files.mimeType', 'files.binary_exists']
    elastic_request.query()
    items = elastic_request.get_results()
    features = []
    for item in items:
        properties = {
            'id': item['id'],
            'title': item.get('title')
        }
        if len(item.get('files', [])):
            properties['binaryExists'] = item['files'][0]['binary_exists']
            properties['fileId'] = item['files'][0]['id']
            properties['mimeType'] = item['files'][0]['mimeType']

        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [item.get('lon'), item.get('lat')]
            },
            "properties": properties
        })
    return json_response({
        'type': 'FeatureCollection',
        'features': features
    })
