import React from "react";

const { Component } = React;

export default class CategoryTableImport extends Component {
    state = {
        initialized: false
    };

    componentDidMount() {
        this.params = {
            csrf_token: document.getElementById('csrf_token').value
        };
        this.setState({
            initialized: true,
            header: tableHeaderData,
            datasets: tablePreviewData,
            mapping: (new Array(tableHeaderData.length)).fill('identifier')
        })
    }

    updateMapping(position, evt) {
        let mapping = [...this.state.mapping];
        mapping[position] = evt.target.value;
        this.setState({
            mapping: mapping
        });
        document.getElementById('mapping').value = JSON.stringify(mapping);
    }

    render() {
        if (!this.state.initialized) {
            return (<div className="row row-form"><div className="col-md-12">... wird geladen ...</div></div>);
        }
        if (this.state.error) {
            return (
                <div className="row row-form">
                    <div className="col-md-12">
                        <div className="alert-danger" style={{padding: '10px', textAlign: 'center'}}>
                            Tabelle kann nicht gelesen werden.
                        </div>
                    </div>
                </div>
            );
        }
        return (
            <div className="row row-form">
                <div className="col-md-12">
                    <table className="table">
                        <thead>
                        <tr>
                            <th>Tabellen-Wert</th>
                            <th>Bedeutung</th>
                            <th>Beispiel</th>
                        </tr>
                        </thead>
                        <tbody>
                        {this.state.header.map((row, i) => this.renderRow(row, i))}
                        </tbody>
                    </table>
                </div>
            </div>
        )
    }

    renderRow(field, position) {
        return(
            <tr key={`row-${position}`}>
                <td>{field}</td>
                <td>
                    {this.renderFieldSelect(position)}
                </td>
                <td>{this.state.datasets[0][position]}</td>
            </tr>
        )
    }

    renderFieldSelect(position) {
        return(
            <select className="form-control" value={this.state.mapping[position]} onChange={this.updateMapping.bind(this, position)}>
                <optgroup label="Basis">
                    <option value="identifier">Laufende Nummer / ID</option>
                    <option value="title">Titel</option>
                    <option value="description">Beschreibung</option>
                    <option value="filename">Dateiname</option>
                    <option value="photographer">Fotograf</option>
                </optgroup>
                <optgroup label="Lizenz">
                    <option value="licence">Lizenz</option>
                    <option value="licence-url">Lizenz-URL</option>
                    <option value="author">Autor</option>
                    <option value="author-url">Autor-URL</option>
                </optgroup>
                <optgroup label="Geographie">
                    <option value="address">Straße und Hausnummer</option>
                    <option value="postcode">Postleitzahl</option>
                    <option value="locality">Ort</option>
                    <option value="lat">Längengrad</option>
                    <option value="lon">Breitengrad</option>
                </optgroup>
                <optgroup label="Datum">
                    <option value="date-year">Jahreszahl</option>
                    <option value="date-year-begin">Jahreszahl Beginn</option>
                    <option value="date-year-end">Jahreszahl Ende</option>
                    <option value="date-full">Vollständiges Datum</option>
                </optgroup>

            </select>
        )
    }

}