/*
Copyright (c) 2007, Ernesto Ruge
All rights reserved.
Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

storage = {
    current_page: 1,
    items_per_page: 10,
    first_request: true,
    browser_nav_action: false,
    form_active: false,
    random_seed: false
};

$(document).on('click', '[data-toggle="lightbox"]', function(e) {
    e.preventDefault();
    $(this).ekkoLightbox();
});

window.addEventListener('popstate', function() {
    storage.browser_nav_action = true;
    get_url();
});

$(document).ready(function () {
    if ($('#frontpage-map').length) {
        init_front_page();
    }

    if ($('#search-result').length) {
        init_search_page();
    }

    if ($('#comment-form').length) {
        if (typeof(Storage) !== "undefined") {
            var name = localStorage.getItem('comment-name');
            if (name) {
                $('#name').val(name);
            }
            var email = localStorage.getItem('comment-email');
            if (email) {
                $('#email').val(email);
            }
        }
        $('#comment-form').submit(function() {
            if (typeof(Storage) !== "undefined") {
                localStorage.setItem('comment-name', $('#name').val());
                localStorage.setItem('comment-email', $('#email').val());
            }
        });
    }

});

function init_front_page() {
    mapboxgl.accessToken = stadtarchiv_config.mapbox_token;

    storage.map = new mapboxgl.Map({
        container: 'frontpage-map',
        style: 'mapbox://styles/mapbox/bright-v9',
        center: [6.693504, 50.869415],
        zoom: 9
    });
    storage.map.addControl(new mapboxgl.NavigationControl(), 'top-right');
    storage.map.addControl(new mapboxgl.AttributionControl(), 'bottom-right');

    storage.map.on('load', function () {
        storage.map.addSource('home-source', {
            type: 'geojson',
            data: {
                type: 'FeatureCollection',
                features: [
                    {
                        'type': 'Feature',
                        'geometry': {
                            'type': 'Point',
                            'coordinates': [6.693504, 50.869415]
                        },
                        'properties': {}
                    }
                ]
            }
        });
        storage.map.addLayer({
            id: 'home-point',
            type: 'circle',
            source: 'home-source',
            paint: {
                'circle-radius': 7,
                'circle-color': '#dc281e'
            }
        }, 200);

        storage.map.addLayer({
            id: 'home-text',
            type: 'symbol',
            source: 'home-source',
            layout: {
                'text-field': 'Stadtarchiv Kerpen',
                'text-offset': [0, 1.2],
                'text-size': 16
            },
            paint: {
                'text-color': '#dc281e'
            }
        }, 200);
    });
}

function init_search_page() {
    storage.random_seed = '';
    var chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    for (var i = 0; i < 16; i++) {
        storage.random_seed += chars.charAt(Math.floor(Math.random() * chars.length));
    }

    $('#search-form').submit(function (evt) {
        evt.preventDefault();
        storage.current_page = 1;
        if ($('#fulltext').val()) {
            $('#order-by').val('_score');
        }
        search();
    });
    for (i = 0; i < stadtarchiv_config.categories.length; i++) {
        $('#category-children').append('<div class="category-child" data-id="' + stadtarchiv_config.categories[i].id + '">' + stadtarchiv_config.categories[i].title + ' (<span>0</span>)</div>');
    }
    $('.category-child, #category-parent').click(function() {
        if (!$(this).hasClass('category-inactive')) {
            select_category($(this).data('id'));
        }
    });
    $('#category-overview').on('show.bs.modal', function () {
        update_category_overview();
    });
    $('#help-required, #with-files').change(function() {
        storage.current_page = 1;
        search();
    });
    $('#order-by').change(function() {
        search();
    });
    $('#fulltext').live_search({
        url: '/api/live-search',
        form: '#search-form',
        input: '#fulltext',
        live_box: '#fulltext-live',
        submit: '#submit',
        modify_params: function (instance, params) {
            return params;
        },
        process_result_line: function (result) {
            return ('<li data-q="' + result + '">' + result + '</li>');
        },
        after_submit: function () {
        },
        result_array: function (result) {
            return (result.data);
        }
    });

    get_url();
    search();
}

function get_url() {
    cut = window.location.href.indexOf('?');
    var query_string = {};
    if (cut != -1) {
        var vars = window.location.href.substr(cut + 1).split("&");

        for (var i = 0; i < vars.length; i++) {
            var pair = vars[i].split('=');
            query_string[pair[0]] = pair[1];
        }
    }
    if (query_string.text)
        $('#fulltext').val(decodeURI(query_string.text))
    else
        $('#fulltext').val('');

    if (query_string.category)
        select_category(query_string.category);
    else
        select_category('root');

    $('#with-files').prop('checked', query_string.media == '1');
    $('#help-required').prop('checked', query_string.help == '1');

    if (query_string.year) {
        year = query_string.year.split('-');
        if (year[0])
            $('#year-start').val(year[0]);
        if (year[1])
            $('#year-end').val(year[1]);
    }

    if (query_string.page)
        storage.current_page = parseInt(query_string.page);
    else
        storage.current_page = 1;

    if (query_string.order)
        $('#order-by').val(query_string.order);
    else {
        if ($('#fulltext').val())
            $('#order-by').val('_score');
        else
            $('#order-by').val('random');
    }
    storage.form_active = true;
}

function set_url(params, category_id) {
    url = [];
    if (params.q) {
        url.push('text=' + encodeURI(params.q));
    }
    if (category_id != 'root') {
        url.push('category=' + category_id);
    }
    if (storage.current_page != 1) {
        url.push('page=' + storage.current_page);
    }
    if (params.fc) {
        url.push('media=1')
    }
    if (params.hc) {
        url.push('help=1');
    }
    if (params.ys || params.ye) {
        year_string = '';
        if (params.ys) {
            year_string += String(params.ys);
        }
        year_string += '-';
        if (params.ye) {
            year_string += String(params.ye);
        }
        url.push('year=' + year_string);
    }
    if ((params.q && params.o != '_score') || (!params.q && params.o != 'random')) {
        url.push('order=' + params.o);
    }

    url = url.join('&');
    if (url) {
        url = '?' + url;
    }
    history.pushState(null, 'Recherche | Unser Stadtarchiv', '/recherche' + url)
}

function update_category_overview() {
    category_list = '<h5 data-id="root">Alle Archive</h5>';
    category_list += get_category_list(stadtarchiv_config.categories);
    $('#category-overview .modal-body').html(category_list);
    $('#category-overview h5').click(function() {
        select_category($(this).data('id'));
        $('#category-overview').modal('toggle');
    });
}

function get_category_list(categories) {
    var html = '<ul>';
    for (var i = 0; i < categories.length; i++) {
        html += '<li><h5 data-id="' + categories[i].id + '">' + categories[i].title + ' (<span>0</span>)</h5>';
        if (categories[i].children) {
            html +=  get_category_list(categories[i].children);
        }
        html += '</li>';
    }
    html += '</ul>';
    return(html);
}

function select_category(category_id) {
    category = get_category_data(stadtarchiv_config.categories, category_id, 0);
    console.log(category);
    $('#category-current').text(category.title).data('id', category.id);
    if (category.level === 0) {
        $('#category-parent').addClass('category-inactive');
        $('#category-parent').text('Eine Ebene hoch');
    }
    else {
        $('#category-parent').removeClass('category-inactive');
        if (category.level == 1) {
            $('#category-parent').text('Alle Archive');
            $('#category-parent').data('id', 'root');
        }
        else if (category.parent) {
            $('#category-parent').data('id', category.parent.id);
            $('#category-parent').text(category.parent.title);
        }
    }
    $('#category-children').html('');
    if (category.children) {
        for (i = 0; i < category.children.length; i++) {
            $('#category-children').append('<div class="category-child" data-id="' + category.children[i].id + '">' + category.children[i].title + ' (<span>0</span>)' + ((category.children[i].description) ? ' <i class="fa fa-info-circle" aria-hidden="true"><div>' + category.children[i].description + '</div></i>' : '') + '</div>');
        }
        $('.category-child').click(function () {
            select_category($(this).data('id'));
        });
    }
    search();
}

function get_category_data(categories, category_id, level) {
    if (category_id === 'root') {
        return {
            title: 'Alle Archive',
            id: 'root',
            level: 0,
            children: stadtarchiv_config.categories
        };
    }
    else {
        for (var i = 0; i < categories.length; i++) {
            if (categories[i].id === category_id) {
                categories[i].level = level + 1;
                return (categories[i]);
            }
            if (categories[i].children) {
                child = get_category_data(categories[i].children, category_id, level + 1);
                if (child) {
                    if (!child.parent) {
                        child.parent = {
                            id: categories[i].id,
                            title: categories[i].title,
                            description: categories[i].description,
                            level: level + 1
                        };
                    }
                    return (child);
                }
            }
        }
    }
    return(false);
}

function get_children(categories) {
    var children = [];
    for (var i = 0; i < categories.length; i++) {
        children.push(categories[i].id);
        if (categories[i].children) {
            children = children.concat(get_children(categories[i].children));
        }
    }
    return(children);
}

function search() {
    if (!storage.form_active)
        return;
    category = get_category_data(stadtarchiv_config.categories, $('#category-current').data('id'), 0);
    var categories = [];
    if (category.children) {
        categories = categories.concat(get_children(category.children));
    }
    if (category.id !== 'root') {
        categories.push(category.id);
    }

    if ($('#fulltext').val()) {
        $('#order-by option[value="_score"]').removeAttr('disabled');
    } else {
        if ($('#order-by').val() == '_score' || !$('#order-by').val()) {
            $('#order-by').val('random');
        }
        $('#order-by option[value="_score"]').attr('disabled','disabled');
    }

    params = {
        skip: (storage.current_page - 1) * storage.items_per_page,
        limit: storage.items_per_page,
        q: $('#fulltext').val(),
        fq: JSON.stringify({'category': categories}),
        fc: (($('#with-files')[0].checked) ? 1 : 0),
        hc: (($('#help-required')[0].checked) ? 1 : 0),
        o: $('#order-by').val(),
        ys: parseInt($('#year-start').val()),
        ye: parseInt($('#year-end').val()),
        rs: storage.random_seed
    };
    if (storage.browser_nav_action)
        storage.browser_nav_action = false;
    else
        set_url(params, category.id);
    $.post('/api/search', params, function (data) {
        $('#search-summary .num-results').text(data.pagination.totalElements);
        $('.search-pagination').html(generate_pagination_html(data.pagination.totalElements, storage.current_page, storage.items_per_page));
        html = '';
        $.each(data.data, function (id, document) {
            html += get_search_list_item(id, document);
        });
        $('#search-result').html(html);
        $('.pagination-page').click(function () {
            if ($(this).hasClass('active')) {
                storage.current_page = parseInt($(this).attr('data-page'));
                search();
            }
        });
        update_category_list_count(data.terms.categories);
    });
}

function update_category_list_count(categories) {
    $('.category-child').each(function () {
        var count = 0;
        // parent
        if (categories[$(this).data('id')]) {
            count += categories[$(this).data('id')].count;
        }
        // children
        primary_category = get_category_data(stadtarchiv_config.categories, $(this).data('id'), 0);
        if (primary_category.children) {
            children = get_children(primary_category.children);
            for (var i = 0; i < children.length; i++) {
                if (categories[children[i]]){
                    count += categories[children[i]].count;
                }
            }
        }
        $(this).find('span').text(count);

    });
}

function get_search_list_item(id, document) {
    html = '<li><div class="search-item-left">';
    if (document.title)
        html += '<h2><a href="/document/' + document.id + '">' + document.title.replace('<', '&lt;').replace('>', '&gt;') + '</a></h2>';
    else
        html += '<h2><a href="/document/' + document.id + '">Unbekannte Darstellung</a></h2>';

    meta = [];
    if (document.date) {
        meta.push('Datum: ' + document.date.substr(8, 2) + '.' + document.date.substr(5, 2) + '.' + document.date.substr(0, 4));
    }
    if (document.date_begin && document.date_end) {
        if (document.date_begin.substr(4) == '-01-01' && document.date_end.substr(4) == '-12-31') {
            if (document.date_begin.substr(0, 4) == document.date_end.substr(0, 4)) {
                meta.push('Jahr: ' + document.date_begin.substr(0, 4));
            }
            else {
                meta.push('Jahr: ' + document.date_begin.substr(0, 4) + ' - ' + document.date_end.substr(0, 4));
            }
        }
        else {
            meta.push('Datum: ' + document.date_begin.substr(8, 2) + '.' + document.date_begin.substr(5, 2) + '.' + document.date_begin.substr(0, 4) + ' - ' + document.date_end.substr(8, 2) + '.' + document.date_end.substr(5, 2) + '.' + document.date_end.substr(0, 4));
        }
    }
    if (document.category_full) {
        meta.push('Kategorie: ' + document.category_full);
    }
    if (document.origination)
        meta.push('Herkunft: ' + document.origination.replace('<', '&lt;').replace('>', '&gt;'));
    if (meta.length)
        html += '<p class="search-item-meta">' + meta.join(' | ').replace('<', '&lt;').replace('>', '&gt;') + '</p>';

    if (document.description)
        html += '<p>' + document.description.replace('<', '&lt;').replace('>', '&gt;') + '</p>';
    html += '</div>';
    if (document.files) {
        if (document.files.length) {
            html += '<div class="search-item-image"><a href="/document/' + document.id + '"><img src="' + stadtarchiv_config.media_url + '/thumbnails/' + document.id + '/' + document.files[0].id + '/150/1.jpg"></a></div>';
        }
    }
    html += '</li>';
    return(html);
}

function generate_pagination_html(total, current_page, items_per_page) {
    var max_pages = Math.ceil(total / items_per_page);
    list_html = '<div class="pagination-page position-left ' + ((current_page > 1) ? 'active' : 'inactive') + '" data-page="1"><i class="fa fa-angle-double-left" aria-hidden="true"></i></div>';
    list_html += '<div class="pagination-page position-left ' + ((current_page - 1 >= 1) ? 'active' : 'inactive') + '" data-page="' + (current_page - 1) + '"><i class="fa fa-angle-left" aria-hidden="true"></i></div>';
    list_html += '<div class="pagination-page position-right ' + ((current_page < max_pages) ? 'active' : 'inactive') + '" data-page="' + max_pages + '"><i class="fa fa-angle-double-right" aria-hidden="true"></i></div>';
    list_html += '<div class="pagination-page position-right ' + ((current_page < max_pages) ? 'active' : 'inactive') + '" data-page="' + (current_page + 1) + '"><i class="fa fa-angle-right" aria-hidden="true"></i></div>';
    list_html += '<div class="pagination-center-box">Seite ' + current_page + ' von ' + max_pages + '</div>';
    return (list_html);
}