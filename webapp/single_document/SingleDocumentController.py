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
from ..common.response import json_response
from ..models import Document, Comment
from .SingleDocumentForms import CommentForm

single_document = Blueprint('single_document', __name__, template_folder='templates')


@single_document.route('/document/<id>', methods=['GET', 'POST'])
def single_document_main(id):
    if len(id) != 24:
        abort(404)
    document = Document.objects(id=id).first()
    if not document:
        abort(404)

    categories = []
    for i in range(0, len(document.category)):
        category = document.category[i]
        categories.append([])
        while category:
            categories[i].insert(0, category)
            category = category.parent
    document.categories = categories

    comments = Comment.objects(document=document, status__gte=1).order_by('-created').all()

    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment()
        if 'X-Forwarded-For' in request.headers:
            comment.ip = request.headers['X-Forwarded-For']
        comment.author_name = form.name.data
        comment.author_email = form.email.data
        comment.content = form.text.data
        comment.document = document.id
        comment.status = 0
        comment.created = datetime.datetime.now()
        comment.modified = datetime.datetime.now()
        comment.save()
        flash('Kommentar gespeichert und wartet auf Freischaltung.', 'success')
        return redirect('/document/%s' % document.id)
    return render_template('single_document.html', document=document, form=form, comments=comments)
