# encoding: utf-8

"""
Copyright (c) 2019, Ernesto Ruge
All rights reserved.
Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

from .common.constants import BaseConfig


class DefaultConfig(BaseConfig):
    PROJECT_URL = 'http://srv:5000'

    DEBUG = True

    ADMINS = ['mail@ernestoruge.de']
    MAILS_FROM = 'mail@ernestoruge.de'

    SECRET_KEY = ''
    SECURITY_PASSWORD_SALT = ''

    MONGODB_HOST = 'mongodb'

    S3_ENDPOINT = 'minio'
    S3_ACCESS_KEY = 'DEVELOPMENT'
    S3_SECRET_KEY = 'DEVELOPMENT'
    S3_MEDIA_URL = 'http://srv:9000'

    CELERY_RESULT_BACKEND = 'amqp://rabbitmq'
    CELERY_BROKER_URL = 'amqp://rabbitmq'

    MAPBOX_TOKEN = 'pk.eyJ1IjoiZXJuZXN0by1ydWdlIiwiYSI6ImNpcWljOWVrMDAwYjdocG1jM2dlcno0dWIifQ.uFojO1A56WY5j6LoHPg2IA'

    ELASTICSEARCH_HOST = 'elasticsearch'


class DevelopmentConfig(DefaultConfig):
    MODE = 'DEVELOPMENT'


class StagingConfig(DefaultConfig):
    MODE = 'STAGING'


class ProductionConfig(DefaultConfig):
    MODE = 'PRODUCTION'


class SandboxConfig(DefaultConfig):
    MODE = 'SANDBOX'


def get_config(MODE):
    SWITCH = {
        'DEVELOPMENT': DevelopmentConfig,
        'STAGING': StagingConfig,
        'PRODUCTION': ProductionConfig,
        'SANDBOX': SandboxConfig
    }
    return SWITCH[MODE]
