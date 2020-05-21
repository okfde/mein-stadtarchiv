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
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, FileField, SelectField
from wtforms.validators import DataRequired
from ..common.form_validator import ValidateMimeType, ValidateKnownXml, DataRequiredIfOtherEmpty, \
    DataRequiredIfOtherMimetype
from ..common.form import SearchBaseForm


class CategorySearchForm(SearchBaseForm):
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


class CategoryFileForm(FlaskForm):
    title = StringField(
        label='Name',
        validators=[
            DataRequiredIfOtherEmpty(
                'category_file',
                message='Ohne Importdatei wird ein Titel benötigt'
            ),
            DataRequiredIfOtherMimetype(
                'category_file',
                ['application/vnd.ms-excel', 'text/csv', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'],
                message='Bei Tabellen wird ein Titel benötigt'
            )
        ]
    )
    category_file = FileField(
        label='XML-Datei',
        validators=[
            DataRequired(
                message='Bitte stellen Sie eine XML-, CSV-, XLS- oder XLSX-Datei bereit'
            ),
            ValidateMimeType(
                mimetypes=[
                    'application/xml', 'text/xml', 'application/vnd.ms-excel', 'text/csv', 'text/plain',
                    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                ],
                allow_empty=True,
                message='Bitte stellen Sie eine XML-, CSV-, XLS- oder XLSX-Datei bereit'
            ),
            ValidateKnownXml(
                ignore_non_xml=True,
                message='Bitte stellen Sie eine XML-, CSV-, XLS- oder XLSX-Datei in einem bekannten Format bereit'
            )
        ]
    )
    description = TextAreaField(
        label='Beschreibung'
    )
    visible = BooleanField(
        label='Öffentlich sichtbar'
    )
    submit = SubmitField(
        label='speichern'
    )


class CategoryTableForm(FlaskForm):
    delete_file = BooleanField(
        label='Hochgeladene Tabellen-Datei vom Server löschen'
    )
    abort = SubmitField(
        label='abrechen'
    )
    submit = SubmitField(
        label='speichern'
    )


class CategoryDeleteForm(FlaskForm):
    abort = SubmitField(
        label='abrechen'
    )
    submit = SubmitField(
        label='löschen'
    )
