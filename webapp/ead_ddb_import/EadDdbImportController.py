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

import os
import datetime
from lxml import etree
from flask import (Flask, Blueprint, render_template, current_app, request, flash, url_for, redirect, session, abort,
                   jsonify, send_from_directory)
from ..common.response import json_response, xml_response
from ..common.helpers import get_minio_connection, slugify
from ..extensions import csrf
from ..models import Dump, Category, Document, File
from dateutil.parser import parse as dateutil_parser
from minio.error import ResponseError, SignatureDoesNotMatch
from urllib3.exceptions import MaxRetryError
from PIL import Image

ead_ddb_import = Blueprint('ead_ddb_import', __name__, template_folder='templates')

file_endings = {
    'image/tiff': 'tif',
    'image/jpeg': 'jpg',
    'application/pdf': 'pdf',
    'image/bmp': 'bmp',
    'image/png': 'png'
}

@ead_ddb_import.route('/api/ead-ddb/push-data', methods=['POST'])
@csrf.exempt
def ead_ddb_push_data():
    # save data dump
    if request.args.get('auth', '') != current_app.config['AUTH']:
        abort(403)

    dump = Dump()
    dump.data = request.get_data(as_text=True)
    dump.save()
    # read xml
    try:
        xml_data = etree.fromstring(request.data)
    except etree.XMLSyntaxError:
        return xml_response(generate_xml_answer('incomplete', 'xml data could not be parsed'))

    # prepare namespace
    namespaces = xml_data.nsmap
    namespaces['ns'] = namespaces[None]
    del namespaces[None]

    # statistic vars
    document_count = 0
    category_count = 0

    # read and save archive
    archive_title = xml_data.xpath('.//ns:archdesc[@level="collection"]/ns:did/ns:repository/ns:corpname',
                                   namespaces=namespaces)
    if not len(archive_title):
        return xml_response(generate_xml_answer('incomplete', 'no archive title found'))
    archive_title = archive_title[0].text
    archive = Category.objects(uid=archive_title).upsert_one(set__title=archive_title, set__uid=archive_title)
    category_count += 1

    file_missing_binaries = []
    # we support multible collections (does this ever happen?)
    collections_xml = xml_data.xpath('.//ns:archdesc[@level="collection"]/ns:dsc/ns:c[@level="collection"]',
                                     namespaces=namespaces)
    for collection_xml in collections_xml:

        # save collection
        collection_uid = collection_xml.get('id')
        collection_title = collection_xml.xpath('./ns:did/ns:unittitle', namespaces=namespaces)
        collection_descr = collection_xml.xpath('./ns:scopecontent/ns:p', namespaces=namespaces)
        collection_order_id = collection_xml.xpath('./ns:did/ns:unitid', namespaces=namespaces)
        upsert_values = {
            'set__uid': collection_uid,
            'set__parent': archive
        }
        if len(collection_title):
            if collection_title[0].text:
                upsert_values['set__title'] = collection_title[0].text
        if len(collection_order_id):
            if collection_order_id[0].text:
                upsert_values['set__order_id'] = collection_order_id[0].text
        if len(collection_descr):
            if collection_descr[0].text:
                upsert_values['set__description'] = collection_descr[0].text.replace('<lb/>', ' ')

        collection = Category.objects(uid=collection_uid).upsert_one(**upsert_values)
        category_count += 1

        # first: no subcollection
        documents_xml = collection_xml.xpath('./ns:c[@level="file"]', namespaces=namespaces)
        for document_xml in documents_xml:
            document, file_missing_binaries_single = save_document(document_xml, collection, namespaces)
            if document:
                document_count += 1
            if file_missing_binaries_single:
                file_missing_binaries += file_missing_binaries_single

        # second: subcollection(s)
        subcollections_xml = collection_xml.xpath('.//ns:c[@level="class"]', namespaces=namespaces)
        for subcollection_xml in subcollections_xml:
            subcollection_uid = subcollection_xml.get('id')
            subcollection_title = subcollection_xml.xpath('./ns:did/ns:unittitle', namespaces=namespaces)
            subcollection_order_id = subcollection_xml.xpath('./ns:did/ns:unitid', namespaces=namespaces)
            upsert_values = {
                'set__uid': subcollection_uid,
                'set__parent': collection
            }
            if len(subcollection_title):
                if subcollection_title[0].text:
                    upsert_values['set__title'] = subcollection_title[0].text
            if len(subcollection_order_id):
                if subcollection_order_id[0].text:
                    upsert_values['set__order_id'] = subcollection_order_id[0].text

            subcollection = Category.objects(uid=subcollection_uid).upsert_one(**upsert_values)
            category_count += 1

            documents_xml = subcollection_xml.xpath('./ns:c[@level="file"]', namespaces=namespaces)
            for document_xml in documents_xml:
                document, file_missing_binaries_single = save_document(document_xml, subcollection, namespaces)
                if document:
                    document_count += 1
                if file_missing_binaries_single:
                    file_missing_binaries += file_missing_binaries_single

    return xml_response(generate_xml_answer('ok', 'saved %s documents in %s categories' % (document_count, category_count), file_missing_binaries))


def save_document(document_xml, category, namespaces):
    file_missing_binaries = []
    document_uid = document_xml.get('id')
    if not document_uid:
        return False, False
    upsert_values = {
        'set__uid': document_uid,
        'set__category': [category],
        'set__modified': datetime.datetime.now()
    }
    # title
    title = document_xml.xpath('./ns:did/ns:unittitle', namespaces=namespaces)
    if len(title):
        if title[0].text:
            title = title[0].text.replace('<lb/>', ' ')
            if '§§ unbekannte Darstellung' in title:
                title = title.replace('§§ unbekannte Darstellung', '')
                upsert_values['set__help_required'] = 1
            upsert_values['set__title'] = title.strip()

    # restricted
    restricted = document_xml.xpath('./ns:accessrestrict', namespaces=namespaces)
    if len(restricted):
        return False, False

    # order_id
    order_id = document_xml.xpath('./ns:did/ns:unitid', namespaces=namespaces)
    if len(order_id):
        if order_id[0].text:
            upsert_values['set__order_id'] = order_id[0].text.replace('<lb/>', ' ')

    # origination
    origination = document_xml.xpath('./ns:did/ns:origination', namespaces=namespaces)
    if len(origination):
        if origination[0].text:
            upsert_values['set__origination'] = origination[0].text.replace('<lb/>', ' ')

    # description (findbuch-specific?)
    description = document_xml.xpath("./ns:did/ns:abstract[@type='Enthält']", namespaces=namespaces)
    if len(description):
        if description[0].text:
            upsert_values['set__description'] = description[0].text.replace('<lb/>', ' ')

    # note
    note = document_xml.xpath('./ns:did/ns:note', namespaces=namespaces)
    if len(note):
        upsert_values['set__note'] = etree.tostring(note[0]).replace('<lb/>', ' ')

    date = document_xml.xpath('./ns:did/ns:unitdate', namespaces=namespaces)
    if len(date):
        date_result = {}
        if date[0].text:
            upsert_values['set__date_text'] = date[0].text
        if 'normal' in date[0].attrib:
            date_normalized = date[0].attrib['normal']
            if '/' in date_normalized:
                date_normalized = date_normalized.split('/')
                if date_normalized[0] == date_normalized[1]:
                    date_result['date'] = datetime.datetime.strptime(date_normalized[0], '%Y-%m-%d')
                else:
                    date_result['begin'] = datetime.datetime.strptime(date_normalized[0], '%Y-%m-%d')
                    date_result['end'] = datetime.datetime.strptime(date_normalized[1], '%Y-%m-%d')
            else:
                date_result['date'] = datetime.datetime.strptime(date_normalized, '%Y-%m-%d')
        if 'date' in date_result:
            upsert_values['set__date'] = date_result['date']
        if 'begin' in date_result:
            upsert_values['set__date_begin'] = date_result['begin']
        if 'end' in date_result:
            upsert_values['set__date_end'] = date_result['end']

    # files
    files = []
    files_xml = document_xml.xpath('./ns:daogrp/ns:daodesc/ns:list/ns:item', namespaces=namespaces)
    for file_xml in files_xml:
        file_name = file_xml.xpath('./ns:name', namespaces=namespaces)
        if not len(file_name):
            continue
        file_name = file_name[0].text
        if not file_name:
            continue
        file_upsert_values = {
            'set__externalId': document_uid + '-' + file_name,
        }
        file = File.objects(externalId=document_uid + '-' + file_name).upsert_one(**file_upsert_values)
        if not file.binary_exists:
            file_missing_binaries.append(file.externalId)
        files.append(file)
    if len(files):
        upsert_values['set__files'] = files

    # all other values
    extra_fields = {}
    extra_fields_raw = document_xml.xpath('./ns:odd', namespaces=namespaces)
    for extra_field_raw in extra_fields_raw:
        field_title = extra_field_raw.xpath('./ns:head', namespaces=namespaces)
        field_value = extra_field_raw.xpath('./ns:p', namespaces=namespaces)
        if len(field_title) and len(field_value):
            if field_title[0].text:
                extra_fields[field_title[0].text] = field_value[0].text.replace('<lb/>', ' ')
    if len(extra_fields.keys()):
        upsert_values['set__extra_fields'] = extra_fields

    # save document
    document = Document.objects(uid=document_uid).upsert_one(**upsert_values)
    return document, file_missing_binaries


@ead_ddb_import.route('/api/ead-ddb/push-file', methods=['POST'])
@csrf.exempt
def ead_ddb_push_media():
    if request.args.get('auth', '') != current_app.config['AUTH']:
        abort(403)
    file_name = request.form.get('name')
    document_uid = request.form.get('document_uid')
    if not file_name or not document_uid:
        return xml_response(generate_xml_answer('data missing', 'file not saved'))

    file = File.objects(externalId=document_uid + '-' + file_name).first()
    if not file:
        return xml_response(generate_xml_answer('file not registered', 'file not registered'))

    document = Document.objects(uid=document_uid).first()
    if not document:
        return xml_response(generate_xml_answer('document not registered', 'document not registered'))

    file.size = request.form.get('size')
    file.mimeType = request.form.get('mimeType')
    file.fileName = request.form.get('fileName')
    file.sha1Checksum = request.form.get('sha1Checksum')
    file.modified = datetime.datetime.now()
    file.binary_exists = True

    file_path = os.path.join(current_app.config['TEMP_UPLOAD_DIR'], '%s-%s' % (document_uid, file_name))
    request.files['file'].save(file_path)
    metadata = {
        'Content-Disposition': 'filename=%s.%s' % (slugify(document.title) if document.title else document.id, file_endings[file.mimeType])
    }
    try:
        s3 = get_minio_connection()
        s3.fput_object(
            current_app.config['S3_BUCKET'],
            "files/%s/%s" % (document.id, file.id),
            file_path,
            content_type=file.mimeType,
            metadata=metadata
        )
    except (ResponseError, SignatureDoesNotMatch, MaxRetryError) as err:
        return xml_response(generate_xml_answer('server error', 'saving file to minio failed'))

    if file.mimeType in ['application/pdf']:
        pass
    else:
        im = Image.open(file_path)
        (width, height) = im.size
        file.pages = 1
        file.thumbnails = {
            '1': {
                'sizes': {
                    'original': {
                        'height': height,
                        'width': width,
                        'size': file.size
                    }
                }
            }
        }
        im.close()

    file.save()

    # tidy up
    os.remove(file_path)

    return xml_response(generate_xml_answer('ok', 'file saved'))


def generate_xml_answer(status, description=None, missing_files=None):
    nsmap = {
        'soapenv': 'http://schemas.xmlsoap.org/soap/envelope',
        'ead-ddb-push': 'https://ead-ddb.de/model/1.0'
    }
    result = etree.Element(
        "{%s}Envelope" % nsmap['soapenv'],
        nsmap=nsmap
    )
    result.append(
        etree.Element(
            "{%s}Header" % nsmap['soapenv'],
            nsmap=nsmap
        )
    )
    result.append(
        etree.Element(
            "{%s}Body" % nsmap['soapenv'],
            nsmap=nsmap
        )
    )
    result[1].append(
        etree.Element(
            "{%s}Status" % nsmap['ead-ddb-push'],
            nsmap=nsmap
        )
    )
    result[1][0].text = status
    if description:
        result[1].append(
            etree.Element(
                "{%s}Description" % nsmap['ead-ddb-push'],
                nsmap=nsmap
            )
        )
        result[1][1].text = description
    if missing_files:
        missing_files_xml = etree.Element(
            "{%s}MissingFiles" % nsmap['ead-ddb-push'],
            nsmap=nsmap
        )
        for missing_file in missing_files:
            missing_file_xml = etree.Element(
                "{%s}MissingFile" % nsmap['ead-ddb-push'],
                nsmap=nsmap
            )
            missing_file_xml.text = missing_file
            missing_files_xml.append(missing_file_xml)
        result[1].append(missing_files_xml)
    return result
