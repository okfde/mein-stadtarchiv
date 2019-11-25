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
from lxml import etree
from flask import current_app
from ..extensions import celery
from ..models import Category


class DataImportWorker:
    identifier = None
    path = None
    _file = None
    _data = None
    _xml = None
    _sub = None
    _parent = None
    nsmap = {}

    def __init__(self, path=None, file=None):
        self._file = file
        self.path = path

    def select_standard(self):
        from .ead_ddb.DataImportEadDdbWorker import DataImportEadDdbWorker
        workers = [DataImportEadDdbWorker]
        for worker in workers:
            check = worker(path=self.path, file=self.file, data=self._data, xml=self._xml)
            if check.is_valid():
                self._sub = check
                return check

    def known_standard(self):
        return self.select_standard() and True

    def is_valid(self):
        return False

    def set_parent(self, parent):
        self._parent = parent

    def save_base_data(self):
        return

    @property
    def file(self):
        if not self._file:
            self._file = open(self.path, 'rb')
        return self._file

    @property
    def data(self):
        if not self._data:
            self._data = self.file.read()
        return self._data

    @property
    def xml(self):
        if self._xml is None:
            try:
                self._xml = etree.fromstring(self.data)
                self.nsmap = self._xml.nsmap
                self.nsmap['ns'] = self.nsmap[None]
                del self.nsmap[None]
            except etree.XMLSyntaxError:
                return
        return self._xml

    def __del__(self):
        if self.path and self.file:
            self.file.close()


#@celery.worker
def import_delayed(filename, archive_id):
    archive = Category.get(archive_id)
    if not archive:
        return
    path = os.path.join(current_app.config['TEMP_UPLOAD_DIR'], filename)
    data_import_worker = DataImportWorker(path=path).select_standard()
    data_import_worker.set_parent(archive)
    data_import_worker.save_data()

