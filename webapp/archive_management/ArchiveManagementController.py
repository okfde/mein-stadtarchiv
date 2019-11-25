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


from flask import Blueprint, current_app, render_template, abort, redirect, request, flash
from flask_login import current_user
from ..storage import Category
from .ArchiveManagementForms import ArchiveForm, ArchiveSearchForm, ArchiveDeleteForm

archive_management = Blueprint('archive_management', __name__, template_folder='templates')

from . import ArchiveManagementApi
from . import CategoryManagementController


@archive_management.route('/admin/archives')
def archive_main():
    if not current_user.has_capability('admin'):
        abort(403)
    form = ArchiveSearchForm()
    return render_template('archives.html', form=form)


@archive_management.route('/admin/archive/<string:archive_id>/show')
def archive_show(archive_id):
    if not current_user.has_capability('admin'):
        abort(403)
    archive = Category.get_or_404(archive_id)
    return render_template('archive-show.html', archive=archive, children=archive.get_dict_with_children().get('children'))


@archive_management.route('/admin/archive/new', methods=['GET', 'POST'])
def archive_new():
    if not current_user.has_capability('admin'):
        abort(403)
    form = ArchiveForm()

    if form.validate_on_submit():
        category = Category()
        form.populate_obj(category)
        category.save()
        flash('Archiv %s gespeichert.' % category.title, 'success')
        return redirect('/admin/archives')
    return render_template('archive-new.html', form=form)


@archive_management.route('/admin/archive/<string:archive_id>/edit', methods=['GET', 'POST'])
def archive_edit(archive_id):
    if not current_user.has_capability('admin'):
        abort(403)
    category = Category.get_or_404(archive_id)
    form = ArchiveForm(obj=category)

    if form.validate_on_submit():
        form.populate_obj(category)
        category.save()
        flash('Archiv %s gespeichert.' % category.title, 'success')
        return redirect('/admin/archives')
    return render_template('archive-edit.html', form=form, archive=category)


@archive_management.route('/admin/archive/<string:archive_id>/delete', methods=['GET', 'POST'])
def archive_delete(archive_id):
    if not current_user.has_capability('admin'):
        abort(403)
    category = Category.get_or_404(archive_id)
    form = ArchiveDeleteForm()

    if form.validate_on_submit():
        if form.abort.data:
            return redirect('/admin/archives')
        category.delete()
        flash('Archiv %s gelöscht.' % category.title, 'success')
        return redirect('/admin/archives')
    return render_template('archive-delete.html', form=form, archive=category)
