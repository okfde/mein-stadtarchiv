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

import datetime
from flask import (Flask, Blueprint, render_template, current_app, request, flash, url_for, redirect, session, abort,
                   jsonify, send_from_directory)
from flask_login import login_required, login_user, current_user, logout_user, confirm_login, login_fresh
from ..extensions import db
from ..models import Comment

admin = Blueprint('admin', __name__, template_folder='templates')


@admin.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_main():
    comments = Comment.objects(status__gt = -1).order_by('-created')[0:5].all()
    return render_template('admin.html', comments=comments)

@admin.route('/admin/comments', methods=['GET', 'POST'])
@login_required
def admin_comments():
    page = request.args.get('page', 1, type=int)
    count = Comment.objects(status__gt = -1).count()
    comments = Comment.objects(status__gt = -1).order_by('-created')[(page - 1) * 10:(page - 1) * 10 + 10].all()
    return render_template('admin-comments.html', comments=comments, count=count, page=page)

@admin.route('/admin/comment')
@login_required
def admin_comment():
    page = request.args.get('page', 1, type=int)
    comment_id = request.args.get('id', 1)
    status = request.args.get('status', 1, type=int)
    if status < -1 or status > 1:
        abort(403)
    comment = Comment.objects(id=comment_id).first()
    if not comment:
        flash('Kommentar nicht gefunden', 'danger')
        return redirect('/admin/comments')
    comment.status = status
    comment.save()
    if status == 1:
        flash('Kommentar erfolgreich freigeschaltet', 'success')
    else:
        flash('Kommentar erfolgreich gelöscht', 'success')
    return redirect('/admin/comments?page=%s' % page)