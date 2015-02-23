/**
 * Created by Sam Baron on 2/20/2015.
 */


var sendData = function (button) {

    // Disable button
    button.disabled = "disabled";
    button.innerHTML = "Sending";

    // Set form element
    var form = button.parentNode;

    // Make AJAX request using form method
    var ajax = $.ajax({
        type: form.elements["_method"].value,
        url: form.action,
        async: true,
        data: JSON.stringify($(form).serializeJSON()),
        dataType: "json",
        contentType: "application/json",
        cache: false,
        processData: false,
        complete: function(jqXHR, textStatus) {

            // Reset button
            button.disabled = "";
            button.innerHTML = "Submit";

            // Set response data and pass to form
            var respData = jqXHR.responseText;
            form = respData;

            // Set response message
            var respMsg = JSON.parse(respData).message;
            $("#message").text(respMsg);

        }
    });
    
};

//var sendData = function (formID) {
//    var form = document.getElementById(formID);
//   // Create a FormData object from the form
//   // var data = new FormData(form);
//    var data = $("#"+formID).serializeJSON();
//    // Make a POST request to the file upload endpoint
//    var ajax = $.ajax(form.action, {
//        async: true,
//        type: 'PUT',
//        data: JSON.stringify(data),
//        cache: false,
//        contentType: "application/json",
//        processData: false,
//        dataType: 'json',
//        complete: function(jqXHR, textStatus) {
//            $("#message").text(textStatus);
//
//            }
//    });
//
//};
