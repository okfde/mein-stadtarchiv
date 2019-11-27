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
from .FaustStadtarchivCategory import save_category, get_category
from .FaustStadtarchivDocument import save_document


class DataImportFaustStadtarchivWorker(DataImportWorker):
    identifier = 'faust-stadtarchiv'

    def is_valid(self):
        if self.xml is None:
            return False
        if self.xml.tag != 'Stadtarchiv':
            return False

        if not len(self.xml):
            return False
        if self.xml[0].tag != 'Findbuch':
            return False
        return True

    def save_base_data(self):
        categories = {}
        datasets = self.xml.findall('./Findbuch')
        for dataset in datasets:
            primary = self.get_field(dataset, './/Bestand')
            if not primary:
                continue
            if primary not in categories.keys():
                categories[primary] = []
            secondary = self.get_field(dataset, './/Klassifikation')
            if not secondary:
                continue
            if secondary in categories[primary]:
                continue
            categories[primary].append(secondary)
        for primary_raw, secondaries in categories.items():
            primary = save_category(self._parent, primary_raw)
            for secondary in secondaries:
                save_category(primary, secondary)

    def save_data(self):
        categories = {}
        datasets = self.xml.findall('./Findbuch')
        for dataset in datasets:
            primary_title = self.get_field(dataset, './/Bestand')
            if not primary_title:
                continue
            if primary_title not in categories.keys():
                categories[primary_title] = {
                    'parent': get_category(self._parent, primary_title),
                    'children': {}
                }
            secondary = self.get_field(dataset, './/Klassifikation')
            if not secondary:
                continue
            if secondary in categories[primary_title]['children'].keys():
                continue
            categories[primary_title]['children'][secondary] = get_category(categories[primary_title]['parent'], secondary)

        for dataset in datasets:
            save_document(categories, dataset)


    @property
    def data(self):
        if not self._data:
            self.file.seek(0)
            self._data = self.file.read()
            self._data = self._data.decode(encoding='ISO-8859-1')
            self._data = self._data.replace('<?xml version="1.0" encoding="ISO-8859-1"?>', '')
        return self._data

    @property
    def xml(self):
        if self._xml is None:
            try:
                parser = etree.XMLParser(encoding='ISO-8859-1')
                self._xml = etree.fromstring(self.data, parser=parser)
                self.nsmap = self._xml.nsmap
                if not self.nsmap:
                    return self._xml
                self.nsmap['ns'] = self.nsmap[None]
                del self.nsmap[None]
            except etree.XMLSyntaxError:
                return
            except ValueError:
                return
        return self._xml

    def get_field(self, data, path):
        result = data.find(path)
        if result is None:
            return
        if not result.text:
            return
        return result.text

