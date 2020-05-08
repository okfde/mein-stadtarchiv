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

from flask import Blueprint, render_template, request, flash, redirect, abort
from flask_login import login_required, current_user
from ..extensions import logger
from ..models import Comment
from .AdminForms import CommentSearchForm

admin = Blueprint('admin', __name__, template_folder='templates')

from . import AdminApi
from . import AdminInstallController


@admin.route('/admin')
def admin_main():
    if not current_user.has_capability('admin'):
        abort(403)
    return render_template('admin.html')


@admin.route('/admin/comments', methods=['GET', 'POST'])
def admin_comments():
    if not current_user.has_capability('admin'):
        abort(403)
    form = CommentSearchForm()
    return render_template('admin-comments.html', form=form)


@admin.route('/admin/comment/<string:comment_id>/set-status')
def admin_comment(comment_id):
    if not current_user.has_capability('admin'):
        abort(403)
    status = request.args.get('status', 1, type=int)
    if status < -1 or status > 2:
        abort(403)
    comment = Comment.get(comment_id)
    if not comment:
        flash('Kommentar nicht gefunden', 'danger')
        return redirect('/admin/comments')
    comment.status = status
    comment.save()
    logger.info('comment', 'comment %s changes status to %s' % (comment.id, comment.status))
    if status == 1:
        flash('Kommentar erfolgreich freigeschaltet', 'success')
    if status == 2:
        flash('Kommentar erfolgreich gesichtet', 'success')
    else:
        flash('Kommentar erfolgreich gelöscht', 'success')
    return redirect('/admin/comments')
