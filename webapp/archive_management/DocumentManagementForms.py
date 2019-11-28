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
from wtforms import SubmitField, FileField, HiddenField, StringField
from wtforms.validators import DataRequired
from ..common.form_validator import ValidateMimeType


def filter_float(value):
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


class DocumentForm(FlaskForm):
    address = StringField(
        label='Adresse'
    )
    postcode = StringField(
        label='Postleitzahl'
    )
    locality = StringField(
       label='Ort'
    )
    lat = HiddenField(
        filters=[
            filter_float
        ]
    )
    lon = HiddenField(
        filters=[
            filter_float
        ]
    )
    submit = SubmitField(
        label='speichern'
    )


class DocumentFileForm(FlaskForm):
    name = StringField(
        label='Name'
    )

    submit = SubmitField(
        label='speichern'
    )

class DocumentNewFileForm(DocumentFileForm):
    image_file = FileField(
        label='Bild- oder PDF-Datei',
        validators=[
            DataRequired(
                message='Bitte stellen Sie eine Bild- oder PDF-Datei bereit'
            ),
            ValidateMimeType(
                mimetypes=['image/tiff', 'image/jpeg', 'image/png', 'image/bmp', 'application/pdf'],
                message='Bitte stellen Sie eine Bild-Datei (JPG, TIF, PNG, BMP) oder eine PDF bereit'
            )
        ]
    )

class DocumentFileDeleteForm(FlaskForm):
    abort = SubmitField(
        label='abbrechen'
    )
    submit = SubmitField(
        label='löschen'
    )
