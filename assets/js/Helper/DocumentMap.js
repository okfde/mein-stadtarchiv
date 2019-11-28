import mapboxgl from 'mapbox-gl';
import {Decimal} from 'decimal.js';
import React from "react";
import ReactDOM from "react-dom";

export default class DocumentMap {
    apiUrl = '/api/geojson';

    constructor() {
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
        $.get(this.apiUrl, function (data) {
            deref_data.resolve(data);
        });
    };

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

    buildImageUrl(properties) {
        return config.cdnUrl + '/thumbnails/' + properties.id + '/' + properties.fileId + '/300/1.jpg';
    }

    closePopup() {
        this.popup.remove();
    }
};
