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

import SearchTableArchives from './SearchTable/SearchTableArchives'

$(document).ready(function () {
    window.common = new Common();
    if (document.getElementById('archive-categories')) {
        window.archiveManagement = new ArchiveManagement();
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
});