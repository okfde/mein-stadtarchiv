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


class BaseConfig:
    INSTANCE_FOLDER_PATH = os.path.join('/tmp', 'instance')

    PROJECT_NAME = 'mein-stadtarchiv'
    PROJECT_VERSION = '2.0.0'

    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    LOG_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, os.pardir, 'logs'))
    DATA_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, os.pardir, 'data'))
    SITEMAP_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, os.pardir, 'static', 'sitemap'))
    TEMP_DIR = os.path.join(PROJECT_ROOT, os.pardir, 'temp')
    TEMP_UPLOAD_DIR = os.path.abspath(os.path.join(TEMP_DIR, 'upload'))
    TEMP_THUMBNAIL_DIR = os.path.abspath(os.path.join(TEMP_DIR, 'thumbnails'))

    REQUIRED_CONFIG_FIELDS = [
        'PROJECT_URL',
        'SECRET_KEY',
        'SECURITY_PASSWORD_SALT',
        'ADMINS',
        'MAILS_FROM',
        'MAIL_SERVER',
        'MAIL_USERNAME',
        'MAIL_PASSWORD',
        'S3_ACCESS_KEY',
        'S3_ACCESS_KEY',
        'S3_MEDIA_URL',
        'AUTH',
        'MAPBOX_TOKEN'
    ]

    DEBUG = False
    TESTING = False

    MAIL_PORT = 587
    MAIL_USE_SSL = False
    MAIL_USE_TLS = True

    MONGODB_HOST = 'localhost'
    MONGODB_PORT = 27017
    MONGODB_DB = 'stadtarchiv'

    MINIO_ENDPOINT = 'localhost'
    MINIO_SECURE = False
    MINIO_REGION = 'us-east-1'
    MINIO_BUCKET = 'stadtarchiv'

    CELERY_BROKER_URL = 'amqp://localhost'

    MAPBOX_CENTER_LAT = 51.470915
    MAPBOX_CENTER_LON = 7.219874
    MAPBOX_ZOOM = 10

    ELASTICSEARCH_HOST = 'localhost'
    ELASTICSEARCH_DOCUMENT_INDEX = 'stadtarchiv-documents'

    PDFTOTEXT_COMMAND = '/usr/bin/pdftotext'
    ABIWORD_COMMAND = '/usr/bin/abiword'
    GHOSTSCRIPT_COMMAND = '/usr/bin/gs'
    JPEGOPTIM_PATH = '/usr/bin/jpegoptim'
    GZIP_PATH = '/bin/gzip'

    ITEMS_PER_PAGE = 10

    THUMBNAIL_SIZES = [150, 300, 600, 1200]
    IMAGE_MIMETYPES = ['image/jpeg', 'image/png', 'image/tiff', 'image/bmp']
