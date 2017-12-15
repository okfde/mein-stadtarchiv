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
import os
import sys
import csv
import datetime
from flask import current_app
from ..models import Totenzettel
from ..extensions import db


class DataImport():
    supported_types = [
        'totenzettel'
    ]

    def import_data(self, data_type):
        if data_type not in self.supported_types:
            sys.exit('unsupported data type')

        mapping = {
            'Ob_f2': 'serial_number',
            'Ob_f9': 'condition',
            'Ob_f7': 'size',
            'Ob_f17': 'owner',
            'Ob_f20': 'name',
            'Ob_f21': 'biography',
            'Ob_f24': 'remark',
            'Ob_f26': 'publication',
            'Ob_f30': 'birth',
            'Ob_f31': 'death'
        }
        obj = Totenzettel
        just_numbers_re = re.compile(r'[^\d]+')
        with open(os.path.join(current_app.config['DATA_DIR'], data_type + '.csv'), encoding='utf-8-sig') as data_file:
            items_raw = csv.DictReader(data_file, delimiter=';', quotechar='"')
            for item_raw in items_raw:
                item = obj.query.filter_by(external_id=item_raw['Ob_ID'])
                if item.count():
                    item = item.first()
                else:
                    item = obj()
                    item.external_id = item_raw['Ob_ID']
                    item.created = datetime.datetime.now()

                item.modified = datetime.datetime.now()

                for key, value in mapping.items():
                    if item_raw[key]:
                        if getattr(obj, value).type == 'INTEGER':
                            setattr(item, value, int(item_raw[key]))
                        elif getattr(obj, value).type == 'DATE':
                            setattr(item, value, self.parse_date(item_raw[key]))
                        else:
                            setattr(item, value, item_raw[key])

                # special: count
                totenzettel_count = just_numbers_re.sub('', item_raw['Ob_f6'])
                if totenzettel_count:
                    item.count = int(totenzettel_count)

                # special: size
                """
                if item_raw['Ob_f7']:
                  try:
                    totenzettel_size = item_raw['Ob_f7'].replace('cm', '').replace(',', '.').split('x')
                    width = int(float(totenzettel_size[0].strip()) * 10)
                    height = int(float(totenzettel_size[1].strip()) * 10)
                    item.width = width
                    item.height = height
                  except ValueError:
                    pass
                """
                db.session.add(item)
                db.session.commit()

    def parse_date(self, date_string):
        if len(date_string) == 8:
            return datetime.date(int(date_string[0:4]), int(date_string[5, 6]), int(date_string[7, 8]))
        return None
