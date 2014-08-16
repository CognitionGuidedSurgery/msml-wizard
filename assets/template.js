function showTemplateAsDialog() {
    $('#save-template-modal').modal();
    return false;
}

function saveTemplateAs(event) {
    event.stopPropagation();
    event.preventDefault();
    // stop event processing

    var data = new FormData(document.getElementById('wizard'));
    data.append("__name__", $('#template_name').val());
    data.append("__description__", $('#template_description').val());

    // AJAX Request
    $.ajax({
        url: "/api/templates",
        type: "POST",
        data: data,
        processData: false,
        contentType: false,
        dataType: "json",
        success: function (response) {
            $('#save-template-modal').modal('hide');
        },
        error: function (e) {
            console.log(e);
            alert("An error has occured: " + e)
        },
        complete: function () {
        }
    });
}
// from: http://jquery-howto.blogspot.de/2009/09/get-url-parameters-values-with-jquery.html
// Read a page's GET URL variables and return them as an associative array.
function getUrlVars() {
    var vars = [], hash;
    var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
    for (var i = 0; i < hashes.length; i++) {
        hash = hashes[i].split('=');
        vars.push(hash[0]);
        vars[hash[0]] = hash[1];
    }
    return vars;
}

function load_template(name) {
    if (name == undefined) {
        name = getUrlVars()['load'];
    }

    $.get("/api/templates", {'template_name': name},
        function (data) {
            $('input[name]').each(
                function (index, item) {
                    q = $(item);
                    if (q.attr('type') == 'radio' || q.attr('type') == 'checkbox') {
                        if (q.attr('name') in data
                            && q.attr('value') == data[q.attr('name')]) {
                            q.attr('checked', 'checked');
                            console.log("check: ", q);
                        }
                    }
                    else {
                        if (q.attr('name') in data) {
                            q.val(data[q.attr('name')]);
                            console.log("set value", q);
                        }
                    }
                }
            );
            evalConstraints();
        });
}


$(function () {
    $('button#save-as-template').on('click', showTemplateAsDialog);
    $('button#submit-save-as-template').on('click', saveTemplateAs);

    if ('load' in getUrlVars()) {
        load_template();
    }
});