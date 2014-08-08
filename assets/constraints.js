function isChecked(item, subitem) {
    if (subitem == undefined) {
        return $("#" + item).prop('checked');
    }
    else {
        item = item + "_" + subitem;
        return isChecked(item);
    }
}


function evalConstraints() {
    $(constraints).each(function (k, v) {
        var pred = v[0];
        var id = v[1];
        var element = $('#' + id);

        var p = pred();
        element.prop("disabled", p);
        if (p) {
            console.log(element, "enabled");
            element.removeClass('disabled');
        }
        else {
            console.log(element, "disabled");
            element.addClass('disabled');
        }

        if (element.hasClass('slider-textfield')) {
            var slid = $('#' + element.prop('id') + "_slider");
            slid.slider(p ? "enable" : "disable");
        }

        if (element.hasClass("panel-body")) { // page (textpage or formpage)
            if (p) {
                element.show();
            }
            else {
                element.hide()
            }
        }
    });
}


function submit_wizard() {
    $.ajax({
        type: "POST",
        url: "/api/generate/" + wizard_name,
        data: $('form').serialize(),
        success: function (response, status, request) {
            var disp = request.getResponseHeader('Content-Disposition');
            if (disp && disp.search('attachment') != -1) {
                var type = request.getResponseHeader('Content-Type');
                var blob = new Blob([response], { type: type });

                if (typeof window.navigator.msSaveBlob !== 'undefined') {
                    // IE workaround for "HTML7007: One or more blob URLs were revoked by closing the blob for which they were created. These URLs will no longer resolve as the data backing the URL has been freed."
                    window.navigator.msSaveBlob(blob);
                } else {
                    var URL = window.URL || window.webkitURL;
                    var downloadUrl = URL.createObjectURL(blob);
                    window.location = downloadUrl;
                }
            }
        },
        error: function (response) {
            alert("error");
        }
    });
    return false;
}