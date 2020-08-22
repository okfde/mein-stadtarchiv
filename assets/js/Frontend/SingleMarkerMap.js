import React from "react";
import {Map, Marker, Popup, TileLayer} from 'react-leaflet'

const { Component } = React;

export default class SingleMarkerMap extends Component {

    state = {
        lat: 'null',
        lon: 'null',
        zoom: 13,
    };

    componentDidMount() {
        this.setState({
            lat: $('#lat-value').text(),
            lon: $('#lon-value').text()
        })
    }

    render() {
        if (isNaN(this.state.lat) || isNaN(this.state.lon)) {
            return ''
        }
        return (
            <Map style={{height: '500px'}} center={[this.state.lat, this.state.lon]} zoom={this.state.zoom}>
                <TileLayer
                    attribution='&amp;copy <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                <Marker position={[this.state.lat, this.state.lon]}>
                </Marker>
            </Map>
        )
    }

}