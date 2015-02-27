/**
 * Created by Sam Baron on 2/20/2015.
 */

// Send form data using Ajax
var sendFormAjax = function(form) {

    var ajax = $.ajax({
        type: form.elements["_method"].value,
        url: form.action,
        async: true,
        data: JSON.stringify($(form).serializeJSON()),
        dataType: "json",
        contentType: "application/json",
        cache: false,
        processData: false,
        complete: function (jqXHR, textStatus) {

            // Set response data and pass to form
            var respData = JSON.parse(jqXHR.responseText);
            form.reset();
            form = respData;
            console.log(respData);
            // Set response message
            var respMsg = respData.message;
            $("#message").text(respMsg);
        }
    });
};

var sendData = function (button) {

    // Disable button
    button.disabled = "disabled";
    button.innerHTML = "Sending";

    // Set form element
    var form = button.parentNode;

    // Send form data via Ajax
    sendFormAjax(form);

    // Enable button
    button.disabled = "";
    button.innerHTML = "Submit";

};

var sendTable = function (button) {

    // Disable button
    button.disabled = "disabled";
    button.innerHTML = "Sending";

    // Set table element
    var table = button.parentNode;

    // Loop through table forms (rows)
    var forms = table.querySelectorAll("form");
    Array.prototype.forEach.call(forms, function(form, i) {

        // Send form data via Ajax
        sendFormAjax(form);

    });

    // Enable button
    button.disabled = "";
    button.innerHTML = "Update";
};

