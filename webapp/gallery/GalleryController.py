from flask import Blueprint, current_app, render_template

from webapp.common.elastic_request import ElasticRequest
from webapp.common.helpers import get_first_thumbnail_url

gallery = Blueprint('gallery', __name__, template_folder='templates')


@gallery.route('/gallery', methods=['GET', 'POST'])
def gallery_main():
    elastic_request = ElasticRequest(
        current_app.config['ELASTICSEARCH_DOCUMENT_INDEX'] + '-latest',
        'document'
    )

    elastic_request.set_range_limit('file_count', "gte", 1)
    elastic_request.set_limit(100)
    elastic_request.query()

    elastic_results = elastic_request.get_results()
    result = []

    for document in elastic_results:
        for file in document['files']:
            if file.get('mimeType') not in current_app.config['IMAGE_MIMETYPES']:
                continue
            result.append({
                'src': get_first_thumbnail_url(document.get('id'), file.get('id'), 600),
                'alt': file.get('name'),
                'document': '/document/' + document.get('id'),
            })

    return render_template('gallery.html', files=result)
