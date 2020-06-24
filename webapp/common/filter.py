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
import pytz
import json
from decimal import Decimal
from datetime import datetime, date
from urllib.parse import quote_plus
from flask import current_app


def register_global_filters(app):
    class FullJSONEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, datetime) or isinstance(obj, date):
                return obj.isoformat()
            elif isinstance(obj, Decimal):
                return str(obj)
            return obj.__dict__

    app.json_encoder = FullJSONEncoder

    @app.template_filter('datetime')
    def template_datetime(value, format='medium'):
        if not value:
            return ''
        if not value.tzinfo:
            value = pytz.UTC.localize(value)
        if value.tzname() == 'UTC':
            value = value.astimezone(pytz.timezone('Europe/Berlin'))
        if format == 'full':
            strftime_format = "%A, der %d.%m.%y um %H:%M Uhr"
        elif format == 'medium':
            strftime_format = "%d.%m.%y, %H:%M"
        elif format == 'short':
            strftime_format = "%d.%m, %H:%M"
        elif format == 'fulldate':
            strftime_format = "%d.%m.%Y"
        elif format == 'daymonth':
            strftime_format = "%d%m"
        elif format == 'year':
            strftime_format = "%Y"
        value = value.strftime(strftime_format)
        return value

    @app.template_filter('urlencode')
    def urlencode(data):
        return (quote_plus(data))

    @app.template_filter('ceil')
    def template_price(value):
        return math.ceil(value)

    @app.template_filter('filesize')
    def template_filesize(value):
        if not value:
            return ''
        if value < 1000:
            return '%s Byte' % value
        elif value < 1000000:
            return "%s kB" % round(value / 1000)
        else:
            return "%s MB" % round(value / 1000000)

    @app.context_processor
    def static_content():
        filename = 'webpack-assets.%sjson' % ('min.' if current_app.config['MODE'] == 'PRODUCTION' else '')
        path = os.path.join(current_app.config['PROJECT_ROOT'], os.pardir, 'static', filename)
        with open(path) as json_file:
            data = json.load(json_file)
            return dict(static_content=data)
