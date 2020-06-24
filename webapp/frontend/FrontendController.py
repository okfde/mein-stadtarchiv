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

from elasticsearch.exceptions import NotFoundError
from flask import Blueprint, render_template, current_app, redirect, request, g
from ..common.elastic_request import ElasticRequest
from ..common.helpers import get_random_password
from ..models import Subsite

frontend = Blueprint('frontend', __name__, template_folder='templates')


@frontend.route('/')
def home():
    elastic_request = ElasticRequest(
        current_app.config['ELASTICSEARCH_DOCUMENT_INDEX'] + '-latest',
        'document'
    )
    elastic_request.set_limit(5)
    elastic_request.set_sort_field('random')
    elastic_request.set_random_seed(get_random_password())
    elastic_request.set_range_limit('helpRequired', 'gte', 1)
    elastic_request.set_range_limit('fileCount', 'gte', 1)
    elastic_request.source = ['id', 'title', 'files.id']
    if g.subsite:
        elastic_request.set_fq('categoryWithParents', [str(category) for category in g.subsite.categories])
        subsites = [{
            'lat': g.subsite.lat,
            'lon': g.subsite.lon,
            'title': g.subsite.title
        }]
    else:
        subsites = []
        for subsite in Subsite.objects():
            subsites.append({
                'id': str(id),
                'host': subsite.host,
                'lat': subsite.lat,
                'lon': subsite.lon,
                'title': subsite.title
            })
    try:
        elastic_request.query()
    except NotFoundError:
        return redirect('/admin/install')
    return render_template('index.html', documents=elastic_request.get_results(), subsites=subsites)


@frontend.route('/impressum')
def impressum():
    return render_template('impressum.html')


@frontend.route('/nutzungsbedingungen')
def code_of_conduct():
    return render_template('nutzungsbedingungen.html')


@frontend.route('/datenschutz')
def datenschutz():
    return render_template('datenschutz.html')


@frontend.route('/info/ueber-uns')
def info_ueber_uns():
    return render_template('ueber-uns.html')


@frontend.route('/info/archive')
def info_archive():
    return render_template('archive.html')


@frontend.route('/info/daten')
def info_daten():
    return render_template('daten.html')


@frontend.route('/robots.txt')
def robots_txt():
    return render_template('robots.txt')
