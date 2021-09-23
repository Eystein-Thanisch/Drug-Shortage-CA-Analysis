// Source: https://select2.org/getting-started/basic-usage

$(document).ready(function () {
    $('.js-example-basic-single').select2({ minimumInputLength: 3 });
});
$('#s2').on('select2:select', function (e) {
    var sub = document.querySelector("#sub_cont");
    sub.hidden = false;
    if (window.search_type == "code") {
        window.term = e.params.data["id"];
    }
    else if (window.search_type == "name") {
        window.term = e.params.data["text"];
    }
    alert(window.term);
});


// Project JavaScript
function search_term(lists, n) {
    window.lists = lists;
    window.term = "";
    window.search_type = "";
    var sel = document.querySelector("#s2_cont");
    var sub = document.querySelector("#sub_cont");
    sel.hidden = true;
    sub.hidden = true;
    var subj = document.querySelector("#subjects").querySelectorAll("button");
    if (n == 0) {
        subj[0].innerHTML = "Drug";
    }
    else if (n == 1) {
        subj[0].innerHTML = "Manufacturer";
    }
    else if (n == 2) {
        subj[0].innerHTML = "Ingredient";
    }
    if (document.querySelector("#searchby") != null) {
        var prev = document.querySelector("#searchby");
        prev.parentNode.removeChild(prev);
    }
    var subjs = document.querySelector("#subjects");
    var div = document.createElement("DIV");
    div.setAttribute("id", "searchby");
    div.setAttribute("class", "dropdown");
    var btn = document.createElement("BUTTON");
    btn.setAttribute("class", "dropbtn");
    btn.innerHTML = "Search by";
    div2 = document.createElement("DIV");
    div2.setAttribute("class", "dropdown-content");
    var a1 = document.createElement("A");
    var str = ""
    var c;
    var nstr = n.toString()
    a1.setAttribute("class", "type");
    if (n == 0) {
        window.search_type = "code";
        a1.innerHTML = "Drug name";
        c = 1;
        cstr = c.toString()
        next_func = str.concat("get_dropdown(", nstr, ", ", cstr, ")")
        a1.setAttribute("onclick", next_func);
    }
    else if (n == 1) {
        window.search_type = "code";
        a1.innerHTML = "Manufacturer name";
        c = 1;
        cstr = c.toString()
        next_func = str.concat("get_dropdown(", nstr, ", ", cstr, ")")
        a1.setAttribute("onclick", next_func);
    }
    else if (n == 2) {
        window.search_type = "name";
        a1.innerHTML = "Ingredient name";
        c = 1;
        cstr = c.toString()
        next_func = str.concat("get_dropdown(", nstr, ", ", cstr, ")")
        a1.setAttribute("onclick", next_func);
    }
    div2.appendChild(a1)
    div.appendChild(btn)
    div.appendChild(div2)
    var a2;
    if (n == 0 || n == 1) {
        a2 = document.createElement("A");
        a2.setAttribute("class", "type");
        if (n == 0) {
            a2.innerHTML = "DIN";
            c = 2;
            cstr = c.toString()
            next_func = str.concat("get_dropdown(", nstr, ", ", cstr, ")")
            a2.setAttribute("onclick", next_func);
        }
        else if (n == 1) {
            a2.innerHTML = "Company code";
            c = 2;
            cstr = c.toString()
            next_func = str.concat("get_dropdown(", nstr, ", ", cstr, ")")
            a2.setAttribute("onclick", next_func);
        }
        div2.appendChild(a2);
    }
    subjs.parentNode.appendChild(div);
    return;
}

function get_dropdown(n, c) {
    var sby = document.querySelector("#searchby").querySelectorAll("button");
    if (c == 1) {
        sby[0].innerHTML = "Name";
    }
    else if (c == 2) {
        if (n == 0) {
            sby[0].innerHTML = "DIN";
        }
        else {
            sby[0].innerHTML = "Code";
        }
    }
    var sel = document.querySelector("#s2");
    sel.innerHTML = "";
    window.term = "";
    var sub = document.querySelector("#sub_cont");
    var sel_cont = document.querySelector("#s2_cont");
    sel_cont.hidden = true;
    sub.hidden = true;
    populate_dropdowns(n, c);
}

function populate_dropdowns(n, c) {
    var list = lists[n];
    var sel = document.querySelector("#s2");
    var sel_cont = document.querySelector("#s2_cont");
    sel.innerHTML = "<option></option>"
    var l = list.length;
    if (c == 1) {
        for (let i = 0; i < l; i++) {
            option = document.createElement("OPTION");
            option.innerHTML = list[i]["name"];
            option.setAttribute('value', list[i]["code"]);
            sel.appendChild(option);
        }
    }
    else if (c == 2) {
        for (let i = 0; i < l; i++) {
            option = document.createElement("OPTION");
            option.innerHTML = list[i]["code"];
            option.setAttribute('value', list[i]["code"]);
            sel.appendChild(option);
        }
    }
    sel_cont.hidden = false;
    return;
}
