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


from .DataWorkerElasticsearch import DataWorkerElasticsearch
from .DataWorkerThumbnails import DataWorkerThumbnails
from .DataWorkerSitemap import DataWorkerSitemap
from ..models import User, Document, File
from ..extensions import celery


"""
def worker():
    #data_worker_thumbnails = DataWorkerThumbnails()
    #data_worker_thumbnails.run()
    data_worker_elasticsearch = DataWorkerElasticsearch()
    data_worker_elasticsearch.run()
    #data_worker_sitemap = DataWorkerSitemap()
    #data_worker_sitemap.run()


@celery.task()
def worker_celery_full():
    data_worker_elasticsearch = DataWorkerElasticsearch()
    data_worker_elasticsearch.run()
    data_worker_sitemap = DataWorkerSitemap()
    data_worker_sitemap.run()
"""


@celery.task()
def process_document_delay(document_id):
    document = Document.get(document_id)
    if not document:
        return
    process_document(document)


def process_document(document):
    data_worker_elasticsearch = DataWorkerElasticsearch()
    data_worker_elasticsearch.prepare()
    data_worker_elasticsearch.index_document(document)


@celery.task()
def process_file_delay(file_id):
    file = File.get(file_id)
    if not file:
        return
    process_file(file)


def process_file(file):
    data_worker_thumbnails = DataWorkerThumbnails()
    data_worker_thumbnails.prepare()
    data_worker_thumbnails.file_thumbnails(file)


def upsert_login(email, password):
    user = User.objects(email=email).first()
    if not user:
        user = User()
        user.email = email
    user.capabilities = ['admin']
    user.password = password
    user.save()

