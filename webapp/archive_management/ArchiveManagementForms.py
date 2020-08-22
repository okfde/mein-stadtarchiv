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
from wtforms import StringField, SelectField, SubmitField, TextAreaField, BooleanField, DecimalField
from wtforms.validators import URL, Optional, DataRequired, Email
from ..common.form import SearchBaseForm
from ..common.countrycodes import country_codes


class ArchiveSearchForm(SearchBaseForm):
    title = StringField(
        label='Name'
    )
    sort_field = SelectField(
        label='Sortier-Feld',
        choices=[
            ('title', 'Name'),
            ('created', 'Erstellt'),
            ('modified', 'Verändert')
        ]
    )


class ArchiveForm(FlaskForm):
    title = StringField(
        label='Name'
    )
    description = TextAreaField(
        label='Beschreibung'
    )
    visible = BooleanField(
        label='Öffentlich sichtbar'
    )
    licenceName = StringField(
        label='Lizenz: Name'
    )
    licenceUrl = StringField(
        label='Lizenz URL',
        validators=[
            URL(message='Bitte eine valide URL oder gar keine eingeben.'),
            Optional()
        ]
    )
    licenceAuthorName = StringField(
        label='Autor Name'
    )
    licenceAuthorUrl = StringField(
        label='Autor URL',
        validators=[
            URL(message='Bitte eine valide URL oder gar keine eingeben.'),
            Optional()
        ]
    )
    externalUrl = StringField(
        label='Externe URL',
        validators=[
            URL(
                message='Bitte geben Sie eine URL ein'
            ),
            Optional()
        ]
    )
    email = StringField(
        label='E-Mail',
        validators=[
            Email(
                message='Bitte geben Sie eine E-Mail ein'
            ),
            Optional()
        ]
    )
    phone = StringField(
        label='Telefon'
    )
    locationSubtitle = StringField(
        label='Orts-Subtitel'
    )
    address = StringField(
        label='Adresse',
        validators=[
            DataRequired(
                message='Bitte geben Sie eine Adresse ein'
            )
        ]
    )
    postcode = StringField(
        label='Postleitzahl',
        validators=[
            DataRequired(
                message='Bitte geben Sie eine Postleitzahl ein'
            )
        ]
    )
    locality = StringField(
        label='Ort',
        validators=[
            DataRequired(
                message='Bitte geben Sie einen Ort ein'
            )
        ]
    )
    country = SelectField(
        label='Land',
        choices=country_codes,
        default='DE'
    )
    lat = DecimalField(
        label='Längengrad',
        places=6
    )
    lon = DecimalField(
        label='Breitengrad',
        places=6
    )
    submit = SubmitField(
        label='speichern'
    )


class ArchiveDeleteForm(FlaskForm):
    abort = SubmitField('abbrechen')
    submit = SubmitField('löschen')
