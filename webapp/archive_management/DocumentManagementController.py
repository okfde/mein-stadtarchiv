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


import os
from flask import current_app, abort, render_template, flash, redirect, request, url_for
from flask_login import current_user

from webapp.common.helpers import get_first_thumbnail_url
from ..models import Document, File
from .DocumentManagementForms import DocumentForm, DocumentFileForm, DocumentFileDeleteForm, DocumentNewFileForm
from .DocumentManagementHelper import process_file

from .ArchiveManagementController import archive_management

from . import CategoryManagementApi


@archive_management.route('/admin/document/<string:document_id>/show')
def admin_document_show(document_id):
    if not current_user.has_capability('admin'):
        abort(403)
    document = Document.get_or_404(document_id)
    categories = []
    for i in range(0, len(document.category)):
        category = document.category[i]
        categories.append([])
        while category:
            categories[i].insert(0, category)
            category = category.parent
    document.categories = categories
    return render_template('document-show.html', document=document)


@archive_management.route('/admin/document/<string:document_id>/edit', methods=['GET', 'POST'])
def archive_category_edit(document_id):
    if not current_user.has_capability('admin'):
        abort(403)
    document = Document.get_or_404(document_id)
    form = DocumentForm(obj=document)
    if form.validate_on_submit():
        form.populate_obj(document)
        document.save()
        return redirect('/document/%s' % document.id)
    return render_template('document-edit.html', document=document, form=form)


@archive_management.route('/admin/document/<string:document_id>/file/new', methods=['GET', 'POST'])
def admin_document_file_new(document_id):
    if not current_user.has_capability('admin'):
        abort(403)
    document = Document.get_or_404(document_id)
    form = DocumentNewFileForm()
    if form.validate_on_submit():
        file_data = form.image_file.data
        file = File()
        if form.name.data:
            file.name = form.name.data
        file.fileName = file_data.filename
        file.mimeType = file_data.content_type
        file.document = document
        file.save()
        document.files.append(file)
        document.save()

        path = os.path.join(current_app.config['TEMP_UPLOAD_DIR'], str(file.id))
        form.image_file.data.seek(0)
        form.image_file.data.save(path)
        process_file.delay(file.id)
        return redirect(url_for('archive_management.admin_document_file_show', document_id=document_id, file_id=str(file.id)))
    return render_template('document-file-new.html', document=document, form=form,  is_edit_mode=False, post=request.url)


@archive_management.route('/admin/document/<string:document_id>/file/<string:file_id>/edit', methods=['GET', 'POST'])
def admin_document_file_edit(document_id, file_id):
    if not current_user.has_capability('admin'):
        abort(403)
    document = Document.get_or_404(document_id)
    file = File.get_or_404(file_id)
    form = DocumentFileForm(obj=file)
    if form.validate_on_submit():
        file.name = form.name.data
        file.save()
        process_file.delay(file.id)
        flash('Datei wurde erfolgreich gespeichert.', 'success')
    return render_template('document-file-edit.html', document=document, file=file, form=form, is_edit_mode=True, post=request.url)


@archive_management.route('/admin/document/<string:document_id>/file/<string:file_id>/show', methods=['GET', 'POST'])
def admin_document_file_show(document_id, file_id):
    if not current_user.has_capability('admin'):
        abort(403)
    document = Document.get_or_404(document_id)
    file = File.get_or_404(file_id)
    return render_template('document-file-show.html', document=document, file=file, url=get_first_thumbnail_url(document.id, file.id, 1200))


@archive_management.route('/admin/document/<string:document_id>/file/<string:file_id>/delete', methods=['GET', 'POST'])
def admin_document_file_delete(document_id, file_id):
    if not current_user.has_capability('admin'):
        abort(403)
    document = Document.get_or_404(document_id)
    file = File.get_or_404(file_id)
    form = DocumentFileDeleteForm()
    if form.validate_on_submit():
        if form.abort.data:
            return redirect('/admin/document/%s/show' % document.id)
        document.files = list(filter(lambda file: str(file.id) != file_id, document.files))
        document.save()
        file.delete()
        flash('Datei wurde erfolgreich gelöscht', 'success')
        return redirect('/admin/document/%s/show' % document.id)
    return render_template('document-file-delete.html', document=document, file=file, form=form)

