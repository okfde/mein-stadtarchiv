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
from flask_script import Manager, Shell, Server
from flask import current_app
from webapp import launch
from webapp.extensions import db, celery
import webapp.models as Models
from webapp.config import DefaultConfig
from webapp.data_worker.DataWorkerHelper import worker as data_worker_run, upsert_login as upsert_login_run
from webapp.admin.AdminHelper import set_auth as set_auth_run, missing_media as missing_media_run, \
    file_document_reverse as file_document_reverse_run, reset_elasticsearch_last_run as reset_elasticsearch_last_run_run

app = launch()

manager = Manager(app)


@manager.shell
def make_shell_context():
    return dict(app=current_app, db=db, models=Models)


@manager.command
def data_worker():
    data_worker_run()

@manager.command
def upsert_login(email, password):
    upsert_login_run(email, password)

@manager.command
def data_worker():
    data_worker_run()

@manager.command
def set_auth(id, auth):
    set_auth_run(id, auth)

@manager.command
def missing_media():
    missing_media_run()

@manager.command
def file_document_reverse():
    file_document_reverse_run()

@manager.command
def reset_elasticsearch_last_run():
    reset_elasticsearch_last_run_run()

@manager.command
def celery_worker():
    celery_args = ['celery', 'worker', '-n', 'worker', '-C', '--autoscale=10,1', '--without-gossip']
    with app.app_context():
        return celery(celery_args)


if __name__ == "__main__":
    manager.run()
