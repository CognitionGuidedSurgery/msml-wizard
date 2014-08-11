function load_files(elements) {
    $.get("/api/file", function (data) {
        //options = "";

        elements.empty()

        for (index in data) {
            //    console.log(data[index]);
            //options += "<option value='" + data[index] + "'>" + data[index] + "</option>"
            var option = $('<option/>');
            option.attr({ 'value': data[index] }).text(data[index]);
            elements.append(option);
            elements.selectpicker('refresh');
        }
    });
}

$(function () {
    $('.progressbar').progressbar();
    load_files($('#select'));
    $('#file-upload-form').on('submit', uploadFile);
});

function openUploadDialog() {
    $('#file-upload-modal').modal();
}

function uploadFile(event) {
    event.stopPropagation();
    event.preventDefault();

    var data = new FormData(document.getElementById('file-upload-form'));
    /*
     var request = new XMLHttpRequest();
     request.open("PUT", "/api/file", true);
     request.send(data); */


    // AJAX Request
    $.ajax({
        url: "/api/file",
        type: "PUT",
        data: data,
        processData: false,
        contentType: false,
        dataType: "json",
        xhr: function () {
            var xhr = $.ajaxSettings.xhr();
            xhr.upload.onprogress = function (evt) {
                var p = evt.loaded * 100 / evt.total;
                $('#file-upload-form .progress-bar').css('width', p + "%");
                console.log("Uploaded: ", p);
            };
            xhr.upload.onload = function () {
            };
            return xhr;
        },
        success: function (response) {
            $('#file-upload-modal').modal('dismiss');
        },
        error: function () {
            console.log("General error occured", "e");
        },
        complete: function () {
            load_files($('#select'));
        }
    });
    return false;
}