export const getUrlParams = () => {
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
};

export const buildImageUrl = (document_id, file_id, size) => {
    if (!size)
        size = 300;
    return stadtarchivConfig.cdnUrl + '/thumbnails/' + document_id + '/' + file_id + '/' + size + '/1.jpg';
};

export const requestGet = async (url) => {
    const response = await fetch(url, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    });
    return response.json();
};

export const requestPost = async (url, data, csrf_token) => {
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrf_token
        },
        body: JSON.stringify(data)
    });
    return response.json();
};