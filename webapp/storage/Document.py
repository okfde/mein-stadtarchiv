# encoding: utf-8

"""
Copyright (c) 2007, Ernesto Ruge
All rights reserved.
Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

from flask import current_app
from mongoengine import Document as MongoDocument, BooleanField, ReferenceField, DateTimeField, StringField, ListField, \
    DecimalField, IntField, GeoJsonBaseField, DictField
from .ArchivDocument import ArchivDocument


class Document(MongoDocument, ArchivDocument):
    uid = StringField()
    order_id = StringField()
    created = DateTimeField(datetime_format='datetime')
    modified = DateTimeField(datetime_format='datetime')

    title = StringField(fulltext=True, sortable=True)
    description = StringField(fulltext=True)
    note = StringField(fulltext=True)
    origination = StringField()
    help_required = IntField()

    date = DateTimeField(datetime_format='date')
    date_begin = DateTimeField(datetime_format='date')
    date_end = DateTimeField(datetime_format='date')
    date_text = StringField()

    category = ListField(ReferenceField('Category', deref_document=True))
    tags = ListField(StringField())
    files = ListField(ReferenceField('File', deref_document=True))

    extra_fields = DictField(delete_document=True)
    document_type = StringField()

    def __init__(self, *args, **kwargs):
        super(MongoDocument, self).__init__(*args, **kwargs)

    def __repr__(self):
        return '<Document %r>' % self.title
