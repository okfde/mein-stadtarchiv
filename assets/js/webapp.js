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
import SingleMarkerMap from "./SingleMarkerMap";
import CategoryFileUpload from "./CategoryFileUpload";
import DocumentMapSearch from './Helper/DocumentMapSearch';
import CategoryTableImport from "./Import/CategoryTableImport";
import SearchTableSubsites from "./SearchTable/SearchTableSubsites";
import SubsiteManagement from "./Helper/SubsiteManagement";


$(document).ready(function () {
    window.common = new Common();
    if (document.getElementById('archive-categories')) {
        window.archiveManagement = new ArchiveManagement();
    }
    if (document.getElementById('subsite-form')) {
        window.subsiteManagement = new SubsiteManagement();
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
    if (document.getElementById('category-table-import')) {
        ReactDOM.render(
            <CategoryTableImport ref={(categoryTableImport) => {window.categoryTableImport = categoryTableImport}} />,
            document.getElementById('category-table-import')
        );
    }
    if (document.getElementById('map-search-form')) {
        ReactDOM.render(
            <DocumentMapSearch ref={(documentMapSearch) => {window.documentMapSearch = documentMapSearch}} />,
            document.getElementById("map-search-form"));
    }
    if (document.getElementById('subsite-search-form')) {
        ReactDOM.render(
            <SearchTableSubsites ref={(searchTableSubsites) => {window.searchTableSubsites = searchTableSubsites}} />,
            document.getElementById("subsite-search-results"));
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

    if (document.getElementById('single-maker-map-container')) {
        ReactDOM.render(
            <SingleMarkerMap ref={(ref) => {window.fileGallery = ref}}/>,
            document.getElementById('single-maker-map-container')
        )
    }

    if (document.getElementById('category-file-upload-container')) {
        ReactDOM.render(
            <CategoryFileUpload ref={(ref) => {window.categoryFileUpload = ref}}/>,
            document.getElementById('category-file-upload-container')
        )
    }
});