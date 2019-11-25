import React from "react";

const { Component } = React;

export default class SearchList extends Component {
    state = {
        page: 1,
        data: [],
        resultCount: 0,
        documents: [],
        initialized: false
    };
    itemsPerPage = 10;
    apiUrl = '/api/documents';

    componentDidMount() {
        this.init();
    }

    init() {
        this.setState({
            initialized: true,
            categories: {
                current: {
                    id: 'all',
                    title: 'Alle Archive'
                },
                parent: null,
                children: archives
            },
            csrf_token: csrf_token
        });
        this.search();
    }

    setPage(page) {
        if (page < 1 || page > this.state.pageMax)
            return;
        this.params.page = page;
        this.updateData();
    }

    search() {
        let params = {
            csrf_token: csrf_token
        };
        $.post(this.apiUrl, params)
            .then((data) => {
                this.setState({
                    documents: data.data
                });
            });
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
                <form id="search-form">
                    <p>
                        <label htmlFor="fulltext">Volltext</label>
                        <input type="text" id="fulltext" name="fulltext" className="form-control" />
                    </p>
                    <div className="container no-gutters" style={{marginBottom: '1rem'}}>
                        <div className="row">
                            <div className="col-md-12">
                                <label htmlFor="year_start">Zeitraum</label>
                            </div>
                        </div>
                        <div className="row">
                            <div className="col-5">
                                <input type="text" id="year_start" name="year_start" className="form-control" />
                            </div>
                            <div className="col-2 orientation-center">
                                -
                            </div>
                            <div className="col-5">
                                <input type="text" id="year_end" name="year_end" className="form-control" />
                            </div>
                        </div>
                    </div>
                    <p>
                        <label htmlFor="files_required">
                            <input type="checkbox" name="files_required" id="files_required" />
                            {' '}Nur Dokumente mit Medien
                        </label>
                    </p>
                    <p>
                        <label htmlFor="help_required">
                            <input type="checkbox" name="help_required" id="help_required" />
                            {' '}Unbekannte Inhalte
                        </label>
                    </p>
                    {this.renderCategories()}
                </form>
            </div>,
            <div className="col-md-8" key="results">
                {this.renderPagination()}
                {this.renderDocuments()}
            </div>
            ]
        );
    }

    renderDocuments() {
        let result = [];
        for (let i = 0; i < this.state.documents.length; i++) {
            result.push(this.renderDocument(this.state.documents[i]));
        }
        return result;
    }

    renderDocument(document) {
        let meta = [];
        console.log(document)
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
            <div key={document.id}>
                <h2>{document.title}</h2>
                <p>{meta.join(' | ')}</p>
            </div>
        );
    }

    renderCategories() {
        let options = [];
        if (this.state.categories.parent) {
            options.push(this.renderCategory(this.state.categories.parent, 'parent'))
        }
        else {
            options.push(this.renderCategory({id: 'root', title: 'Eine Ebene hoch'}, 'parent', true))
        }
        for (let i = 0; i < this.state.categories.children.length; i++) {
            options.push(this.renderCategory(this.state.categories.children[i], 'child'));
        }
        return (
            <div id="category-field">
                <input type="hidden" name="category" id="category" />
                <p id="category-current">
                    {this.state.categories.current.title}
                </p>
                <ul id="category-search">
                    {options}
                </ul>
            </div>
        );
    }

    renderCategory(category, type, disabled) {
        return (
            <li data-uid={category.id} className={`category-${type} ${(disabled) ? 'disabled' : ''}`} key={category.id}>
                {type === 'parent' &&
                    <i className="fa fa-arrow-circle-o-left" aria-hidden="true"></i>
                }
                {type === 'child' &&
                    <i className="fa fa-arrow-circle-o-right" aria-hidden="true"></i>
                }
                {' '}{category.title}
            </li>
        );
    }

    renderStatusLineTop() {
        return (
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
        )
    }

    renderStatusLineBottom() {
        return (
            <div className="row">
                <div className="col-md-12 search-table-result-footer">
                    <div className="d-flex justify-content-end">
                        {this.renderPagination()}
                    </div>
                </div>
            </div>
        )
    }

    renderStatusLineText() {
        let sort_list = [];
        for (let i = 0; i < this.sortDef.length; i++) {
            if (!this.operatorEnabled && this.sortDef[i].key === 'operator')
                continue;
            let attrib = {};
            if (this.params.sort_field === this.sortDef[i].key) {
                attrib['selected'] = 'selected';
            }
            sort_list.push(
                <option value={this.sortDef[i].key} {...attrib}>{this.sortDef[i].name}</option>
            )
        }
        let attrib_asc = {};
        let attrib_desc = {};
        if (this.params.sort_order === 'asc') {
            attrib_asc['selected'] = 'selected';
        }
        else {
            attrib_desc['selected'] = 'selected';
        }
        return (
            <div className="d-flex justify-content-start search-table-result-header-text">
                <span>
                    {this.state.resultCount} Ergebnis{this.state.resultCount === 1 ? '' : 'se'}
                </span>
                <select id="sort_order" name="sort_order" onChange={(event) => this.formSubmit(event)} className="selectpicker" data-width="fit">
                    <option value="asc" {...attrib_asc}>aufsteigend</option>
                    <option value="desc" {...attrib_desc}>absteigend</option>
                </select>
                <span>
                    sortiert nach
                </span>
                <select id="sort_field" name="sort_field" onChange={(event) => this.formSubmit(event)} className="selectpicker" data-width="fit" data-showIcon="false">
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
}

