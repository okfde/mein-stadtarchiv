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

from flask import Blueprint, render_template, flash, redirect, session, abort
from flask_login import current_user, logout_user
from .UserForms import LoginForm, UserSearchForm, UserForm, UserDeleteForm
from ..models import User
from ..extensions import logger

user_management = Blueprint('user', __name__, template_folder='templates')

from . import UserApi


@user_management.route('/login', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        return redirect('/admin')
    form = LoginForm()
    if form.validate_on_submit():
        user, authenticated = User.authenticate(form.email.data, form.password.data, form.remember_me.data)
        if authenticated:
            logger.info('user', 'user %s logged in' % user.id)
            flash('Login erfolgreich.', 'success')
            return redirect('/admin')
        flash('Zugangsdaten nicht korrekt', 'danger')
    return render_template('login.html', form=form)


@user_management.route('/logout')
def logout():
    session.pop('login', None)
    logout_user()
    flash('Sie haben sich erfolgreich ausgeloggt.', 'success')
    return redirect('/')


@user_management.route('/admin/users')
def user_main():
    if not current_user.has_capability('admin'):
        abort(403)
    form = UserSearchForm()
    return render_template('users.html', form=form)


@user_management.route('/admin/user/<string:user_id>/show')
def user_show(user_id):
    if not current_user.has_capability('admin'):
        abort(403)
    user = User.get_or_404(user_id)
    return render_template(
        'user-show.html',
        user=user
    )


@user_management.route('/admin/user/new', methods=['GET', 'POST'])
def user_new():
    if not current_user.has_capability('admin'):
        abort(403)
    form = UserForm()

    if form.validate_on_submit():
        user = User()
        form.populate_obj(user)
        user.save()
        flash('User %s gespeichert.' % user.email, 'success')
        return redirect('/admin/users')
    return render_template('user-new.html', form=form)


@user_management.route('/admin/user/<string:user_id>/edit', methods=['GET', 'POST'])
def user_edit(user_id):
    if not current_user.has_capability('admin'):
        abort(403)
    user = User.get_or_404(user_id)
    form = UserForm(obj=user)

    if form.validate_on_submit():
        form.populate_obj(user)
        user.save()
        flash('User %s gespeichert.' % user.email, 'success')
        return redirect('/admin/users')
    return render_template('user-edit.html', form=form, user=user)


@user_management.route('/admin/user/<string:user_id>/delete', methods=['GET', 'POST'])
def user_delete(user_id):
    if not current_user.has_capability('admin'):
        abort(403)
    user = User.get_or_404(user_id)
    form = UserDeleteForm()

    if form.validate_on_submit():
        if form.abort.data:
            return redirect('/admin/users')
        user.delete()
        flash('User %s gelöscht.' % user.email, 'success')
        return redirect('/admin/users')
    return render_template('user-delete.html', form=form, user=user)
