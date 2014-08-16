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

