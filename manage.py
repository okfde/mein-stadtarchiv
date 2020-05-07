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

from flask_script import Manager, Shell, Server
from flask import current_app
from webapp import launch
from webapp.extensions import db, celery
import webapp.models as Models
from webapp.data_worker.DataWorkerElasticsearchIndex import create_index as create_index_run
from webapp.data_worker.DataWorkerHelper import worker as data_worker_run, upsert_login as upsert_login_run
from webapp.admin.AdminHelper import set_auth as set_auth_run, missing_media as missing_media_run, \
    file_document_reverse as file_document_reverse_run, reset_elasticsearch_last_run as reset_elasticsearch_last_run_run, \
    init_archive as init_archive_run
from webapp.data_worker.DataWorkerThumbnails import regenerate_thumbnails as regenerate_thumbnails_run
from webapp.data_worker.DataWorkerGeoreference import DataWorkerGeoreference

app = launch()
manager = Manager(app)


@manager.shell
def make_shell_context():
    return dict(app=current_app, db=db, models=Models)


@manager.command
def create_index():
    """
    (re)creates elasticsearch index
    """
    create_index_run()


@manager.command
def data_worker():
    """
    processes all uploaded data
    """
    data_worker_run()


@manager.command
def upsert_login(email, password):
    """
    upserts a login
    """
    upsert_login_run(email, password)


@manager.command
def set_auth(category_id, auth):
    """
    sets an auth by category
    """
    set_auth_run(category_id, auth)


@manager.command
def missing_media():
    """
    outputs all missing media
    """
    missing_media_run()


@manager.command
def file_document_reverse():
    """
    creates reverse references for files
    """
    file_document_reverse_run()


@manager.command
def reset_elasticsearch_last_run():
    """
    resets last elasticsearch run
    """
    reset_elasticsearch_last_run_run()


@manager.command
def init_archive(title, auth):
    """
    inittializes archove by title and auth
    """
    init_archive_run(title, auth)


@manager.command
def georeference(category_id):
    """
    georeferences documents by category
    """
    dwg = DataWorkerGeoreference()
    dwg.run(category_id)


@manager.command
def regenerate_thumbnails(file_id):
    """
    regenerate thumbnails by file id
    """
    regenerate_thumbnails_run(file_id)


@manager.command
def celery_worker():
    celery_args = ['celery', 'worker', '-n', 'worker', '-C', '--autoscale=10,1', '--without-gossip']
    with app.app_context():
        return celery(celery_args)


if __name__ == "__main__":
    manager.run()
