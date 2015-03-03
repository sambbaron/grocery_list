/**
 * JavaScript for Entire App
 */


function postAjax(url, data, callback) {
    var ajax = new XMLHttpRequest();
    ajax.onload = function () {
        callback(ajax.responseText);
    };
    ajax.open("POST", url);
    ajax.send(data);
}

function postFormData(url, formId, callback) {
    var form = document.getElementById(formId);
    var formData = new FormData(form);
    var ajax = postAjax(url, formData, callback);
}

function responseRedirect (response) {
    location.assign(response);
}
