import React from "react";
import SearchTable from './SearchTable'

export default class SearchTableAdminAccount extends SearchTable {
    params = {
        sort_field: 'created',
        sort_order: 'desc',
        page: 1
    };
    apiUrl = '/api/admin/accounts';
    formId = 'admin-account-form';
    varPrefix = 'searchTableAccount';
    loadParamsRegExp = [
        /\/admin\/account\/(.*)/g
    ];

    sortDef = [
        { key: 'created', name: 'Registrierungsdatum' },
        { key: 'last_name', name: 'Name' }
    ];

    colDef = [
        { text: 'Name & IBAN' },
        { sortField: 'created', text: 'Erstellt' },
        { text: 'Zugangsmedien'},
        { text: 'Nachweis'},
        { text: 'Aktionen' }
    ];
    
    renderTableRow(row) {
        return (
            <tr>
                {this.renderTableCellName(row)}
                {this.renderTableCellCreated(row)}
                {this.renderTableCellTokens(row)}
                {this.renderTableCellProof(row)}
                {this.renderTableCellActions(row)}
            </tr>
        )
    }

    renderTableCellName(row) {
        return(
            <td>
                {row.name}<br/>
                <small>{this.formatAccountIBAN(row.iban)}</small>
            </td>
        )
    }

    renderTableCellCreated(row) {
        return(
            <td>{row.created.substr(8, 2)}.{row.created.substr(5, 2)}.{row.created.substr(0, 4)}</td>
        )
    }


    renderTableCellTokens(row) {
        let tokens = [];
        for (let i = 0; i < row.token.length; i++) {
            if (i !== 0)
                tokens.push(<br/>);
            tokens.push(this.renderTableCellToken(row.token[i]));
        }
        return(
            <td>{tokens}</td>
        )
    }

    renderTableCellToken(token) {
        return this.formatTokenType(token.type) + ': ' + this.formatTokenIdentifier(token);
    }

    renderTableCellProof(row) {
        return (
            <td>
                {this.formatAccountProof(row.proof)}
            </td>
        )
    }

    renderTableCellActions(row) {
        return(
            <td>
                {this.renderTableCellActionIcon(`/admin/account/${row.id}/show`, 'info', 'Details', true)}
                {this.renderTableCellActionIcon(`/admin/account/${row.id}/validate`, 'check', 'validieren', row.proof === 'photo' || !row.proof)}
            </td>
        )
    }
}