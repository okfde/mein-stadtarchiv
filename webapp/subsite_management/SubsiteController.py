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


from flask import Blueprint, render_template, abort, redirect, flash
from flask_login import current_user
from ..storage import Subsite
from .SubsiteForms import SubsiteForm, SubsiteSearchForm, SubsiteDeleteForm

subsite_management = Blueprint('subsite_management', __name__, template_folder='templates')

from . import SubsiteApi


@subsite_management.route('/admin/subsites')
def subsite_main():
    if not current_user.has_capability('admin'):
        abort(403)
    form = SubsiteSearchForm()
    return render_template('subsites.html', form=form)


@subsite_management.route('/admin/subsite/<string:subsite_id>/show')
def subsite_show(subsite_id):
    if not current_user.has_capability('admin'):
        abort(403)
    subsite = Subsite.get_or_404(subsite_id)
    return render_template(
        'subsite-show.html',
        subsite=subsite,
        children=subsite.get_dict_with_children(True).get('children')
    )


@subsite_management.route('/admin/subsite/new', methods=['GET', 'POST'])
def subsite_new():
    if not current_user.has_capability('admin'):
        abort(403)
    form = SubsiteForm()

    if form.validate_on_submit():
        subsite = Subsite()
        form.populate_obj(subsite)
        subsite.save()
        flash('Subsite %s gespeichert.' % subsite.title, 'success')
        return redirect('/admin/subsites')
    return render_template('subsite-new.html', form=form)


@subsite_management.route('/admin/subsite/<string:subsite_id>/edit', methods=['GET', 'POST'])
def subsite_edit(subsite_id):
    if not current_user.has_capability('admin'):
        abort(403)
    subsite = Subsite.get_or_404(subsite_id)
    form = SubsiteForm(obj=subsite)

    if form.validate_on_submit():
        form.populate_obj(subsite)
        subsite.save()
        flash('Subsite %s gespeichert.' % subsite.title, 'success')
        return redirect('/admin/subsites')
    return render_template('subsite-edit.html', form=form, subsite=subsite)


@subsite_management.route('/admin/subsite/<string:subsite_id>/delete', methods=['GET', 'POST'])
def subsite_delete(subsite_id):
    if not current_user.has_capability('admin'):
        abort(403)
    subsite = Subsite.get_or_404(subsite_id)
    form = SubsiteDeleteForm()

    if form.validate_on_submit():
        if form.abort.data:
            return redirect('/admin/subsites')
        subsite.delete()
        flash('Subsite %s gelöscht.' % subsite.title, 'success')
        return redirect('/admin/subsites')
    return render_template('subsite-delete.html', form=form, subsite=subsite)
