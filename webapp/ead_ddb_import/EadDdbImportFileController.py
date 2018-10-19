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
from flask import current_app, request, abort
from ..common.response import json_response, xml_response
from ..common.helpers import get_minio_connection, slugify
from ..extensions import csrf, logger
from ..models import Document, File, Category
from minio.error import ResponseError, SignatureDoesNotMatch
from urllib3.exceptions import MaxRetryError
from PIL import Image
from ..data_worker.DataWorkerHelper import worker_celery_single

from .EadDdbImportController import ead_ddb_import, generate_xml_answer

Image.MAX_IMAGE_PIXELS = None

file_endings = {
    'image/tiff': 'tif',
    'image/jpeg': 'jpg',
    'application/pdf': 'pdf',
    'image/bmp': 'bmp',
    'image/png': 'png'
}


@ead_ddb_import.route('/api/ead-ddb/push-file', methods=['POST'])
@csrf.exempt
def ead_ddb_push_media():
    logger.info('api.eadddb.file.debug', request.headers)
    logger.info('api.eadddb.file.debug', request.form)
    logger.info('api.eadddb.file.debug', request.files)

    auth = request.headers.get('X-Auth', None)
    if not auth:
        auth = request.args.get('auth', None)

    if not Category.objects(auth=auth).first():
        logger.info('api.eadddb.file.reply', 'invalid-auth')
        return xml_response(generate_xml_answer('invalid-auth', 'invalid auth'))
    file_name = request.form.get('name')
    if not file_name:
        file_name = request.form.get('fileName')
        if file_name:
            file_name = '.'.join(file_name.split('.')[0:-1])
    document_uid = request.form.get('document_uid')
    if not file_name or not document_uid:
        logger.info('api.eadddb.file.reply', 'data missing')
        return xml_response(generate_xml_answer('data missing', 'file not saved'))

    file = File.objects(externalId=document_uid + '-' + file_name).first()
    if not file:
        logger.info('api.eadddb.file.reply', '%s %s: file not registered' % (file_name, document_uid))
        return xml_response(generate_xml_answer('file not registered', 'file not registered'))

    document = Document.objects(uid=document_uid).first()
    if not document:
        logger.info('api.eadddb.file.reply', '%s %s: document not registered' % (file_name, document_uid))
        return xml_response(generate_xml_answer('document not registered', 'document not registered'))

    file.size = request.form.get('size')
    file.mimeType = request.form.get('mimeType')
    file.fileName = request.form.get('fileName')
    file.sha1Checksum = request.form.get('sha1Checksum')
    file.modified = datetime.datetime.now()
    file.binary_exists = True
    if file.mimeType not in file_endings.keys():
        logger.info('api.eadddb.file.reply', '%s %s: invalid mime type' % (file_name, document_uid))
        return xml_response(generate_xml_answer('invalid mime type', 'invalid mime type'))
    logger.info('api.eadddb.file', 'file %s was uploaded for document %s' % (file_name, document_uid))

    file_path = os.path.join(current_app.config['TEMP_UPLOAD_DIR'], '%s-%s' % (document_uid, file_name))
    request.files.get('file').save(file_path)
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
        logger.info('api.eadddb.file.reply', '%s %s: minio server error' % (file_name, document_uid))
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

    worker_celery_single.delay(str(document.id))
    return xml_response(generate_xml_answer('ok', 'file saved'))

