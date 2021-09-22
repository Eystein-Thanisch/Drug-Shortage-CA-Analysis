// Source: https://select2.org/getting-started/basic-usage
$(document).ready(function () {
    $('.js-example-basic-single').select2();
});
$('#s2_1').select2({
    placeholder: "Name",
    minimumInputLength: 3
});
$('#s2_2').select2({
    placeholder: "ID",
    minimumInputLength: 3
});

// JavaScript source code
function get_list(name, lists) {
    if (name = "drug") {
        list = lists[0];
        return list;
    }
    else if (name = "manufacturer") {
        list = lists[1];
        return list;
    }
    else if (name = "ingredient") {
        list = lists[2];
        return list;
    }
    else {
        alert("Please select an item from the list!")
    }
}