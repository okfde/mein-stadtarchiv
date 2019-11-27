import 'core-js/fn/string/includes';
import 'core-js/es7/array';
import 'core-js/fn/object/assign';

import '../sass/base.scss'
import '../sass/webapp.scss'

import React from "react";
import ReactDOM from "react-dom";

import Common from './Common';
import SearchList from './Helper/SearchList'
import ArchiveManagement from './Helper/ArchiveManagement'
import DocumentManagement from './Helper/DocumentManagement';

import SearchTableArchives from './SearchTable/SearchTableArchives'
import SearchTableComments from './SearchTable/SearchTableComments';


$(document).ready(function () {
    window.common = new Common();
    if (document.getElementById('archive-categories')) {
        window.archiveManagement = new ArchiveManagement();
    }
    if (document.getElementById('document-form')) {
        window.documentManagement = new DocumentManagement();
    }

    if (document.getElementById('search-list-box')) {
        ReactDOM.render(
            <SearchList ref={(searchList) => {window.searchList = searchList}} />,
            document.getElementById('search-list-box')
        );
    }

    if (document.getElementById('archive-search-form')) {
        ReactDOM.render(
            <SearchTableArchives ref={(searchTableArchives) => {window.searchTableArchives = searchTableArchives}} />,
            document.getElementById("archive-search-results"));
    }
    if (document.getElementById('comment-search-form')) {
        ReactDOM.render(
            <SearchTableComments ref={(searchTableComments) => {window.searchTableComments = searchTableComments}} />,
            document.getElementById("comment-search-results"));
    }
});