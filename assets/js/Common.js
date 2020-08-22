export default class Common {
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

};
