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

from webapp.models import Category
from ...extensions import logger


def get_category(data, parent, nsmap):
    return Category.objects(parent=parent, uid=get_identifier(data, nsmap)).first()


def get_identifier(data, nsmap):
    collection_id = data.get('id')
    if not collection_id:
        collection_id = data.xpath('./ns:did/ns:unitid', namespaces=nsmap)
        if len(collection_id):
            collection_id = collection_id[0].text
        else:
            collection_id = None
    if not collection_id:
        collection_id = data.xpath('./ns:did/ns:unittitle', namespaces=nsmap)
        if len(collection_id):
            collection_id = collection_id[0].text
        else:
            collection_id = None
    if not collection_id:
        return
    return collection_id


def save_category(data, parent, nsmap, status):
    collection_id = get_identifier(data, nsmap)
    if not collection_id:
        return
    category = get_category(data, parent, nsmap)
    if not category:
        category = Category()
        category.uid = collection_id
        category.parent = parent

    category.status = status
    collection_title = data.xpath('./ns:did/ns:unittitle', namespaces=nsmap)
    collection_descr = data.xpath('./ns:scopecontent/ns:p', namespaces=nsmap)
    collection_order_id = data.xpath('./ns:did/ns:unitid', namespaces=nsmap)

    if len(collection_title) and collection_title[0].text:
        category.title = collection_title[0].text
    if len(collection_order_id) and collection_order_id[0].text:
        category.order_id = collection_order_id[0].text
    if len(collection_descr) and collection_descr[0].text:
        category.description = collection_descr[0].text.replace('<lb/>', ' ').strip()

    category.save()
    logger.info('dataimport.eadddb.category', 'category %s saved' % category.id)
    return category
