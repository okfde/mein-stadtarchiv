import mapboxgl from 'mapbox-gl';
import React from "react";

const { Component } = React;

import SearchListCategories from './SearchListCategories';


export default class DocumentMapSearch extends Component {
    state = {
        page: 1,
        data: [],
        resultCount: 0,
        params: {
            fulltext: '',
            files_required: false,
            category: 'all'
        },
        initialized: false
    };
    apiUrl = '/api/geojson';

    componentDidMount() {
        let params = this.state.params;
        params.csrf_token = csrf_token;
        this.setState({
            initialized: true,
            params: params
        });
        document.getElementById('map-search-form').onsubmit = (evt) => {
            evt.preventDefault();
            this.search(this.state.params);
        };

        mapboxgl.accessToken = config.mapbox_token;

        this.map = new mapboxgl.Map({
            container: 'document-map',
            style: 'mapbox://styles/mapbox/dark-v9',
            center: [10.448, 51.116],
            zoom: 5.5
        });
        this.map.addControl(new mapboxgl.NavigationControl(), 'top-left');

        var deref_map = new $.Deferred();
        var deref_data = new $.Deferred();

        $.when(deref_map, deref_data).done((mapready, data) => this.initMapData(mapready, data));
        this.map.on('load', function (data) {
            deref_map.resolve(data);
        });
        $.post(this.apiUrl, params)
            .then((data) => {
                deref_data.resolve(data);
                this.setState({
                });
            });
    }

    search(params) {
        $.post(this.apiUrl, params)
            .then((data) => {
                this.updateMapData(data);
            });
    }

    updateCategory(category) {
        let params = this.state.params;
        params.category = category;
        this.setState({
            params: params
        });
        this.search(params);
    }

    handleChange(event) {
        let params = this.state.params;
        params[event.target.id] = (event.target.type === 'checkbox') ? event.target.checked : event.target.value;
        this.setState({params: params});
        if (event.target.type === 'checkbox' || event.target.tagName.toLowerCase() === 'select') {
            this.search(params);
        }
    }

    render() {
        if (!this.state.initialized) {
            return (
                <div className={'search-table-loading'}>
                    ... wird geladen ...
                </div>
            );
        }
        return (
            <div className="row">
                <div className="col-md-3">
                    <label htmlFor="fulltext">Volltext</label>
                    <input
                        type="text"
                        id="fulltext"
                        name="fulltext"
                        className="form-control"
                        value={this.state.params.fulltext}
                        onChange={this.handleChange.bind(this)}
                    />
                </div>
                <div className="col-md-3">
                    <span className="fake-label">&nbsp;</span>
                    <label htmlFor="files_required">
                        <input
                            type="checkbox"
                            name="files_required"
                            id="files_required"
                            checked={this.state.params.files_required}
                            onChange={this.handleChange.bind(this)}
                        />
                        {' '}Nur Dokumente mit Medien
                    </label>
                </div>
                <div className="col-md-3">
                    <span className="fake-label">Kategorie</span>
                    <SearchListCategories
                      onUpdate={(category) => this.updateCategory(category)}
                    >
                    </SearchListCategories>
                </div>
                <div className="col-md-3">
                    <span className="fake-label">&nbsp;</span>
                    <input type="submit" name="submit" value="suchen" className="form-control"/>
                </div>
            </div>
        );
    }

    initMapData(mapready, data) {
        this.map.addSource('data-source', {
            type: 'geojson',
            data: data
        });
        this.map.addLayer({
            id: 'data-documents',
            type: 'circle',
            source: 'data-source',
            paint: {
                'circle-radius': 6,
                'circle-color': '#5cb85c',
                'circle-stroke-width': 1,
                'circle-stroke-color': '#89f789'
            }
        });
        this.popup = new mapboxgl.Popup({
            closeButton: false,
            closeOnClick: false
        });
        this.map.on('mouseenter', 'data-documents', (evt) => {
            this.map.getCanvasContainer().style.cursor = 'pointer';
            this.openPopup(evt);
        });
        this.map.on('mouseleave', 'data-documents',(evt) => {
            this.map.getCanvasContainer().style.cursor = '';
            this.closePopup(evt);
        });

        this.map.on('click', 'data-documents', (evt) => {
            window.location.href = '/document/' + evt.features[0].properties.id;
        });


    };

    updateMapData(geojson) {
        this.map.getSource('data-source').setData(geojson);
    }

    openPopup(evt) {
        let coordinates = evt.features[0].geometry.coordinates.slice();
        let content = '';
        if (evt.features[0].properties.binaryExists) {
            content += '<img class="img-fluid" src="' + this.buildImageUrl(evt.features[0].properties) + '">'
        }
        content += '<p class="document-map-popup-text">' + evt.features[0].properties.title + '</p>';
        while (Math.abs(evt.lngLat.lng - coordinates[0]) > 180) {
            coordinates[0] += evt.lngLat.lng > coordinates[0] ? 360 : -360;
        }
        this.popup.setLngLat(coordinates)
            .setHTML(content)
            .addTo(this.map);
    }

    buildImageUrl(properties, size) {
        if (!size)
            size = 300;
        return config.cdnUrl + '/thumbnails/' + properties.id + '/' + properties.fileId + '/' + size + '/1.jpg';
    }

    closePopup() {
        this.popup.remove();
    }
}

