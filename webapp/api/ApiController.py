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

import time
import json
from flask import (Flask, Blueprint, render_template, current_app, request, flash, url_for, redirect, session, abort,
                   jsonify, send_from_directory)
from ..common.response import json_response
from ..models import Document

api = Blueprint('api', __name__, template_folder='templates')


@api.route('/api/documents')
def documents_main():
    page = request.args.get('page', 1, type=int)
    documents_raw = Document.objects(help_required=True)[(page - 1) * 100:page * 100]
    documents = []
    for document_raw in documents_raw:
        document = document_raw.to_dict(deref='deref_document', format_datetime=True, delete='delete_document', clean_none=True)
        if 'files' in document:
            for i in range(0, len(document['files'])):
                document['files'][i]['accessUrl'] = '%s/files/%s/%s/show' % (current_app.config['MINIO_MEDIA_URL'], document['id'], document['files'][i]['id'])
                document['files'][i]['downloadUrl'] = '%s/files/%s/%s/download' % (current_app.config['MINIO_MEDIA_URL'], document['id'], document['files'][i]['id'])
        documents.append(document)
    return json_response({
        'data': documents,
        'pagination': {
            'next': '%s/api/documents?page=%s' % (current_app.config['PROJECT_URL'], page + 1)
        }
    })
