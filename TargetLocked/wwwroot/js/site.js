// Please see documentation at https://docs.microsoft.com/aspnet/core/client-side/bundling-and-minification
// for details on configuring this project to bundle and minify static web assets.

// Write your JavaScript code.

$(function () {
    var searchBox = $("#searchBox").dxSelectBox({
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
        onValueChanged: function (e) {
            console.log(e);
        }
    }).dxSelectBox("instance");
    $("#searchIcon").dxButton({
        icon: "search",
        text: "Search",
        onClick: function () {
            let data = JSON.stringify({ QueryString: searchBox.option("value") });
            $.ajax({
                url: "/Home/Search",
                type: "POST",
                data: data,
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                success: function () {
                    console.log("success");
                },
                error: function () {
                    console.log("error");
                }
            });
        }
    });
    var list = $("#responseList").dxList({

    }).dxList("instance");
});
