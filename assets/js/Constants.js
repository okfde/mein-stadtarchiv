import moment from 'moment';

export const daterangepicker_locale = {
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

export const daterangepicker_ranges = {
   'heute': [moment(), moment()],
   'gestern': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
   'letzte 7 Tage': [moment().subtract(6, 'days'), moment()],
   'letzte 30 Tage': [moment().subtract(29, 'days'), moment()],
   'dieser Monat': [moment().startOf('month'), moment().endOf('month')],
   'letzter Monat': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
};

export const multiselect_options = {
    numberDisplayed: 0,
    includeSelectAllOption: true,
    allSelectedText: 'alles ausgewählt',
    nonSelectedText: 'bitte wählen',
    selectAllText: 'alles auswählen',
    nSelectedText: 'ausgewählt',
    buttonClass: 'form-control',
    buttonContainer: '<div class="btn-group bootstrap-multiselect" />'
};