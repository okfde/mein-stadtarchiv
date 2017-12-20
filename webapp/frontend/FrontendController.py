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

import random
from flask import (Flask, Blueprint, render_template, current_app, request, flash, url_for, redirect, session, abort,
                   jsonify, send_from_directory)
from ..models import Document
from ..extensions import es
from ..common.response import json_response

frontend = Blueprint('frontend', __name__, template_folder='templates')


@frontend.route('/')
def root():
    # todo: random query

    result_raw = es.search(
        index=current_app.config['ELASTICSEARCH_DOCUMENT_INDEX'] + '-latest',
        doc_type='document',
        body={
            'query': {
                'function_score': {
                    'random_score': {},
                    'query': {
                        'bool': {
                            'must': [
                                {
                                    'range': {
                                        'help_required': {
                                            'gte': 1
                                        }
                                    }
                                }
                            ]
                        }
                    }
                }
            }
        },
        sort = '_score',
        _source = 'id,files,slider_height',
        size = 5,
        from_ = 1
    )
    """
    max_height = 0
    for item in result_raw['hits']['hits']:
        if 'slider_height' in item['_source']:
            if item['_source']['slider_height'] > max_height:
                max_height = item['_source']['slider_height']
    """
    return render_template('index.html', documents=result_raw['hits']['hits'])


@frontend.route('/impressum')
def impressum():
    return render_template('impressum.html')


@frontend.route('/code-of-conduct')
def code_of_conduct():
    return render_template('code-of-conduct.html')


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
