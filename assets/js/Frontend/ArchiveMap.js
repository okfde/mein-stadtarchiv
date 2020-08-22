import mapboxgl from 'mapbox-gl';
import FrontpageGallery from './FrontpageGallery';

import React from "react";
import ReactDOM from "react-dom";

export default class ArchiveMap {
    constructor() {
        mapboxgl.accessToken = stadtarchivConfig.mapboxToken;

        this.map = new mapboxgl.Map({
            container: 'archive-map',
            style: 'mapbox://styles/mapbox/light-v10',
            center: [stadtarchivConfig.mapboxCenterLon, stadtarchivConfig.mapboxCenterLat],
            zoom: stadtarchivConfig.mapboxZoom
        });
        this.map.addControl(new mapboxgl.NavigationControl(), 'top-left');

        this.map.on('load', this.loadMapData.bind(this));
    };

    loadMapData() {
        let archiveGeojson = {
            type: 'FeatureCollection',
            features : frontpageMapData.filter(item => item.lat !== null && item.lon !== null).map((item, id) => {
                return {
                    type: 'Feature',
                    geometry: {
                        type: 'Point',
                        coordinates: [item.lon, item.lat]
                    },
                    properties: {
                        id: item.id,
                        title: item.title
                    }
                };
            })
        };
        this.map.addSource('data-source', {
            type: 'geojson',
            data: archiveGeojson
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
            //window.location.href = '/document/' + evt.features[0].properties.id;
        });
    }
}
