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

from datetime import datetime

def filter_file_min(query_parts, file_min):
    if file_min:
        query_parts.append({
            'range': {
                'file_count': {
                    'gte': 1
                }
            }
        })
def filter_help_required(query_parts, help_required):
    if help_required:
        query_parts.append({
            'range': {
                'help_required': {
                    'gte': 1
                }
            }
        })

def filter_year(query_parts, year_start, year_end):
    if year_start or year_end:
        part = {}
        if year_start:
            part['gte'] = '%s-01-01' % year_start
        if year_end:
            part['lt'] = '%s-01-01' % (year_end + 1)

        query_parts.append({
            'range': {
                'date_sort': part
            }
        })

def filter_search_string(query_parts, search_string):
    if search_string:
        search_string = search_string.replace('/', '\\/')
        query_parts.append(
            {
                'bool': {
                    'should': [
                        {
                            'query_string': {
                                'fields': ['title.fulltext'],
                                'query': search_string,
                                'default_operator': 'and',
                                'boost': 50
                            }
                        },
                        {
                            'query_string': {
                                'fields': ['description.fulltext'],
                                'query': search_string,
                                'default_operator': 'and',
                                'boost': 20
                            }
                        },
                        {
                            'query_string': {
                                'fields': ['extra_field_text.fulltext'],
                                'query': search_string,
                                'default_operator': 'and',
                                'boost': 25
                            }
                        }
                    ]
                }
            }
        )


def filter_search_string_complete(query_parts, search_string):
    if search_string:
        query_parts.append(
            {
                'bool': {
                    'should': [
                        {
                            'match_phrase_prefix': {
                                'fields': ['title.fulltext'],
                                'query': search_string,
                                'default_operator': 'and',
                                'boost': 50
                            }
                        },
                        {
                            'match_phrase_prefix': {
                                'fields': ['description.fulltext'],
                                'query': search_string,
                                'default_operator': 'and',
                                'boost': 20
                            }
                        }
                    ]
                }
            }
        )


def filter_categories(query_parts, facets):
    if 'category' in facets:
        if len(facets['category']):
            query_parts.append({
                'nested': {
                    'path': 'category',
                    'query': {
                        'terms': {
                            'category.id': facets['category']
                        }
                    }
                }
            })