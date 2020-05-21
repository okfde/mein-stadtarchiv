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

import magic
from flask import current_app
from ..models import Category, Comment, Document, File, Tag
from ..extensions import minio
from minio.error import ResponseError, NoSuchKey
from ..data_worker.DataWorkerThumbnails import regenerate_thumbnails


def migrate_data(action):
    if action == 'camel_case':
        migrate_camel_case()
    if action == 'broken_files':
        broken_files()
    if action == 'consistent_files':
        consistent_files()
    if action == 'set_reverse_file':
        set_reverse_file()
    if action == 'reset_mimetype':
        reset_mimetype()
    if action == 'check_mimetypes':
        check_mimetypes()
    if action == 'check_thumbnails':
        check_thumbnails()


def reset_mimetype():
    for file in File.objects(thumbnailStatus='wrong-mimetype').all():
        file.thumbnailGenerated = None
        file.thumbnailStatus = None
        file.save()


def set_reverse_file():
    for document in Document.objects.all():
        for file in document.files:
            file.document = document
            file.save()


def migrate_camel_case():
    for category in Category.objects().all():
        if category.uploaded_file:
            category.uploadedFile = category.uploaded_file
        if category.order_id:
            category.orderId = category.order_id
        category.save()

    for comment in Comment.objects().all():
        if comment.author_name:
            comment.authorName = comment.author_name
        if comment.author_email:
            comment.authorEmail = comment.author_email
        comment.save()

    for document in Document.objects().all():
        if document.date_begin:
            document.dateBegin = document.date_begin
        if document.date_end:
            document.dateEnd = document.date_end
        if document.date_text:
            document.dateText = document.date_text
        if document.extra_fields:
            document.extraFields = document.extra_fields
        document.save()

    for file in File.objects().all():
        if file.binary_exists:
            file.binaryExists = file.binary_exists
        file.save()

    for tag in Tag.objects().all():
        if tag.order_number:
            tag.orderNumber = tag.order_number
        tag.save()


def broken_files():
    for file in File.objects(document__exists=False).all():
        print(file.id)


def consistent_files():
    for file in File.objects().all():
        if not file.document:
            continue
        try:
            data = minio.connection.get_object(
                current_app.config['MINIO_BUCKET'],
                "files/%s/%s" % (file.document.id, file.id)
            )
        except NoSuchKey:
            data = None
        if (data is not None) != file.binaryExists:
            file.binaryExists = data is not None
            file.save()


def check_mimetypes():
    for file in File.objects.all():
        try:
            data = minio.connection.get_object(
                current_app.config['MINIO_BUCKET'],
                "files/%s/%s" % (file.document.id, file.id)
            )
        except NoSuchKey:
            continue
        magic_mime = magic.from_buffer(data, mime=True)
        if file.mimeType != magic_mime:
            print('file %s has db mime %s and magic mime %s' % (file.id, file.mimeType, magic_mime))


def check_thumbnails():
    for file in File.objects(binaryExists=1).all():
        try:
            data = minio.connection.get_object(
                current_app.config['MINIO_BUCKET'],
                "thumbnails/%s/%s/1200/1.jpg" % (file.document.id, file.id)
            )
        except NoSuchKey:
            data = None
        if data is None:
            print('file %s thumbnail missing' % file.id)
            regenerate_thumbnails(file.id)
