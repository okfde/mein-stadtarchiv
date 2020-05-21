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


def get_document(data, parent, nsmap):
    return Document.objects(category=[parent], uid=get_identifier(data, nsmap)).first()


def get_identifier(data, nsmap):
    document_id = data.get('id')
    if not document_id:
        document_id = data.xpath('./ns:did/ns:unitid', namespaces=nsmap)
        if len(document_id):
            document_id = document_id[0].text
        else:
            document_id = None
    if not document_id:
        document_id = data.xpath('./ns:did/ns:unittitle', namespaces=nsmap)
        if len(document_id):
            document_id = document_id[0].text
        else:
            document_id = None
    if not document_id:
        return
    return document_id


def save_document(data, parent, nsmap):
    document_id = get_identifier(data, nsmap)
    if not document_id:
        return document_id

    document = get_document(data, parent, nsmap)
    if not document:
        document = Document()
        document.uid = data.get('id')
        document.category = [parent]

    # title
    title = data.xpath('./ns:did/ns:unittitle', namespaces=nsmap)
    title = clean_text(title[0].text) if len(title) else ''
    if '§§ unbekannte Darstellung' in title:
        title = title.replace('§§ unbekannte Darstellung', '')
        document.help_required = 1
    document.title = title.strip()

    # restricted
    restricted = data.xpath('./ns:accessrestrict', namespaces=nsmap)
    if len(restricted):
        return False, False

    # order_id
    order_id = data.xpath('./ns:did/ns:unitid', namespaces=nsmap)
    document.orderId = clean_text(order_id[0].text) if len(order_id) else ''

    # origination
    origination = data.xpath('./ns:did/ns:origination', namespaces=nsmap)
    document.origination = clean_text(origination[0].text) if len(origination) else ''

    # description (findbuch-specific?)
    description = data.xpath("./ns:did/ns:abstract[@type='Enthält']", namespaces=nsmap)
    document.description = clean_text(description[0].text) if len(description) else ''

    # note
    note = data.xpath('./ns:did/ns:note', namespaces=nsmap)
    document.note = clean_text(etree.tostring(note[0]).text) if len(note) else ''

    date = data.xpath('./ns:did/ns:unitdate', namespaces=nsmap)
    if len(date):
        date_result = {}
        if date[0].text:
            document.date_text = date[0].text
        if 'normal' in date[0].attrib:
            date_normalized = date[0].attrib['normal']
            if '/' in date_normalized:
                date_normalized = date_normalized.split('/')
                if date_normalized[0] == date_normalized[1]:
                    date_result['date'] = datetime.strptime(date_normalized[0], '%Y-%m-%d')
                else:
                    date_result['begin'] = datetime.strptime(date_normalized[0], '%Y-%m-%d')
                    date_result['end'] = datetime.strptime(date_normalized[1], '%Y-%m-%d')
            else:
                date_result['date'] = datetime.strptime(date_normalized, '%Y-%m-%d')
        if 'date' in date_result:
            document.date = date_result['date']
        if 'begin' in date_result:
            document.date_begin = date_result['begin']
        if 'end' in date_result:
            document.date_end = date_result['end']

    # files
    files = []
    files_xml = data.xpath('./ns:daogrp/ns:daodesc/ns:list/ns:item', namespaces=nsmap)
    for file_xml in files_xml:
        file_name = file_xml.xpath('./ns:name', namespaces=nsmap)
        if not len(file_name):
            continue
        file_name = file_name[0].text
        if not file_name:
            continue
        file_upsert_values = {
            'set__externalId': data.get('id') + '-' + file_name,
            'set__fileName': file_name
        }
        file = File.objects(externalId=data.get('id') + '-' + file_name).upsert_one(**file_upsert_values)
        files.append(file)
    document.files = files

    # all other values
    extra_fields = {}
    for extra_field_raw in data.xpath('./ns:odd', namespaces=nsmap):
        field_title = extra_field_raw.xpath('./ns:head', namespaces=nsmap)
        field_value = extra_field_raw.xpath('./ns:p', namespaces=nsmap)
        if len(field_title) and len(field_value) and len(clean_text(field_title[0].text)):
            extra_fields[clean_text(field_title[0].text)] = clean_text(field_value[0].text)
    if len(extra_fields.keys()):
        document.extra_fields = extra_fields

    # save document
    document.save()
    logger.info('dataimport.eadddb.document', 'document %s saved' % document.id)
    return document


def clean_text(text):
    return text.replace('<lb/>', ' ').strip()
