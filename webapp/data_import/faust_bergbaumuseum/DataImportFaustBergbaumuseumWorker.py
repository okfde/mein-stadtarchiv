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

from lxml import etree
from ..DataImportWorker import DataImportWorker
from .FaustBergbaumuseumCategory import save_category, get_category
from .FaustBergbaumuseumDocument import save_document


class DataImportFaustBergbaumuseumWorker(DataImportWorker):
    identifier = 'faust-bergbaumuseum'

    def is_valid(self):
        if self.xml is None:
            return False
        if self.xml.tag != 'montandok':
            return False

        if not len(self.xml):
            return False
        if self.xml[0].tag != 'Objekt':
            return False
        return True

    def save_base_data(self):
        categories = []
        datasets = self.xml.findall('./Objekt')
        for dataset in datasets:
            primary = self.get_field(dataset, './/Klassifikation_Tektonik')
            if not primary:
                continue
            if primary in categories:
                continue
            categories.append(primary)
        for primary_raw in categories:
            save_category(self._parent, primary_raw)

    def save_data(self):
        categories = {}
        datasets = self.xml.findall('./Objekt')
        for dataset in datasets:
            primary_title = self.get_field(dataset, './/Klassifikation_Tektonik')
            if not primary_title:
                continue
            categories[primary_title] = get_category(self._parent, primary_title)
        for dataset in datasets:
            primary_title = self.get_field(dataset, './/Klassifikation_Tektonik')
            save_document(categories[primary_title], dataset)


    def get_field(self, data, path):
        result = data.find(path)
        if result is None:
            return
        if not result.text:
            return
        return result.text

