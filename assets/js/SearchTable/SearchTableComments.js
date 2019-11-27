import React from "react";
import SearchTable from './SearchTable'

export default class SearchTableArchives extends SearchTable {
    defaultStartDate = moment().subtract(3, 'month');
    defaultEndDate = moment();

    params = {
        sort_field: 'created',
        sort_order: 'desc',
        page: 1,
        daterange: this.defaultStartDate.format('DD.MM.YYYY') + ' - ' + this.defaultEndDate.format('DD.MM.YYYY'),
        status: ['0', '1']
    };
    apiUrl = '/api/admin/comments';
    formId = 'comment-search-form';
    varPrefix = 'searchTableComments';
    loadParamsRegExp = [
        /\/admin\/comment\/(.*)/g
    ];

    sortDef = [
        { key: 'created', name: 'Datum' }
    ];

    colDef = [
        { sortField: 'created', text: 'Erstellt' },
        { text: 'Autor'},
        { text: 'Dokument'},
        { text: 'Kommentar'},
        { text: 'Status'},
        { text: 'Aktionen' }
    ];

    init() {
        super.init();
        $('#status').multiselect(window.common.multiselect_options);
        $('#daterange').daterangepicker({
            startDate: this.defaultStartDate,
            endDate: this.defaultEndDate,
            ranges: window.common.daterangepicker_ranges,
            locale: window.common.daterangepicker_locale
        }, (start, end, label) => this.daterangepickerSubmit(start, end, label));
    }

    renderTableRow(row) {
        return (
            <tr key={row.id}>
                {this.renderTableCellCreated(row)}
                {this.renderTableCellAuthor(row)}
                {this.renderTableCellDocument(row)}
                {this.renderTableCellComment(row)}
                {this.renderTableCellStatus(row)}
                {this.renderTableCellActions(row)}
            </tr>
        )
    }

    renderTableCellCreated(row) {
        return(
            <td>
                {row.created.substr(8, 2)}.{row.created.substr(5, 2)}.{row.created.substr(0, 4)}<br/>
                {row.created.substr(11, 2)}:{row.created.substr(14, 2)}:{row.created.substr(17, 2)}
            </td>
        )
    }

    renderTableCellAuthor(row) {
        return(
            <td>
                <a href={`mailto:${row.author_email}`}>{row.author_name}</a><br/>
                <small>{row.author_email}</small>
            </td>
        )
    }

    renderTableCellDocument(row) {
        return(
            <td><a href={`/document/${row.document.id}`}>{row.document.title}</a></td>
        )
    }

    renderTableCellComment(row) {
        return(
            <td>{row.content}</td>
        )
    }

    renderTableCellStatus(row) {
        return(
            <td>
                {row.status === 0 &&
                    <i className="fa fa-question-circle-o" aria-hidden="true"></i>
                }
                {row.status === 1 &&
                    <i className="fa fa-check-circle-o" aria-hidden="true"></i>
                }
                {row.status === 2 &&
                    <i className="fa fa-eye" aria-hidden="true"></i>
                }
                {row.status === -1 &&
                    <i className="fa fa-ban" aria-hidden="true"></i>
                }
            </td>
        )
    }

    renderTableCellActions(row) {
        return (
            <td>
                {this.renderTableCellActionIcon(`/admin/comment/${row.id}/set-status?status=1`, 'check-circle-o', 'freischalten', [0, -1].includes(row.status))}
                {this.renderTableCellActionIcon(`/admin/comment/${row.id}/set-status?status=2`, 'eye', 'sichten', [0, -1, 1].includes(row.status))}
                {this.renderTableCellActionIcon(`/admin/comment/${row.id}/set-status?status=-1`, 'ban', 'bannen', [0, 1, 2].includes(row.status))}
            </td>
        )
    }
}