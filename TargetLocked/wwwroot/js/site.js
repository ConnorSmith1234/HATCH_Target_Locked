// Please see documentation at https://docs.microsoft.com/aspnet/core/client-side/bundling-and-minification
// for details on configuring this project to bundle and minify static web assets.

// Write your JavaScript code.

let list, searchBox;
let searchData = [];

$(function () {
    searchBox = $("#searchBox").dxSelectBox({
        dataSource: [
            "HD Video Player",
            "SuperHD Video Player",
            "SuperPlasma 50",
            "SuperLED 50",
            "SuperLED 42",
            "SuperLCD 55",
            "SuperLCD 42",
            "SuperPlasma 65",
            "SuperLCD 70",
            "Projector Plus",
            "Projector PlusHT",
            "ExcelRemote IR",
            "ExcelRemote BT",
            "ExcelRemote IP"
        ],
        width: "100%",
        displayExpr: null,
        searchEnabled: true,
        showDropDownButton: false,
        minSearchLength: 3,
        acceptCustomValue: true,
        onKeyDown: function (e) {
            if (e.event.key == "Enter") {
                sendSearch();
            }
        }
    }).dxSelectBox("instance");
    $("#searchIcon").dxButton({
        icon: "search",
        text: "Search",
        onClick: function () {
            sendSearch();
        }
    });
    list = $("#responseList").dxList({
        dataSource: searchData,
        visible: false,
        height: "100%",
        width: "100%",
        itemTemplate: function (data, index) {
            let titleString = $("<div>").addClass("titleLink").html(data.title);
            let authorsList = $("<div>").addClass("authors").html(data.authors.join(", "));
            let synopsis;
            if (data.abstract.length > 260) {
                synopsis = data.abstract.substring(0, 260) + " ...";
            } else {
                synopsis = data.abstract;
            }
            let summary = $("<div>").addClass("abstract").html(synopsis);
            let citedBy = $("<div>").addClass("citations").html("Citations: 1000"); //+ data.)
            console.log(data);
            return $("<div>").addClass("container-fluid").append(titleString).append(authorsList).append(summary).append(citedBy);
        }
    }).dxList("instance");
});

function sendSearch() {
    let data = JSON.stringify({ QueryString: searchBox.option("value") });
    $.ajax({
        url: "/Home/Search",
        type: "POST",
        data: data,
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (result) {
            searchData = result;
            list.option("dataSource", searchData);
            list.reload();
            list.option("visible", true);
            console.log("success");
        },
        error: function () {
            console.log("error");
        }
    });
}
