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

from flask_wtf import FlaskForm
from wtforms import validators
from wtforms import StringField, BooleanField, SelectMultipleField, PasswordField, SubmitField, SelectField
from ..common.form import SearchBaseForm
from ..common.form_field import SubsiteMultibleField


class UserSearchForm(SearchBaseForm):
    name = StringField(
        label='Name'
    )
    sort_field = SelectField(
        label='Sortier-Feld',
        choices=[
            ('name', 'Name'),
            ('created', 'Erstellt'),
            ('modified', 'Verändert')
        ]
    )


class LoginForm(FlaskForm):
    email = StringField(
        'E-Mail',
        [
            validators.Email(
                message='Bitte geben Sie eine E-Mail an'
            )
        ]
    )
    password = PasswordField(
        'Passwort',
        [
            validators.DataRequired(
                message='Bitte geben Sie ein Passwort ein.'
            )
        ]
    )
    remember_me = BooleanField(
        'Eingeloggt bleiben',
        default=False
    )
    submit = SubmitField('login')


class UserForm(FlaskForm):
    email = StringField(
        'E-Mail',
        [
            validators.Email(
                message='Bitte geben Sie eine E-Mail an'
            )
        ]
    )
    firstname = StringField(
        label='Vorname'
    )
    lastname = StringField(
        label='Nachname'
    )
    organisation = StringField(
        label='Organisation'
    )
    subsites = SubsiteMultibleField(
        label='Zugriff auf folgende Subsites'
    )
    capabilities = SelectMultipleField(
        label='Rechte',
        choices=[
            ('admin', 'Globaler Administrator'),
            ('local', 'Lokaler Administrator'),
            ('archive-view', 'Archive ansehen'),
            ('archive-manage', 'Archive bearbeiten'),
            ('comment-view', 'Kommentare ansehen'),
            ('comment-manage', 'Kommentare bearbeiten'),
            ('subsite-manage-own', 'Eigene Unterseite bearbeiten')
        ],
        description='Ein globaler Administrator darf alles. Ein lokaler Administrator darf alles in den angegebenen Subsites. User, die kein Administrator sind, dürfen nur die Einzelrechte in den angegeben Subsites.'
    )
    submit = SubmitField('speichern')


class UserDeleteForm(FlaskForm):
    abort = SubmitField('abbrechen')
    submit = SubmitField('löschen')
