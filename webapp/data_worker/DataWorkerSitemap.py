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
import math
import subprocess
from flask import (Flask, Blueprint, render_template, current_app, request, flash, url_for, redirect, session, abort,
                   jsonify, send_from_directory)
from ..models import Document, Option
from ..extensions import logger


class DataWorkerSitemap():
    def __init__(self):
        pass

    def run(self, *args):
        logger.info('worker.sitemap', 'create sitemap')
        lock = Option.objects(key='sitemap_lock').first()
        if lock:
            if lock.value == '1':
                return
        else:
            lock = Option()
            lock.key = 'sitemap_lock'
        lock.value = '1'
        lock.save()

        self.sitemaps = []
        self.tidy_up()
        self.generate_document_sitemap()
        self.generate_meta_sitemap()

        lock = Option.objects(key='sitemap_lock').first()
        lock.value = '0'
        lock.save()
        # Create meta-sitemap

    def tidy_up(self):
        for sitemap_file in os.listdir(current_app.config['SITEMAP_DIR']):
            if sitemap_file[0] != '.':
                file_path = os.path.join(current_app.config['SITEMAP_DIR'], sitemap_file)
                os.unlink(file_path)

    def generate_document_sitemap(self):
        document_count = Document.objects.count()
        for sitemap_number in range(0, int(math.ceil(document_count / 500000))):
            documents = Document.objects()[sitemap_number * 50000:((sitemap_number + 1) * 50000) - 1]
            sitemap_path = os.path.join(current_app.config['SITEMAP_DIR'], 'documents-%s.xml' % sitemap_number)
            with open(sitemap_path, 'w') as f:
                f.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
                f.write("<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">\n")
                for document in documents.all():
                    f.write("  <url><loc>%s/document/%s</loc><lastmod>%s</lastmod></url>\n" % (current_app.config['PROJECT_URL'], document.id, document.modified.strftime('%Y-%m-%d')))
                f.write("</urlset>\n")
            subprocess.call([current_app.config['GZIP_PATH'], sitemap_path])
            self.sitemaps.append('documents-%s.xml' % sitemap_number)
            sitemap_number += 1

    def generate_meta_sitemap(self):
        meta_sitemap_path = os.path.join(current_app.config['SITEMAP_DIR'], 'sitemap.xml')
        with open(meta_sitemap_path, 'w') as f:
            f.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
            f.write("<sitemapindex xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">\n")
            for sitemap_name in self.sitemaps:
                f.write("  <sitemap><loc>%s/static/sitemap/%s.gz</loc></sitemap>\n" % (current_app.config['PROJECT_URL'], sitemap_name))
            f.write("</sitemapindex>\n")
