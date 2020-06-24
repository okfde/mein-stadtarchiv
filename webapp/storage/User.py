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

from passlib.hash import bcrypt
from werkzeug.security import check_password_hash
from mongoengine import Document, StringField, ListField, ReferenceField
from flask_login import login_user, UserMixin, AnonymousUserMixin
from .Base import Base


class User(Base, UserMixin):
    active = True
    email = StringField()
    _password = StringField(db_field='password')
    capabilities = ListField(StringField())
    firstname = StringField()
    lastname = StringField()
    organisation = StringField()
    subsites = ListField(ReferenceField('Subsite', deref_document=False))

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def has_capability(self, *capabilities):
        if not self.capabilities:
            return False
        if 'admin' in self.capabilities:
            return True
        check_capabilities = self.capabilities
        for capability in capabilities:
            if capability in check_capabilities:
                return True
        return False

    @staticmethod
    def validate_login(password_hash, password):
        return check_password_hash(password_hash, password)

    # password should be encrypted
    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        self._password = bcrypt.hash(password)

    def check_password(self, password):
        """
        Ueberprueft das Passwort des Nutzers
        """
        if self.password is None:
            return False
        return bcrypt.verify(password, self.password)

    @classmethod
    def authenticate(self, email, password, remember):
        """
        Authentifiziert einen Nutzer
        """
        user = User.objects(email=email).first()

        if user:
            authenticated = user.check_password(password) and user.active
            if authenticated:
                login_user(user, remember=bool(remember))
        else:
            authenticated = False
        return user, authenticated

    def __init__(self, *args, **kwargs):
        super(Document, self).__init__(*args, **kwargs)

    def __repr__(self):
        return '<User %r>' % self.email


class AnonymousUser(AnonymousUserMixin):
    id = None
    type = 'guest'

    def has_capability(self, *capabilities):
        return False
