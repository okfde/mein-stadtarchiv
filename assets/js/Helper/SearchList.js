import React from "react";

const { Component } = React;

import SearchListCategories from './SearchListCategories';


export default class SearchList extends Component {
    defaultParams = {
        fulltext: '',
        yearStart: '',
        yearEnd: '',
        filesRequired: false,
        helpRequired: false,
        category: 'all',
        sort_field: 'random',
        sort_order: 'asc',
        page: 1
    };
    state = {
        page: 1,
        data: [],
        resultCount: 0,
        documents: [],
        params: Object.assign({}, this.defaultParams),
        initialized: false
    };
    sortDef = [
        { key: 'random', name: 'Zufall' },
        { key: 'title.sort', name: 'Titel'},
        { key: 'dateSort', name: 'Datum'},
        { key: '_score', name: 'Priorität'}
    ];
    itemsPerPage = 10;
    excerptLength = 250;
    apiUrl = '/api/documents';
    lastParams = {};

    componentDidMount() {
        let params = this.state.params;
        Object.assign(params, window.common.getUrlParams());
        params.filesRequired = (params.filesRequired) ? parseInt(params.filesRequired) && true : false;
        params.helpRequired = (params.helpRequired) ? parseInt(params.helpRequired) && true : false;
        params.csrf_token = config.csrf_token;
        if (!params.random_seed)
            params.random_seed = Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
        this.setState({
            initialized: true,
            params: params
        });
        this.search(params);
        document.getElementById('search-form').onsubmit = (evt) => {
            evt.preventDefault();
            this.search(this.state.params);
        };
    }

    componentDidUpdate(prevProps, prevState, snapshot) {
        $(".selectpicker").selectpicker('refresh');
        $('.btn-icon').tooltip();
    }

    checkUpdateUrl() {
        for (const [key, value] of Object.entries(this.state.params)) {
            if (['csrf_token'].includes(key)) {
                continue;
            }
            if (this.lastParams[key] !== value) {
                return this.updateUrl();
            }
        }
    }

    updateUrl() {
        let url_params = [];
        this.lastParams = {};
        for (const [key, value] of Object.entries(this.state.params)) {
            if (['csrf_token'].includes(key)) {
                continue;
            }
            this.lastParams[key] = value;
            if (!value || this.defaultParams[key] === value)
                continue;
            if (['helpRequired', 'filesRequired'].includes(key)) {
                url_params.push(key + '=' + ((value) ? '1' : '0'));
            }
            else {
                url_params.push(key + '=' + encodeURIComponent(value));
            }
        }
        let url = '/recherche' + ((url_params.length) ? '?' : '') + url_params.join('&');
        history.replaceState(this.lastParams, 'Recherche | Mein Stadtarchiv', url);
    }

    search(params) {
        if (params.fulltext && !this.lastParams.fulltext) {
            params.sort_field = '_score';
            params.sort_order = 'desc';
            this.setState({
                params: params
            });
        }
        if (!params.fulltext && params.sort_field === '_score') {
            params.sort_field = 'random';
            params.sort_order = 'asc';
            this.setState({
                params: params
            });
        }
        this.checkUpdateUrl();
        $.post(this.apiUrl, params)
            .then((data) => {
                this.setState({
                    documents: data.documents,
                    page: this.state.params.page,
                    resultCount: data.count,
                    pageMax: (data.count) ? Math.ceil(data.count / this.itemsPerPage) : 1
                });
            });
    }

    setPage(page) {
        if (page < 1 || page > this.state.pageMax)
            return;
        let params = this.state.params;
        params.page = page;
        this.setState({
            params: params
        });
        this.search(params);
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
        return ([
            <div className="col-md-4" key="sidebar">
                <h3>Suche</h3>
                <p>
                    <label htmlFor="fulltext">Volltext</label>
                    <input
                        type="text"
                        id="fulltext"
                        name="fulltext"
                        className="form-control"
                        value={this.state.params.fulltext}
                        onChange={this.handleChange.bind(this)}
                    />
                </p>
                <div className="container no-gutters" style={{marginBottom: '1rem'}}>
                    <div className="row">
                        <div className="col-md-12">
                            <label htmlFor="yearStart">Zeitraum</label>
                        </div>
                    </div>
                    <div className="row">
                        <div className="col-5">
                            <input
                                type="number"
                                id="yearStart"
                                name="yearStart"
                                className="form-control"
                                value={this.state.params.yearStart}
                                onChange={this.handleChange.bind(this)}
                            />
                        </div>
                        <div className="col-2 orientation-center">
                            -
                        </div>
                        <div className="col-5">
                            <input
                                type="number"
                                id="yearEnd"
                                name="yearEnd"
                                className="form-control"
                                value={this.state.params.yearEnd}
                                onChange={this.handleChange.bind(this)}
                            />
                        </div>
                    </div>
                </div>
                <p>
                    <label htmlFor="filesRequired">
                        <input
                            type="checkbox"
                            name="filesRequired"
                            id="filesRequired"
                            checked={this.state.params.filesRequired}
                            onChange={this.handleChange.bind(this)}
                        />
                        {' '}Nur Dokumente mit Medien
                    </label>
                </p>
                <p>
                    <label htmlFor="helpRequired">
                        <input
                            type="checkbox"
                            name="helpRequired"
                            id="helpRequired"
                            checked={this.state.params.helpRequired}
                            onChange={this.handleChange.bind(this)}
                        />
                        {' '}Unbekannte Inhalte
                    </label>
                </p>
                <SearchListCategories
                  onUpdate={(category) => this.updateCategory(category)}
                >
                </SearchListCategories>
                <p>
                    <input type="submit" name="submit" value="suchen" className="form-control"/>
                </p>
            </div>,
            <div className="col-md-8" key="results">
                {this.renderStatusLineTop()}
                {this.renderDocuments()}
                {this.renderStatusLineBottom()}
            </div>
        ]);
    }

    renderDocuments() {
        let results = [];
        for (let i = 0; i < this.state.documents.length; i++) {
            results.push(this.renderDocument(this.state.documents[i]));
        }
        return (
            <ul id="search-results">
                {results}
            </ul>
        );
    }

    renderDocument(document) {
        let meta = [];
        if (document.dateBegin && document.dateEnd) {
            meta.push('Jahr ' + this.formatYear(document.dateBegin) + ' - ' + this.formatYear(document.dateEnd));
        }
        else if (document.date) {
            meta.push('Jahr ' + this.formatYear(document.date));
        }
        else if (document.dateText) {
            meta.push('Jahr ' + document.dateText);
        }
        if (document.origination) {
            meta.push('Quelle: ' + document.origination);
        }
        for (let i = 0; i < document.categoryFull.length; i++) {
            meta.push('Kategorie: ' + document.categoryFull[i]);
        }
        return(
            <li key={document.id}>
                <div className="search-result-text">
                    <h2>
                        <a href={`/document/${document.id}`}>
                            {(document.title) ? document.title : 'Unbekanntes Dokument'}
                        </a>
                    </h2>
                    <p className="search-result-meta">{meta.join(' | ')}</p>
                    {document.description &&
                        <p className="search-result-description">{this.formatExcept(document.description)}</p>
                    }
                </div>
                {document.files && <div className="search-result-image">
                    <img src={window.common.buildImageUrl(document.id, document.files[0].id, 150)} />
                </div>}
            </li>
        );
    }

    renderStatusLineTop() {
        return (
            <div className="container no-gutters">
                <div className="row">
                    <div className="col-md-12 search-table-result-header">
                        <div className="d-flex justify-content-between bd-highlight">
                            {this.renderStatusLineText()}
                            <div className="d-flex justify-content-end">
                                {this.renderPagination()}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        )
    }

    renderStatusLineBottom() {
        return (
            <div className="container no-gutters">
                <div className="row">
                    <div className="col-md-12 search-table-result-footer">
                        <div className="d-flex justify-content-end">
                            {this.renderPagination()}
                        </div>
                    </div>
                </div>
            </div>
        )
    }

    renderStatusLineText() {
        let sort_list = [];
        for (let i = 0; i < this.sortDef.length; i++) {
            if (this.sortDef[i].key === '_score' && !this.state.params.fulltext) {
                continue;
            }
            sort_list.push(
                <option value={this.sortDef[i].key} key={this.sortDef[i].key}>{this.sortDef[i].name}</option>
            )
        }
        return (
            <div className="d-flex justify-content-start search-table-result-header-text">
                <span>
                    {this.state.resultCount === 10000 && <span>Über </span>}
                    {this.state.resultCount} Ergebnis{this.state.resultCount === 1 ? '' : 'se'}
                </span>
                <select
                    id="sort_order"
                    name="sort_order"
                    onChange={this.handleChange.bind(this)}
                    className="selectpicker"
                    data-width="fit"
                    value={this.state.params.sort_order}
                >
                    <option value="asc">aufsteigend</option>
                    <option value="desc">absteigend</option>
                </select>
                <span>
                    sortiert nach
                </span>
                <select
                    id="sort_field"
                    name="sort_field"
                    onChange={this.handleChange.bind(this)}
                    className="selectpicker"
                    data-width="fit"
                    value={this.state.params.sort_field}
                >
                    {sort_list}
                </select>
            </div>
        )
    }

    renderPagination() {
        return(
            <nav aria-label="pagination">
                <ul className="pagination justify-content-end">
                    <li className={'page-item' + (this.state.page === 1 ? ' disabled' : '')}>
                        <a className="page-link" href="#" aria-label="first" onClick={this.setPage.bind(this, 1)}>
                            <span aria-hidden="true">&laquo;</span>
                        </a>
                    </li>
                    <li className={'page-item' + (this.state.page === 1 ? ' disabled' : '')}>
                        <a className="page-link" href="#" aria-label="previous" onClick={this.setPage.bind(this, this.state.page - 1)}>
                            <span aria-hidden="true">&lsaquo;</span>
                        </a>
                    </li>
                    <li className="page-item disabled">
                        <span className="page-link">{this.state.page}/{this.state.pageMax}</span>
                    </li>
                    <li className={'page-item' + (this.state.page >= this.state.pageMax ? ' disabled' : '')}>
                        <a className="page-link" href="#" aria-label="next" onClick={this.setPage.bind(this, this.state.page + 1)}>
                            <span aria-hidden="true">&rsaquo;</span>
                        </a>
                    </li>
                    <li className={'page-item' + (this.state.page >= this.state.pageMax ? ' disabled' : '')}>
                        <a className="page-link" href="#" aria-label="last" onClick={this.setPage.bind(this, this.state.pageMax)}>
                            <span aria-hidden="true">&raquo;</span>
                        </a>
                    </li>
                </ul>
            </nav>
        )
    }

    renderTableRows() {
        let rows = [];
        for (let i = 0; i < this.state.data.length; i++) {
            rows.push(this.renderTableRow(this.state.data[i]))
        }
        return (
            <tbody>
            {rows}
            </tbody>
        )
    }

    formatDate(date) {
        if (!date)
            return '';
        return date.substr(8, 2) + '.' + date.substr(5, 2) + '.' + date.substr(0, 4);
    }

    formatDateTime(datetime) {
        if (!datetime)
            return '';
        return window.common.datetimeify(datetime);
    }

    formatYear(date) {
        return date.substr(0, 4);
    }

    formatExcept(text) {
        if (text.length > this.excerptLength)
            return text.substr(0, this.excerptLength) + ' ...';
        return text;
    }
}

