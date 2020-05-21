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
import re
import magic
from uuid import uuid4
from flask import current_app, abort, render_template, flash, redirect
from flask_login import current_user
from ..models import Category
from ..common.response import json_response
from .CategoryManagementForms import CategoryFileForm, CategoryTableForm, CategoryDeleteForm
from ..data_import.DataImportSelect import import_delayed
from ..data_import.DataImportTable import DataImportTable

from .ArchiveManagementController import archive_management

from . import CategoryManagementApi


table_deref = {
    'application/vnd.ms-excel': 'xls',
    'text/csv': 'csv',
    'text/plain': 'csv',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx'
}


@archive_management.route('/admin/category/<string:category_id>/show')
def archive_category_show(category_id):
    if not current_user.has_capability('admin'):
        abort(403)
    category = Category.get_or_404(category_id)
    return render_template('category-show.html', category=category)


@archive_management.route('/admin/archive/<string:archive_id>/category/new', methods=['GET', 'POST'])
def admin_archive_category_new(archive_id):
    if not current_user.has_capability('admin'):
        abort(403)
    archive = Category.get_or_404(archive_id)
    form = CategoryFileForm()
    if form.validate_on_submit():
        if not form.category_file.data:
            flash('Bestand erfolgreich gespeichert', 'success')
            return redirect('/admin/archive/%s/show' % archive.id)
        filename = str(uuid4())
        form.category_file.data.seek(0)
        path = os.path.join(current_app.config['TEMP_UPLOAD_DIR'], filename)
        form.category_file.data.save(path)
        mimetype = magic.from_file(path, mime=True)
        if mimetype in table_deref.keys():
            flash('Bestand erfolgreich hochgeladen. Zuordnung erforderlich.', 'success')
            filename += '.' + table_deref[mimetype]
        path = os.path.join(current_app.config['TEMP_UPLOAD_DIR'], filename)
        form.category_file.data.seek(0)
        form.category_file.data.save(path)
        if mimetype in table_deref.keys():
            category = Category()
            form.populate_obj(category)
            category.parent = archive
            category.uploadedFile = filename
            category.save()
            return redirect('/admin/category/%s/table/%s' % (
                category.id,
                filename
            ))
        form.category_file.data_import_worker.set_parent(archive)
        form.category_file.data_import_worker.save_base_data()

        import_delayed.delay(filename, archive_id)
        flash('Bestand erfolgreich hochgeladen und Importvorgang gestartet', 'success')
        return redirect('/admin/archive/%s/show' % archive.id)
    return render_template('category-new.html', archive=archive, form=form)


@archive_management.route('/admin/category/<string:category_id>/table/<string:filename>', methods=['GET', 'POST'])
def admin_archive_category_table(category_id, filename):
    if not current_user.has_capability('admin'):
        abort(403)
    category = Category.get_or_404(category_id)
    check_uuid_filename(filename)
    form = CategoryTableForm()
    if form.validate_on_submit():
        if form.abort.data:
            if form.delete_file.data:
                os.remove(filename)
                category.uploadedFile = None
                category.save()
            return redirect('/admin/archive/%s/show' % category.parent.id)
        flash('Importvorgang gestartet', 'success')
        return redirect('/admin/archive/%s/show' % category.parent.id)
    return render_template('category-table.html', category=category, form=form, filename=filename)


@archive_management.route('/api/admin/category/<string:category_id>/table/<string:filename>', methods=['GET', 'POST'])
def api_admin_archive_category_table(category_id, filename):
    if not current_user.has_capability('admin'):
        abort(403)
    category = Category.get_or_404(category_id)
    check_uuid_filename(filename)
    dit = DataImportTable(filename)

    return json_response({
        'status': 0,
        'data': {
            'header': dit.header,
            'datasets': dit.preview
        }
    })


@archive_management.route('/admin/category/<string:category_id>/edit', methods=['GET', 'POST'])
def admin_archive_category_edit(category_id):
    if not current_user.has_capability('admin'):
        abort(403)
    category = Category.get_or_404(category_id)
    form = CategoryFileForm()
    if form.validate_on_submit():
        form.category_file.data_import_worker.set_parent(category.parent.id)
        form.category_file.data_import_worker.save_base_data()
        filename = str(uuid4())
        path = os.path.join(current_app.config['TEMP_UPLOAD_DIR'], filename)
        form.category_file.data.seek(0)
        form.category_file.data.save(path)

        import_delayed.delay(filename, category.parent.id)
        flash('Bestand erfolgreich hochgeladen und Importvorgang gestartet', 'success')
        return redirect('/admin/archive/%s/show' % category.parent.id)
    return render_template('category-edit.html', category=category, form=form)


@archive_management.route('/admin/category/<string:category_id>/delete', methods=['GET', 'POST'])
def admin_archive_category_delete(category_id):
    if not current_user.has_capability('admin'):
        abort(403)
    category = Category.get_or_404(category_id)
    form = CategoryDeleteForm()
    if form.validate_on_submit():
        if form.abort.data:
            return redirect('/admin/archive/%s/show' % category.parent.id)
        category.delete()
        # TODO: delete all the files (?)
        flash('Bestand erfolgreich gelöscht', 'success')
        return redirect('/admin/archive/%s/show' % category.parent.id)
    return render_template('category-delete.html', category=category, form=form)


@archive_management.route('/admin/category/<string:category_id>/upload')
def archive_category_upload_files(category_id):
    if not current_user.has_capability('admin'):
        abort(403)
    category = Category.get_or_404(category_id)

    return render_template('category-upload.html', category=category)


def check_uuid_filename(filename):
    parts = filename.split('.')
    if len(parts) != 2:
        abort(403)
    if not re.match('[0-9a-f-]{36}', filename):
        abort(403)
    if parts[1] not in table_deref.values():
        abort(403)
    path = os.path.join(current_app.config['TEMP_UPLOAD_DIR'], filename)
    if not os.path.exists(path):
        abort(404)
