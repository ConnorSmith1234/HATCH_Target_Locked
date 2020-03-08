// Please see documentation at https://docs.microsoft.com/aspnet/core/client-side/bundling-and-minification
// for details on configuring this project to bundle and minify static web assets.

// Write your JavaScript code.

let list, searchBox;
let firstSearchFlag = true;
let searchData = [];
let speciesParams = [], diseaseParams = [];
let minCitation, maxCitation;
let earliestDate, latestDate;

let beforeDatePicker, afterDatePicker;

$(function () {
    searchBox = $("#searchBox").dxAutocomplete({
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
        minSearchLength: 3,
        placeholder: "Search...",
        onKeyDown: function (e) {
            if (e.event.key == "Enter") {
                sendSearch();
            }
        }
    }).dxAutocomplete("instance");
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
            displaySidebar();
            console.log("success");
        },
        error: function () {
            console.log("error");
        }
    });
}

function displaySidebar() {
    if (firstSearchFlag) {
        firstSearchFlag = false;
        let dateList = searchData.map(a => a.date);
        earliestDate = Math.min(...dateList);
        latestDate = Math.max(...dateList);
        setupDates(earliestDate, latestDate);
        $("#dateDropdownButton").dxSelectBox({
            height: 36,
            items: ["Before", "After", "Between"],
            value: "After",
            onValueChanged: function (e) {
                if (e.value == "Before") {
                    beforeDatePicker.option("visible", true);
                    afterDatePicker.option("visible", false);
                }
                else if (e.value == "After") {
                    beforeDatePicker.option("visible", false);
                    afterDatePicker.option("visible", true);
                }
                else {
                    beforeDatePicker.option("visible", true);
                    afterDatePicker.option("visible", true);
                }
            }
        });
        let citationList = [100, 1000];
        $("#citationFilter").dxRangeSlider({
            min: Math.min(...citationList),
            max: Math.max(...citationList),
            start: Math.min(...citationList),
            end: Math.max(...citationList),
            tooltip: {
                enabled: true,
                format: function (value) {
                    return value;
                },
                showMode: "always",
                position: "bottom"
            }
        });
        let speciesList = searchData.map(a => a.species)[0];
        $("#speciesFilter").dxList({
            items: speciesList,
            selectionMode: "all",
            showSelectionControls: true
        });
        let diseaseList = searchData.map(a => a.diseases)[0];
        $("#diseaseFilter").dxList({
            items: diseaseList,
            selectionMode: "all",
            showSelectionControls: true
        })
        $("#filterSidebar").addClass("active");
        console.log(dateList);
    }
}

function setupDates(start, end) {
    let startDate = new Date(1970, 0, 1);
    startDate.setSeconds(startDate.getSeconds() + start);
    let endDate = new Date(1970, 0, 1);
    endDate.setSeconds(endDate.getSeconds() + end);
    afterDatePicker = $("#afterDate").dxDateBox({
        type: "date",
        placeholder: "Start",
        min: startDate,
        max: endDate
    }).dxDateBox("instance");
    beforeDatePicker = $("#beforeDate").dxDateBox({
        type: "date",
        placeholder: "End",
        visible: false,
        min: startDate,
        max: endDate
    }).dxDateBox("instance");
}
