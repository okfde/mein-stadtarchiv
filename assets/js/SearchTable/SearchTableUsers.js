import React from "react";
import SearchTable from './SearchTable'

export default class SearchTableUsers extends SearchTable {
    params = {
        sort_field: 'name',
        sort_order: 'asc',
        page: 1
    };
    apiUrl = '/api/admin/users';
    formId = 'user-search-form';
    varPrefix = 'searchTableUsers';
    loadParamsRegExp = [
        /\/admin\/user\/(.*)/g
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
                {row.firstname} {row.lastname}<br/>
                {row.email}
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
                {this.renderActionLink(`/admin/user/${row.id}/show`, 'info', true)}
                {this.renderActionLink(`/admin/user/${row.id}/edit`, 'edit', true)}
                {this.renderActionLink(`/admin/user/${row.id}/delete`, 'delete',  true)}
            </td>
        )
    }
}