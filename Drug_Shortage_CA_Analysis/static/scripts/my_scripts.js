// Source: https://select2.org/getting-started/basic-usage
$(document).ready(function () {
    $('.js-example-basic-single').select2({ minimumInputLength: 3 });
});
$('#s2').on('select2:select', function (e) {
    var sub = document.querySelector("#sub_cont");
    sub.hidden = false;
});


// Project JavaScript
function search_term(n) {
    window.subject = n;
    var sub = document.querySelector("#sub_cont");
    sub.hidden = true;
    var sby = document.querySelector("#searchby");
    sby.innerHTML = "";
    var s2 = document.querySelector("#s2");
    s2.innerHTML = "";
    var s2_cont = document.querySelector("#s2_cont");
    s2_cont.hidden = true;
    var ph = document.createElement("OPTION");
    ph.disabled = true;
    ph.selected = true;
    ph.innerHTML = "Search by";
    sby.appendChild(ph);
    if (n == 0) {
        var t1 = document.createElement("OPTION");
        t1.setAttribute("class", "type");
        t1.setAttribute("value", 0);
        t1.innerHTML = "Name";
        sby.appendChild(t1);
        var t2 = document.createElement("OPTION");
        t2.setAttribute("class", "type");
        t2.setAttribute("value", 1);
        t2.innerHTML = "DIN";
        sby.appendChild(t2);
        document.querySelector("#warning").hidden = true;
    }
    else if (n == 1) {
        var t1 = document.createElement("OPTION");
        t1.setAttribute("class", "type");
        t1.setAttribute("value", 0);
        t1.innerHTML = "Name";
        sby.appendChild(t1);
        var t2 = document.createElement("OPTION");
        t2.setAttribute("class", "type");
        t2.setAttribute("value", 1);
        t2.innerHTML = "Code";
        sby.appendChild(t2);
        document.querySelector("#warning").hidden = true;
    }
    else if (n == 2) {
        var t1 = document.createElement("OPTION");
        t1.setAttribute("class", "type");
        t1.setAttribute("value", 0);
        t1.innerHTML = "Name";
        sby.appendChild(t1);
        document.querySelector("#warning").hidden = false;
    }
    else {
        alert("Please choose an item from the list!");
        return;
    }
    s1b.hidden = false;
    return;
}

function get_dropdown(lists, c) {
    var lists = lists;
    window.type = c;
    var n = window.subject;
    if (n == 0) {
        if (c == 0) {
            populate_dropdowns(lists, 0, 0);
        }
        else if (c == 1) {
            populate_dropdowns(lists, 0, 1);
        }
    }
    else if (n == 1) {
        if (c == 0) {
            populate_dropdowns(lists, 1, 0);
        }
        else if (c == 1) {
            populate_dropdowns(lists, 1, 1);
        }
    }
    else if (n == 2) {
        populate_dropdowns(lists, 2, 0);
    }
    return;
}

function populate_dropdowns(lists, n, c) {
    var s2 = document.querySelector("#s2");
    var ph = document.createElement("OPTION");
    ph.disabled = true;
    ph.selected = true;
    ph.innerHTML = "";
    s2.appendChild(ph);
    var list = lists[n];
    var l = list.length;
    for (let i = 0; i < l; i++) {
        var opt = document.createElement("OPTION");
        if (n != 2) {
            opt.setAttribute("value", list[i]["code"]);
            if (n == 0) {
                if (c == 0) {
                    var name = list[i]["name"];
                    var comp = list[i]["company"]
                    opt.innerHTML = name + " [" + comp + "]";
                }
                else {
                    opt.innerHTML = list[i]["code"];
                }
            }
            else {
                if (c == 0) {
                    opt.innerHTML = list[i]["name"];
                }
                else {
                    opt.innerHTML = list[i]["code"];
                }
            }
        }
        else {
            opt.setAttribute("value", list[i]["name"]);
            opt.innerHTML = list[i]["name"];
        }
        s2.appendChild(opt);
    }
    var s2_cont = document.querySelector("#s2_cont");
    s2_cont.hidden = false;
    return;
}
