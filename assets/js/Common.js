import {Decimal} from 'decimal.js';
import moment from 'moment';

export default class Common {

    daterangepicker_locale = {
        format: 'DD.MM.YYYY',
        applyLabel: "wählen",
        cancelLabel: "abbrechen",
        customRangeLabel: 'Eigener Bereich',
        daysOfWeek: [
            "So",
            "Mo",
            "Di",
            "Mi",
            "Do",
            "Fr",
            "Sa"
        ],
        monthNames: [
            "Januar",
            "Februar",
            "März",
            "April",
            "mai",
            "Juni",
            "Juli",
            "August",
            "September",
            "Oktober",
            "November",
            "Dezember"
        ]
    };

    daterangepicker_ranges = {
       'heute': [moment(), moment()],
       'gestern': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
       'letzte 7 Tage': [moment().subtract(6, 'days'), moment()],
       'letzte 30 Tage': [moment().subtract(29, 'days'), moment()],
       'dieser Monat': [moment().startOf('month'), moment().endOf('month')],
       'letzter Monat': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
    };

    multiselect_options = {
        numberDisplayed: 0,
        includeSelectAllOption: true,
        allSelectedText: 'alles ausgewählt',
        nonSelectedText: 'bitte wählen',
        selectAllText: 'alles auswählen',
        nSelectedText: 'ausgewählt',
        buttonClass: 'form-control',
        buttonContainer: '<div class="btn-group bootstrap-multiselect" />'
    };


    constructor () {
        window.onunload = function(){};
        this.storageAvailable = this.getStorageAvailable();
        this.setLastUrl();

        $('[data-toggle="tooltip"]').tooltip();
    };


    setLastUrl() {
        if (!this.storageAvailable)
            return;
        this.lastUrl = localStorage.getItem('lastUrl');
        localStorage.setItem('lastUrl', window.location.pathname);
    }

    getStorageAvailable() {
        try {
            let x = '__storage_test__';
            localStorage.setItem(x, x);
            localStorage.removeItem(x);
            return true;
        }
        catch(e) {
            return e instanceof DOMException && (
                // everything except Firefox
                e.code === 22 ||
                // Firefox
                e.code === 1014 ||
                // test name field too, because code might not be present
                // everything except Firefox
                e.name === 'QuotaExceededError' ||
                // Firefox
                e.name === 'NS_ERROR_DOM_QUOTA_REACHED') &&
                // acknowledge QuotaExceededError only if there's something already stored
                storage.length !== 0;
        }
    }

    getUrlParams() {
        let match;
        let pl     = /\+/g;
        let search = /([^&=]+)=?([^&]*)/g;
        let decode = function (s) { return decodeURIComponent(s.replace(pl, " ")); };
        let query  = window.location.search.substring(1);

        let urlParams = {};
        while (match = search.exec(query)) {
            urlParams[decode(match[1])] = decode(match[2]);
        }
        return urlParams;
    }

    buildImageUrl(document_id, file_id, size) {
        if (!size)
            size = 300;
        return config.cdnUrl + '/thumbnails/' + document_id + '/' + file_id + '/' + size + '/1.jpg';
    }

};
