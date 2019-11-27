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
from flask import current_app
from ..extensions import celery
from ..models import Category
from .ead_ddb.DataImportEadDdbWorker import DataImportEadDdbWorker
from .faust_stadtarchiv.DataImportFaustStadtarchivWorker import DataImportFaustStadtarchivWorker
from ..data_worker.DataWorkerHelper import worker


workers = [
    DataImportFaustStadtarchivWorker,
    DataImportEadDdbWorker
]


def select_standard(*args, **kwargs):
    for worker in workers:
        check = worker(*args, **kwargs)
        if check.is_valid():
            return check


#@celery.worker
def import_delayed(filename, archive_id):
    archive = Category.get(archive_id)
    if not archive:
        return
    path = os.path.join(current_app.config['TEMP_UPLOAD_DIR'], filename)
    data_import_worker = select_standard(path=path, parent=archive)
    data_import_worker.save_data()
    worker()
