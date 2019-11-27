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
from uuid import uuid4
from flask import current_app, abort, render_template, flash, redirect
from flask_login import current_user
from ..models import Category
from .CategoryManagementForms import CategoryFileForm
from ..data_import.DataImportSelect import import_delayed

from .ArchiveManagementController import archive_management

from . import CategoryManagementApi


@archive_management.route('/admin/archive/<string:archive_id>/category/new', methods=['GET', 'POST'])
def admin_archive_category_new(archive_id):
    if not current_user.has_capability('admin'):
        abort(403)
    archive = Category.get_or_404(archive_id)
    form = CategoryFileForm()
    if form.validate_on_submit():
        form.category_file.data_import_worker.set_parent(archive)
        form.category_file.data_import_worker.save_base_data()
        filename = str(uuid4())
        path = os.path.join(current_app.config['TEMP_UPLOAD_DIR'], filename)
        form.category_file.data.seek(0)
        form.category_file.data.save(path)

        import_delayed(filename, archive_id)
        flash('Bestand erfolgreich hochgeladen und Importvorgang gestartet', 'success')
        return redirect('/admin/archive/%s/show' % archive.id)
    return render_template('category-new.html', archive=archive, form=form)


@archive_management.route('/admin/archive/<string:archive_id>/category/<string:category_id>/show')
def archive_category_show(archive_id, category_id):
    if not current_user.has_capability('admin'):
        abort(403)
    archive = Category.get_or_404(archive_id)
    category = Category.get_or_404(category_id)
    return render_template('category-show.html', archive=archive, category=category)


