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

from datetime import datetime
from lxml import etree
from webapp.models import Document, File
from ...extensions import logger


def get_document(uid, parent):
    return Document.objects(category=[parent], uid=uid).first()


def save_document(category, data):

    uid = get_field(data, './/Inventar-Nummer')
    document = get_document(uid, category)
    if not document:
        document = Document()
        document.category = [category]
        document.uid = uid
    extra_fields = {}
    document.title = get_field(data, './/Titel')
    document.description = get_field(data, './/Beschreibung_Inhalt/Inhalt')
    document.orderId = uid
    document.licence = get_field(data, './/Rechteerklaerung/Rechtsstatus')
    document.author = get_field(data, './/Rechteerklaerung/creditline')
    document.date_text = get_field(data, './/Entstehung/Datierung_Herstellung/Dat_Begriff')
    date_addon_text = get_field(data, './/Entstehung/Datierung_Herstellung/DatZusatz')
    if date_addon_text:
        if document.date_text:
            document.date_text += '; ' + date_addon_text
        else:
            document.date_text = date_addon_text
    date_str = get_field(data, './/Beschreibung_Inhalt/Zeitbezuege/Zeitbezug_norm')
    if date_str:
        if len(date_str) == 4:
            document.dateBegin = '%s-01-01' % date_str
            document.dateEnd = '%s-12-31' % date_str
        elif len(date_str) == 10:
            document.date = datetime.strptime(date_str, '%Y-%m-%d').date()
        elif len(date_str) == 21:
            date_arr = date_str.split('/')
            if len(date_arr) == 2:
                document.dateBegin = datetime.strptime(date_arr[0], '%Y-%m-%d').date()
                document.dateEnd = datetime.strptime(date_arr[1], '%Y-%m-%d').date()
    for key in ['Sachgebiet', 'Objektname', 'Objektklasse', 'Sachgebiet', 'Material', 'Beschreibung_Inhalt/Objektgeschichte']:
        item = get_field(data, './/%s' % key)
        if item:
            if '/' in key:
                extra_fields[key.split('/')[-1]] = item
            else:
                extra_fields[key] = item
    document.extraFields = extra_fields
    # save document
    document.save()
    logger.info('dataimport.eadddb.document', 'document %s saved' % document.id)
    for file_raw in data.xpath('.//Image'):
        if not file_raw.get('Abbildung'):
            continue
        file = File.objects(externalId=file_raw.get('Abbildung'), document=document).first()
        if file:
            continue
        file = File()
        file.document = document
        file.externalId = file_raw.get('Abbildung')
        file.fileName = file_raw.get('Abbildung')
        file.binaryExists = False
        file.save()
    return document


def get_field(data, path):
    result = data.find(path)
    if result is None:
        return
    if not result.text:
        return
    return result.text
