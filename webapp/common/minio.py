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


import json
import minio
from io import BytesIO
from flask import current_app, _app_ctx_stack


class Minio(object):
    """This class is used to control the Minio integration to one or more Flask
    applications.
    """

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.teardown_appcontext(self.teardown)

    def connect(self):
        connection = minio.Minio(
            current_app.config['MINIO_ENDPOINT'],
            access_key=current_app.config['MINIO_ACCESS_KEY'],
            secret_key=current_app.config['MINIO_SECRET_KEY'],
            secure=current_app.config['MINIO_SECURE'],
            region=current_app.config['MINIO_REGION']
        )
        if not connection.bucket_exists(current_app.config['MINIO_BUCKET']):
            connection.make_bucket(current_app.config['MINIO_BUCKET'], location=current_app.config['MINIO_REGION'])
        try:
            connection.stat_object(current_app.config['MINIO_BUCKET'], 'files/.miniokeep')
        except minio.error.NoSuchKey:
            miniokeep = BytesIO(b'')
            connection.put_object(current_app.config['MINIO_BUCKET'], 'files/.miniokeep', miniokeep, 0, 'text/plain')
        try:
            connection.stat_object(current_app.config['MINIO_BUCKET'], 'thumbnails/.miniokeep')
        except minio.error.NoSuchKey:
            miniokeep = BytesIO(b'')
            connection.put_object(current_app.config['MINIO_BUCKET'], 'thumbnails/.miniokeep', miniokeep, 0, 'text/plain')
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": ["*"]},
                    "Action": ["s3:GetBucketLocation"],
                    "Resource": ["arn:aws:s3:::%s" % current_app.config['MINIO_BUCKET']]
                },
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": ["*"]},
                    "Action": ["s3:GetObject"],
                    "Resource": [
                        "arn:aws:s3:::%s/thumbnails*" % current_app.config['MINIO_BUCKET'],
                        "arn:aws:s3:::%s/files*" % current_app.config['MINIO_BUCKET']
                    ]
                },
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": ["*"]},
                    "Action": ["s3:ListBucket"],
                    "Resource": ["arn:aws:s3:::%s" % current_app.config['MINIO_BUCKET']],
                    "Condition": {"StringEquals": {"s3:prefix": ["files", "thumbnails"]}}
                }
            ]
        }
        connection.set_bucket_policy(current_app.config['MINIO_BUCKET'], json.dumps(policy))
        return connection

    def teardown(self, exception):
        ctx = _app_ctx_stack.top
        if hasattr(ctx, 'minio'):
            ctx.minio._http.clear()

    @property
    def connection(self):
        ctx = _app_ctx_stack.top
        if ctx is not None:
            if not hasattr(ctx, 'minio'):
                ctx.minio = self.connect()
            return ctx.minio