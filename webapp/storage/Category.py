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

from bson import DBRef, ObjectId
from mongoengine import BooleanField, ReferenceField, StringField, DecimalField
from .Base import Base
from .Subsite import Subsite


class Category(Base):
    uid = StringField(index=True)
    orderId = StringField()
    title = StringField()
    slug = StringField()
    auth = StringField()
    visible = BooleanField()
    status = StringField()
    uploadedFile = StringField()
    parent = ReferenceField('Category', deref_document=False)

    description = StringField(fulltext=True)
    externalUrl = StringField()
    email = StringField()
    phone = StringField()
    address = StringField()
    postcode = StringField()
    locality = StringField()
    country = StringField()

    lat = DecimalField(precision=6)
    lon = DecimalField(precision=6)

    licenceName = StringField()
    licenceUrl = StringField()
    licenceAuthorName = StringField()
    licenceAuthorUrl = StringField()

    def get_dict_with_children(self, recursive=False, level=1):
        result = self.to_dict()
        if not recursive and level > 1:
            return result
        result['children'] = []
        for category in Category.objects(parent=self.id).order_by('+title').all():
            result['children'].append(category.get_dict_with_children(recursive, level + 1))
        return result

    def get_children_list(self):
        result = []
        for category in Category.objects(parent=self.id).order_by('+title').all():
            result.append(category)
            result += category.get_children_list()
        return result

    def __repr__(self):
        return '<Category %r>' % self.title

    @property
    def subsite(self):
        return Subsite.objects(categories__contains=self).first()
