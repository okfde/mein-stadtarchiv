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
import re
from flask import current_app, abort, request, jsonify
from flask_login import current_user
from ..models import Category, File, Document
from ..common.response import json_response
from .CategoryManagementForms import CategorySearchForm

from webapp.archive_management.DocumentManagementHelper import process_file
from webapp.common.elastic_request import ElasticRequest
from webapp.extensions import csrf

from .ArchiveManagementController import archive_management


@archive_management.route('/api/admin/archive/categories', methods=['POST'])
def api_admin_categories():
    if not current_user.has_capability('admin'):
        abort(403)
    form = CategorySearchForm()
    if not form.validate_on_submit():
        return json_response({
            'status': -1
        })
    archives = Category.objects(parent__exists=False)
    count = archives.count()
    archives = archives.order_by('%s%s' % ('+' if form.sort_order.data == 'asc' else '-', form.sort_field.data))\
        .limit(current_app.config['ITEMS_PER_PAGE'])\
        .skip((form.page.data - 1) * current_app.config['ITEMS_PER_PAGE'])\
        .all()
    data = []
    for archive in archives:
        data.append(archive.to_dict())

    return json_response({
        'data': data,
        'status': 0,
        'count': count
    })


@csrf.exempt
@archive_management.route('/api/admin/archive/<string:archive_id>/category/<string:category_id>/upload', methods=['POST'])
def archive_category_upload_file(archive_id, category_id):
    if not current_user.has_capability('admin'):
        abort(403)
    archive = Category.get_or_404(archive_id)
    category = Category.get_or_404(category_id)

    elastic_request = ElasticRequest(
        current_app.config['ELASTICSEARCH_DOCUMENT_INDEX'] + '-latest',
        'document'
    )
    elastic_request.set_fq('category_with_parents', category_id)
    elastic_request.query_parts_should = [
            {"range": {"file_missing_count": {"gte": 1}}},
            {"range": {"file_count": {"gte": 1}}}
        ],
    elastic_request.set_limit(32000)
    elastic_request.query()
    documents = elastic_request.get_results()

    if request.files:
        uploaded_file = request.files['file']
        # Hacky way of uploading files because at Stadtarchiv Moers, there's no connection between Document and File in XML
        print(archive.title)
        if archive.title == 'Stadtarchiv Moers':
            document, matching_file = get_matching_document_file_stadtarchiv_moers(archive, uploaded_file)
            if not document:
                return jsonify({'error': 'Dateiname wurde in keinem Dokument dieser Kategorie gefunden.'}), 400
        else:
            matching_file_as_dict, document_as_dict = get_matching_file(uploaded_file, documents)
            if not matching_file_as_dict:
                return jsonify({'error': 'Dateiname wurde in keinem Dokument dieser Kategorie gefunden.'}), 400

            # we need to fetch this document and assign it to the matching_file, because the process_file
            # function will use this property later on - mongoengine does not dereference it.
            document = Document.get(document_as_dict.get('id'))
            if not document:
                return jsonify({'error': 'Das angegebene Dokument ist indiziert, wurde jedoch nicht in der Datenbank gefunden.'}), 400
            matching_file = File.get(matching_file_as_dict.get('id'))
            if not matching_file:
                return jsonify({'error': 'Die angegebene Datei ist indiziert, wurde jedoch nicht in der Datenbank gefunden.'}), 400

        matching_file.mimeType = uploaded_file.content_type
        matching_file.document = document
        matching_file.save()
        if matching_file not in matching_file.document.files:
            if matching_file.document.files:
                matching_file.document.files.append(matching_file)
            else:
                matching_file.document.files = [matching_file]
        matching_file.document.save()

        # This should be part of the process_file function
        path = os.path.join(current_app.config['TEMP_UPLOAD_DIR'], str(matching_file.id))
        uploaded_file.seek(0)
        uploaded_file.save(path)

        process_file.delay(str(matching_file.id))

    return jsonify(success=True)


def get_matching_file(uploaded_file, documents):
    for document in documents:
        for file in document['files']:
            if file.get('fileName') in [uploaded_file.filename, uploaded_file.filename.split('.')[0]]:
                return file, document
    return None, None


def get_matching_document_file_stadtarchiv_moers(archiv, uploaded_file):
    allowed_categories = archiv.get_children_list()
    re_id = re.match("^60-([0-9]+)_", uploaded_file.filename)
    if not re_id:
        return None, None
    if not re_id.group(1):
        return None, None
    document = Document.objects(uid=re_id.group(1), category__in=allowed_categories).first()
    if not document:
        return None, None
    file = File()
    file.fileName = uploaded_file.filename
    return document, file
