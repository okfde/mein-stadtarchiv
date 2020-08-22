import React from "react";

const { Component } = React;

export default class CategoryTableImport extends Component {
    state = {
        initialized: false
    };

    componentDidMount() {
        this.category_uid = document.getElementById('category-table-import').getAttribute('data-category');
        this.filename = document.getElementById('category-table-import').getAttribute('data-filename');
        this.apiUrl = '/api/admin/category/' + this.category_uid + '/table/' + this.filename;
        this.params = {
            csrf_token: document.getElementById('csrf_token').value
        };
        $.post(this.apiUrl, this.params)
            .then(data => {
                if (data.status) {
                    this.setState({
                        initialized: true,
                        error: true
                    });
                    return
                }
                this.setState({
                    initialized: true,
                    header: data.data.header,
                    datasets: data.data.datasets
                })
            });
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
        let trs = [];
        for (let i = 0; i < this.state.header.length; i++) {
            trs.push(this.renderRow(this.state.header[i], i));
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
                        {trs}
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
                    {this.renderFieldSelect()}
                </td>
                <td>{this.state.datasets[0][position]}</td>
            </tr>
        )
    }

    renderFieldSelect() {
        return(
            <select className="form-control">
                <optgroup label="Basis">
                    <option value="title">Laufende Nummer / ID</option>
                    <option value="title">Titel</option>
                    <option value="description">Beschreibung</option>
                    <option value="filename">Dateiname</option>
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