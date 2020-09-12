import '../sass/base.scss'
import '../sass/webapp.scss'

import React from "react";
import ReactDOM from "react-dom";

import Common from './Common';

import SearchList from './Frontend/SearchList'
import ArchiveMap from "./Frontend/ArchiveMap";
import SingleMarkerMap from "./Frontend/SingleMarkerMap";
import DocumentMapSearch from './Frontend/DocumentMapSearch';

import UserManagement from "./Backend/UserManagement";
import ArchiveManagement from './Backend/ArchiveManagement'
import DocumentManagement from './Backend/DocumentManagement';
import CategoryTableImport from "./Backend/CategoryTableImport";
import SubsiteManagement from "./Backend/SubsiteManagement";
import CategoryFileUpload from "./Backend/CategoryFileUpload";

import SearchTableArchives from './SearchTable/SearchTableArchives'
import SearchTableComments from './SearchTable/SearchTableComments';
import SearchTableSubsites from "./SearchTable/SearchTableSubsites";
import SearchTableUsers from "./SearchTable/SearchTableUsers";
import FrontpageGallery from "./Frontend/FrontpageGallery";


$(document).ready(function () {
    window.common = new Common();

    let helperObjects = {
        'archive-map': ArchiveMap,
        'archive-categories': ArchiveManagement,
        'user-form': UserManagement,
        'subsite-form': SubsiteManagement,
        'document-form': DocumentManagement
    }

    for (const [html_id, HelperClass] of Object.entries(helperObjects)) {
        if (document.getElementById(html_id)) {
            window[HelperClass.name.charAt(0).toLowerCase() + HelperClass.name.slice(1)] = new HelperClass();
        }
    }
    let reactObjects = {
        'search-list-box': SearchList,
        'frontpage-gallery': FrontpageGallery,
        'category-table-import': CategoryTableImport,
        'map-search-form': DocumentMapSearch,
        'user-search-results': SearchTableUsers,
        'subsite-search-results': SearchTableSubsites,
        'archive-search-results': SearchTableArchives,
        'comment-search-results': SearchTableComments,
        'single-maker-map-container': SingleMarkerMap,
        'category-file-upload-container': CategoryFileUpload
    }

    for (const [html_id, ReactClass] of Object.entries(reactObjects)) {
        if (document.getElementById(html_id)) {
            ReactDOM.render(
                <ReactClass ref={(reactClass) => {window[ReactClass.name.charAt(0).toLowerCase() + ReactClass.name.slice(1)] = reactClass}} />,
                document.getElementById(html_id)
            );
        }
    }
});