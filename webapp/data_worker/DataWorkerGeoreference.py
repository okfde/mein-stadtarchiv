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
import requests
from time import sleep
from datetime import datetime
from ..models import Category, Document
from ..extensions import logger


class DataWorkerGeoreference:
    def __init__(self):
        pass

    def prepare(self):
        pass

    def run(self, category_id):
        category = Category.get(category_id)
        if not category:
            return
        self.loop_categories(category)

    def loop_categories(self, category):
        for document in Document.objects(category=category).all():
            self.georeference_document(document)
        for category in Category.objects(parent=category).all():
            self.loop_categories(category)

    def georeference_document(self, document):
        if document.lat and document.lon:
            return
        logger.info('worker.georeference', 'Georeferencing document %s' % document.id)
        street = document.title # TODO: flexible way of selecting this. should support title and meta values
        street = street.replace('str.', 'straße').replace('Str.', 'Straße')

        # TODO: this is nothing we can ever do in an admin config. only way would be regexp which is nothing an archive employee could do. only way: proper filled fields
        street = street.split(',')
        street = street[0 if len(street) == 1 else 1]
        street = re.sub('[(].*?[)]', '', street)
        street = street.strip()
        postfix = 'Moers' # TODO: flexible way of setting prefix (perhaps by base category?)
        args = {
            'format': 'json',
            'q': '%s, %s, Deutschland' % (street, postfix)
        }
        results = requests.get('https://nominatim.openstreetmap.org/search', args)
        sleep(1)
        if results.status_code != 200:
            return
        if not results.text:
            return
        results = results.json()
        if not len(results):
            return
        if not results[0].get('place_id'):
            return
        args = {
            'format': 'json',
            'place_id': results[0].get('place_id')
        }
        result = requests.get('https://nominatim.openstreetmap.org/details', args)
        sleep(1)
        if result.status_code != 200:
            return
        if not result.text:
            return
        result = result.json()
        if type(result.get('addresstags')) is dict:
            document.address = result.get('addresstags', {}).get('street')
            if result.get('addresstags', {}).get('housenumber'):
                document.address += result.get('addresstags', {}).get('housenumber')
            document.postcode = result.get('addresstags', {}).get('postcode')
            document.locality = result.get('addresstags', {}).get('city')
        if document.address == street:
            document.georeferencePrecision = 'exact'
        else:
            document.georeferencePrecision = 'vague'
        document.georeferenceDone = datetime.utcnow()
        document.lat = float(results[0].get('lat'))
        document.lon = float(results[0].get('lon'))
        document.save()
