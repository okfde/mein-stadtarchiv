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

import re
import codecs
import string
from random import SystemRandom
import translitcodec
from flask import current_app
from datetime import datetime, timedelta
from flask.json import JSONEncoder as BaseJSONEncoder
from minio import Minio
from minio.error import ResponseError, BucketAlreadyOwnedByYou, BucketAlreadyExists


slugify_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')


def get_random_password(length=32):
    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return ''.join(SystemRandom().choice(chars) for _ in range(length))


def get_current_time():
    return datetime.utcnow()


def slugify(text, delim='-'):
    result = []
    for word in slugify_re.split(text.lower()):
        word = codecs.encode(word, 'translit/long')
        if word:
            result.append(word)
    return delim.join(result)


def get_current_time_plus(days=0, hours=0, minutes=0, seconds=0):
    return get_current_time() + timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)


def get_minio_connection():
    s3 = Minio(
        current_app.config['S3_ENDPOINT'],
        access_key=current_app.config['S3_ACCESS_KEY'],
        secret_key=current_app.config['S3_SECRET_KEY'],
        secure=current_app.config['S3_SECURE']
    )
    try:
        s3.make_bucket(current_app.config['S3_BUCKET'], location=current_app.config['S3_LOCATION'])
    except BucketAlreadyOwnedByYou as err:
        pass
    except BucketAlreadyExists as err:
        pass
    #if s3.get_bucket_policy(current_app.config['S3_BUCKET'], 'files') != 'readonly':
    #    s3.set_bucket_policy(current_app.config['S3_BUCKET'], 'files', Policy.READ_ONLY)
    #if s3.get_bucket_policy(current_app.config['S3_BUCKET'], 'thumbnails') != 'readonly':
    #    s3.set_bucket_policy(current_app.config['S3_BUCKET'], 'thumbnails', Policy.READ_ONLY)
    return s3


