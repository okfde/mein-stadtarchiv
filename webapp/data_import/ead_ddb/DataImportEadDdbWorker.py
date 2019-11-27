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
from .EadDdbCategory import save_category, get_category
from .EadDdbDocument import save_document


class DataImportEadDdbWorker(DataImportWorker):
    identifier = 'ead-ddb'

    def is_valid(self):
        if self.xml is None:
            return False
        if etree.QName(self.xml.tag).namespace != 'urn:isbn:1-931666-22-9':
            return False
        if etree.QName(self.xml.tag).localname != 'ead':
            return False

        if not len(self.xml):
            return False
        if etree.QName(self.xml[0].tag).localname != 'eadheader':
            return False
        return True

    def save_base_data(self):
        collections_xml = self.xml.xpath(
            './/ns:archdesc[@level="collection"]/ns:dsc/ns:c[@level="collection"]',
            namespaces=self.nsmap
        ) or self.xml.xpath(
            './/ns:archdesc[@level="collection"]/ns:dsc/ns:c01[@level="collection"]',
            namespaces=self.nsmap
        )
        for collection_xml in collections_xml:
            category = save_category(collection_xml, self._parent, self.nsmap, 'importing')
            if not category:
                continue
            subcollections = collection_xml.xpath('.//ns:c[@level="class"]', namespaces=self.nsmap) \
                or collection_xml.xpath('.//ns:c02[@level="class"]', namespaces=self.nsmap)
            for subcollection_xml in subcollections:
                save_category(subcollection_xml, category, self.nsmap, 'ready')

    def save_data(self):
        collections_xml = self.xml.xpath(
            './/ns:archdesc[@level="collection"]/ns:dsc/ns:c[@level="collection"]',
            namespaces=self.nsmap
        ) or self.xml.xpath(
            './/ns:archdesc[@level="collection"]/ns:dsc/ns:c01[@level="collection"]',
            namespaces=self.nsmap
        )
        for collection_xml in collections_xml:
            category = get_category(collection_xml, self._parent, self.nsmap)
            if not category:
                continue
            documents = collection_xml.xpath('./ns:c[@level="file"]', namespaces=self.nsmap) \
                or collection_xml.xpath('./ns:c02[@level="file"]', namespaces=self.nsmap)
            for document in documents:
                save_document(document, category, self.nsmap)
            subcollections = collection_xml.xpath('.//ns:c[@level="class"]', namespaces=self.nsmap) \
                or collection_xml.xpath('.//ns:c02[@level="class"]', namespaces=self.nsmap)
            for subcollection_xml in subcollections:
                subcategory = get_category(subcollection_xml, category, self.nsmap)
                if not subcategory:
                    continue
                subdocuments = subcollection_xml.xpath('./ns:c[@level="file"]', namespaces=self.nsmap) \
                    or subcollection_xml.xpath('./ns:c03[@level="file"]', namespaces=self.nsmap)
                for document in subdocuments:
                    save_document(document, subcategory, self.nsmap)
            category.status = 'ready'
            category.save()

