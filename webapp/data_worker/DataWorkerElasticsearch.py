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

import re
import time
import string
from bs4 import BeautifulSoup
from datetime import datetime
from flask import current_app
from ..models import Document, Category, Option
from ..extensions import es, logger
from .DataWorkerElasticsearchIndex import create_index


class DataWorkerElasticsearch():
    def __init__(self):
        pass

    def prepare(self):
        self.statistics = {
            'created': 0,
            'updated': 0
        }
        self.category_cache_str = {}
        self.category_cache_id = {}
        self.index_name = current_app.config['ELASTICSEARCH_DOCUMENT_INDEX'] + '-latest'

        for category in Category.objects.all():
            category_list_title = []
            category_list_id = []
            category_tmp = category
            while category_tmp:
                category_list_title.insert(0, category_tmp.title)
                category_list_id.insert(0, str(category_tmp.id))
                category_tmp = category_tmp.parent
            self.category_cache_str[str(category.id)] = ' → '.join(category_list_title)
            self.category_cache_id[str(category.id)] = category_list_id

    def run(self, *args):
        start = datetime.utcnow()
        start_with = False
        last_run = Option.objects(key='elasticsearch_last_run').first()
        if last_run:
            pass
            #if last_run.value:
            #    start_with = datetime.fromtimestamp(int(last_run.value))
        else:
            last_run = Option()
            last_run.key = 'elasticsearch_last_run'
            last_run.save()

        last_run = Option.objects(key='elasticsearch_last_run').first()

        self.prepare()

        if not es.indices.exists_alias(name=current_app.config['ELASTICSEARCH_DOCUMENT_INDEX'] + '-latest'):
            create_index()
        
        if start_with:
            documents = Document.objects(modified__gte=start_with)
        else:
            documents = Document.objects()

        for document in documents.all():
            self.index_document(document)

        last_run.value = str(int(start.timestamp()))
        last_run.save()

        logger.info('worker.elasticsearch', 'ElasticSearch import successfull: %s created, %s updated' % (self.statistics['created'], self.statistics['updated']))

    def index_document(self, document):
        document_dict = document.to_dict('deref_document', format_datetime=True, delete='delete_document')

        document_dict['file_count'] = 0
        if document.files:
            for file in document.files:
                if file.binary_exists:
                    document_dict['file_count'] += 1

        replace_punctuation_re = re.compile('[%s\n\r]' % re.escape(string.punctuation))
        extra_fields = []
        for extra_field_value in document.extra_fields.values():
            extra_fields.append(extra_field_value)
        document_dict['extra_field_text'] = ' '.join(extra_fields)

        document_dict['category_full'] = []
        document_dict['category_with_parents'] = []
        for category in document.category:
            document_dict['category_full'].append(self.category_cache_str[str(category.id)])
            document_dict['category_with_parents'] += self.category_cache_id[str(category.id)]
        if document.date:
            document_dict['date_sort'] = document.date.strftime('%Y-%m-%d')
        elif document.date_begin:
            document_dict['date_sort'] = document.date_begin.strftime('%Y-%m-%d')
        document_dict['autocomplete'] = []
        for field in ['title', 'description', 'extra_field_text']:
            if field in document_dict:
                if document_dict[field]:
                    # Sämtliche Newlines und Zeichen entfernen
                    autocomplete_keywords = replace_punctuation_re.sub(' ', document_dict[field])
                    # Sämtliche HTML Tags entfernen
                    autocomplete_soup = BeautifulSoup(autocomplete_keywords, 'html.parser')
                    autocomplete_keywords = ' '.join(autocomplete_soup.findAll(text=True))
                    # Wörter mit Gewichtung hinzufügen
                    autocomplete_keywords = autocomplete_keywords.split(' ')
                    while '' in autocomplete_keywords:
                        autocomplete_keywords.remove('')
                    document_dict['autocomplete'].append({
                        'input': autocomplete_keywords,
                        'weight': 20 if field == 'title' else 10
                    })
        new_doc = es.index(
            index=self.index_name,
            id=str(document.id),
            doc_type='document',
            body=document_dict
        )
        if new_doc['result'] in ['created', 'updated']:
            self.statistics[new_doc['result']] += 1
        else:
            logger.warn('worker.elasticsearch', 'Unknown result at %s' % document.id)


