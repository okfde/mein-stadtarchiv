
export default class DocumentManagement {
    baseUrl = 'https://nominatim.openstreetmap.org/search?';
    params = {
        country: 'Deutschland',
        countrycodes: 'de',
        format: 'json'
    };
    constructor() {
        document.getElementById('document-form').onsubmit = (evt) => this.submitData(evt);
        document.getElementById('address').onkeydown = (evt) => this.resetGeocode(evt);
        document.getElementById('postcode').onkeydown = (evt) => this.resetGeocode(evt);
        document.getElementById('locality').onkeydown = (evt) => this.resetGeocode(evt);
    }

    resetGeocode() {
        document.getElementById('document-form').classList.remove('geocoded');
        document.getElementById('geocoding-error').style.display = 'none';
    }

    setGeocodeError() {
        document.getElementById('geocoding-error').style.display = 'block';
        document.getElementById('document-form').classList.add('geocoded');
    }

    submitData(evt) {
        if (document.getElementById('document-form').classList.contains('geocoded')) {
            return;
        }
        evt.preventDefault();
        let params = {};
        Object.assign(params, this.params);
        params.address = document.getElementById('address').value;
        params.postcode = document.getElementById('postcode').value;
        params.locality = document.getElementById('locality').value;
        if (!params.address || !params.postcode || !params.locality) {
            this.setGeocodeError();
            return;
        }
        $.get(this.baseUrl + $.param(params))
            .then((data) => this.handleGeocodingResults(data));
    }

    handleGeocodingResults(data) {
        if (data.length === 0) {
            this.setGeocodeError();
            return;
        }
        let geocoded = data[0];
        if (!geocoded.lat || !geocoded.lon) {
            this.setGeocodeError();
            return;
        }
        document.getElementById('lat').value = String(geocoded.lat);
        document.getElementById('lon').value = String(geocoded.lon);
        document.getElementById('document-form').classList.add('geocoded');
        document.getElementById('submit').click();
    }


}