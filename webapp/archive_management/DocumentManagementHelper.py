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
from PIL import Image
from minio.error import ResponseError, SignatureDoesNotMatch
from urllib3.exceptions import MaxRetryError
from flask import current_app
from ..models import File
from ..extensions import minio, logger, celery
from ..data_worker.DataWorkerThumbnails import DataWorkerThumbnails
from ..common.helpers import slugify


file_endings = {
    'image/tiff': 'tif',
    'image/jpeg': 'jpg',
    'application/pdf': 'pdf',
    'image/bmp': 'bmp',
    'image/png': 'png'
}


@celery.task()
def process_file(file_id):
    file = File.get(file_id)
    if not file:
        return
    file.binary_exists = True
    path = os.path.join(current_app.config['TEMP_UPLOAD_DIR'], str(file.id))
    file.size = os.path.getsize(path)
    metadata = {
        'Content-Disposition': 'filename=%s.%s' % (
            slugify(file.document.title) if file.document.title else file.document.id, file_endings[file.mimeType]
        )
    }
    try:
        minio.connection.fput_object(
            current_app.config['MINIO_BUCKET'],
            "files/%s/%s" % (file.document.id, file.id),
            path,
            content_type=file.mimeType,
            metadata=metadata
        )
    except (ResponseError, SignatureDoesNotMatch, MaxRetryError) as err:
        print(err)
        logger.info('admin.document.file', '%s %s: minio server error' % (file.id, file.document.id))
        return

    if file.mimeType not in ['application/pdf']:
        im = Image.open(path)
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

    dwt = DataWorkerThumbnails()
    dwt.prepare()
    dwt.file_thumbnails(file)
