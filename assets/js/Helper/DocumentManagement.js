
export default class DocumentManagement {
    baseUrl = 'https://nominatim.openstreetmap.org/search?';
    address = {
        country: 'Deutschland',
    }
    params = {
        format: 'json',
        q: ''
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
        let params = Object.assign({}, this.params);
        const addressParts = this.getAddressParts();
        if (addressParts.some(part => !part)) {
            this.setGeocodeError();
            return;
        }
        addressParts.push('Deutschland');
        params.q = addressParts.join(', ');
        $.get(this.baseUrl + $.param(params))
            .then((data) => this.handleGeocodingResults(data));
    }

    getAddressParts() {
        const addressParts = []
        addressParts.push(document.getElementById('address').value);
        addressParts.push(document.getElementById('postcode').value);
        addressParts.push(document.getElementById('locality').value);
        return addressParts;
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