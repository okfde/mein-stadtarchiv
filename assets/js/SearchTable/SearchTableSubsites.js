import React from "react";
import SearchTable from './SearchTable'

export default class SearchTableSubsites extends SearchTable {
    params = {
        sort_field: 'title',
        sort_order: 'asc',
        page: 1
    };
    apiUrl = '/api/admin/subsites';
    formId = 'subsite-search-form';
    varPrefix = 'searchTableSubsites';
    loadParamsRegExp = [
        /\/admin\/subsite\/(.*)/g
    ];

    sortDef = [
        { key: 'created', name: 'Registrierungsdatum' },
        { key: 'title', name: 'Name' }
    ];

    colDef = [
        { sortField: 'title', text: 'Name' },
        { text: 'Aktionen' }
    ];

    renderTableRow(row) {
        return (
            <tr key={row.id}>
                {this.renderTableCellName(row)}
                {this.renderTableCellActions(row)}
            </tr>
        )
    }

    renderTableCellName(row) {
        return(
            <td>
                {row.title}
            </td>
        )
    }

    renderTableCellCreated(row) {
        return(
            <td>{row.created.substr(8, 2)}.{row.created.substr(5, 2)}.{row.created.substr(0, 4)}</td>
        )
    }

    renderTableCellActions(row) {
        return (
            <td>
                {this.renderActionLink(`/admin/subsite/${row.id}/show`, 'info', true)}
                {this.renderActionLink(`/admin/subsite/${row.id}/edit`, 'edit', true)}
                {this.renderActionLink(`/admin/subsite/${row.id}/delete`, 'delete',  true)}
            </td>
        )
    }
}