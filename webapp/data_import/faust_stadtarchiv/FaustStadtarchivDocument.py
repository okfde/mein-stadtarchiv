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
from lxml import etree
from webapp.models import Document, File
from ...extensions import logger


def get_document(uid, parent):
    return Document.objects(category=[parent], uid=uid).first()


def save_document(categories, data):
    primary = get_field(data, './/Bestand')
    secondary = get_field(data, './/Klassifikation')
    if not primary or not secondary:
        return
    category = categories[primary]['children'][secondary]

    uid = get_field(data, './/Signatur')
    document = get_document(uid, category)
    if not document:
        document = Document()
        document.category = [category]
        document.uid = uid
    extra_fields = {}
    document.title = get_field(data, './/Titel')
    document.description = get_field(data, './/Enthaelt')
    document.orderId = uid
    for key in ['Altsignatur', 'Sachbegriffe', 'Personen']:
        item = get_field(data, './/%s' % key)
        if item:
            extra_fields[key] = item
    document.extraFields = extra_fields
    # save document
    document.save()
    logger.info('dataimport.eadddb.document', 'document %s saved' % document.id)
    return document


def clean_text(text):
    return text.replace('<lb/>', ' ').strip()


def get_field(data, path):
    result = data.find(path)
    if result is None:
        return
    if not result.text:
        return
    return result.text
