import React from "react";

const { Component } = React;

import SearchListCategories from './SearchListCategories';


export default class SearchList extends Component {
    state = {
        page: 1,
        data: [],
        resultCount: 0,
        documents: [],
        params: {
            fulltext: '',
            year_start: '',
            year_end: '',
            files_required: false,
            help_required: false,
            category: 'all',
            sort_field: 'random',
            sort_order: 'asc',
            page: 1
        },
        initialized: false
    };
    sortDef = [
        { key: 'random', name: 'Zufall' },
        { key: 'title', name: 'Titel'}
    ];
    itemsPerPage = 10;
    excerptLength = 250;
    apiUrl = '/api/documents';

    componentDidMount() {
        let params = this.state.params;
        params.csrf_token = csrf_token;
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
        $('.btn-icon').tooltip()
    }

    search(params) {
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
                            <label htmlFor="year_start">Zeitraum</label>
                        </div>
                    </div>
                    <div className="row">
                        <div className="col-5">
                            <input
                                type="text"
                                id="year_start"
                                name="year_start"
                                className="form-control"
                                value={this.state.params.year_start}
                                onChange={this.handleChange.bind(this)}
                            />
                        </div>
                        <div className="col-2 orientation-center">
                            -
                        </div>
                        <div className="col-5">
                            <input
                                type="text"
                                id="year_end"
                                name="year_end"
                                className="form-control"
                                value={this.state.params.year_end}
                                onChange={this.handleChange.bind(this)}
                            />
                        </div>
                    </div>
                </div>
                <p>
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
                </p>
                <p>
                    <label htmlFor="help_required">
                        <input
                            type="checkbox"
                            name="help_required"
                            id="help_required"
                            checked={this.state.params.help_required}
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
        if (document.date_begin && document.date_end) {
            meta.push('Jahr ' + this.formatYear(document.date_begin) + ' - ' + this.formatYear(document.date_end));
        }
        else if (document.date) {
            meta.push('Jahr ' + this.formatYear(document.date));
        }
        if (document.origination) {
            meta.push('Quelle: ' + document.origination);
        }
        for (let i = 0; i < document.category_full.length; i++) {
            meta.push('Kategorie: ' + document.category_full[i]);
        }
        return(
            <li key={document.id}>
                <div className="search-result-text">
                    <h2><a href={`/document/${document.id}`}>{document.title}</a></h2>
                    <p className="search-result-meta">{meta.join(' | ')}</p>
                    {document.description &&
                        <p className="search-result-description">{this.formatExcept(document.description)}</p>
                    }
                </div>
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
            sort_list.push(
                <option value={this.sortDef[i].key} key={this.sortDef[i].key}>{this.sortDef[i].name}</option>
            )
        }
        return (
            <div className="d-flex justify-content-start search-table-result-header-text">
                <span>
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

