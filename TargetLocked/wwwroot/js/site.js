// Please see documentation at https://docs.microsoft.com/aspnet/core/client-side/bundling-and-minification
// for details on configuring this project to bundle and minify static web assets.

// Write your JavaScript code.

let urlLookup = [{
    "siteName": "MedArchive",
    "URL": "https://www.medrxiv.org/",
}, {
    "siteName": "BioArchive",
    "URL": "https://www.biorxiv.org/"
}];

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
        focusStateEnabled: false,
        activeStateEnabled: false,
        height: "100%",
        width: "100%",
        itemTemplate: function (data, index) {
            let url = data.url.indexOf("http") != 0 ? "https://" + data.url : data.url;
            let titleString = $("<a>").addClass("titleLink").addClass("w-auto").html(data.title).attr("href", url).attr("target", "_blank");
            let apiSite = $("<a>").addClass("api").html("Source: " + data.api).attr("href", urlLookup.filter(x => x.siteName == data.api)[0].URL).attr("target", "_blank");
            let titleDiv = $("<div>").addClass("d-flex").append(titleString).append(apiSite);
            let authorsList = $("<div>").addClass("authors").html(data.authors ? (data.authors.length > 4 ? data.authors.slice(0, 4).join(", ") + ", et al." : data.authors.join(", ")) : "No authors found");
            let synopsis;
            if (data.abstract.length > 260) {
                synopsis = data.abstract.substring(0, 260) + " ...";
            } else {
                synopsis = data.abstract;
            }
            let summary = $("<div>").addClass("abstract").html(synopsis);
            console.log(data);
            return $("<div>").addClass("container-fluid").append(titleDiv).append(authorsList).append(summary);
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
        },
        error: function () {
            console.log("boneless");
        }
    });
}

function displaySidebar() {
    if (firstSearchFlag) {
        firstSearchFlag = false;
        let dateList = searchData.map(a => a.date_seconds);
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
                    beforeDatePicker.option("value", afterDatePicker.option("value"));
                    afterDatePicker.option("visible", false);
                }
                else if (e.value == "After") {
                    beforeDatePicker.option("visible", false);
                    afterDatePicker.option("visible", true);
                    afterDatePicker.option("value", beforeDatePicker.option("value"));
                }
                else {
                    beforeDatePicker.option("visible", true);
                    afterDatePicker.option("visible", true);
                }
                handleFilterChange();
            }
        });
        let authorsList = searchData.map(a => a.authors).join().split(",");
        let authorsCount = [];
        authorsList.forEach(function (i) {
            if (i.length == 0) {
                return true;
            }
            if (authorsCount.some(x => x.Name == i)) {
                authorsCount.filter(x => x.Name == i)[0].Count++;
            }
            else {
                authorsCount.push({ "Name": i, "Count": 1 });
            }
        });
        let authorsHeight = authorsCount.length > 3 ? 185 : null;
        $("#authorsFilter").dxList({
            items: authorsCount,
            height: authorsHeight,
            itemTemplate: function (data) {
                return $("<div>").html(data.Name + " (" + data.Count + ")");
            },
            onSelectionChanged: function () {
                handleFilterChange();
            },
            selectionMode: "all",
            showSelectionControls: true
        });
        let speciesList = searchData.map(a => a.species).join().split(",");
        let speciesCount = [];
        speciesList.forEach(function (i) {
            if (i.length == 0) {
                return true;
            }
            if (speciesCount.some(x => x.Name == i)) {
                speciesCount.filter(x => x.Name == i)[0].Count++;
            }
            else {
                speciesCount.push({ "Name": i, "Count": 1 });
            }
        });
        let speciesHeight = speciesCount.length > 3 ? 185 : null;
        $("#speciesFilter").dxList({
            items: speciesCount,
            height: speciesHeight,
            itemTemplate: function (data) {
                return $("<div>").html(data.Name + " (" + data.Count + ")");
            },
            onSelectionChanged: function () {
                handleFilterChange();
            },
            selectionMode: "all",
            showSelectionControls: true
        });
        let diseaseList = searchData.map(a => a.diseases);
        let diseaseCount = [];
        let masterDiseaseList = [];
        diseaseList.forEach(function (i) {
            masterDiseaseList.push(i.map(x => x.disease));
        });
        masterDiseaseList = [].concat.apply([], masterDiseaseList);
        masterDiseaseList.forEach(function (i) {
            if (i.length == 0) {
                return true;
            }
            if (diseaseCount.some(x => x.Name == i)) {
                diseaseCount.filter(x => x.Name == i)[0].Count++;
            }
            else {
                diseaseCount.push({ "Name": i, "Count": 1 });
            }
        });
        let diseaseHeight = diseaseCount.length > 3 ? 185 : null;
        $("#diseaseFilter").dxList({
            items: diseaseCount,
            height: diseaseHeight,
            itemTemplate: function (data) {
                return $("<div>").html(data.Name + " (" + data.Count + ")");
            },
            onSelectionChanged: function () {
                handleFilterChange();
            },
            selectionMode: "all",
            showSelectionControls: true,
        });
        handleCollapse();
        $("#filterSidebar").addClass("active");
    }
}

function setupDates(start, end) {
    let startDate = new Date(start);
    let endDate = new Date(end);
    afterDatePicker = $("#afterDate").dxDateBox({
        type: "date",
        placeholder: "Start",
        value: startDate,
        min: startDate,
        max: endDate,
        onValueChanged: function () {
            handleFilterChange();
        }
    }).dxDateBox("instance");
    beforeDatePicker = $("#beforeDate").dxDateBox({
        type: "date",
        placeholder: "End",
        visible: false,
        value: endDate,
        min: startDate,
        max: endDate,
        onValueChanged: function () {
            handleFilterChange();
        }
    }).dxDateBox("instance");
}

function handleCollapse() {
    $(".collapseIcon").click(function () {
        if ($(this).hasClass("dx-icon-chevronup")) {
            let thisString = $(this).attr("id").substring(0, $(this).attr("id").indexOf("Collapse"));
            $("#" + thisString + "Filter").dxList("instance").option("visible", false);
            $(this).removeClass("dx-icon-chevronup").addClass("dx-icon-chevrondown");
        }
        else {
            let thisString = $(this).attr("id").substring(0, $(this).attr("id").indexOf("Collapse"));
            $("#" + thisString + "Filter").dxList("instance").option("visible", true);
            $(this).removeClass("dx-icon-chevrondown").addClass("dx-icon-chevronup");
        }
    });
}

function handleFilterChange() {
    let authorsSelection = $("#authorsFilter").dxList("instance").option("selectedItems").map(x => x.Name);
    let speciesSelection = $("#speciesFilter").dxList("instance").option("selectedItems").map(x => x.Name);
    let diseaseSelection = $("#diseaseFilter").dxList("instance").option("selectedItems").map(x => x.Name);
    let beforeSelection = new Date(new Date($("#beforeDate").dxDateBox("instance").option().value).toDateString());
    let afterSelection = new Date(new Date($("#afterDate").dxDateBox("instance").option().value).toDateString());
    beforeSelection = new Date(beforeSelection.getTime() + (60 * 60 * 24 * 1000));
    let dateDropdownSelection = $("#dateDropdownButton").dxSelectBox("instance").option().value;
    let filteredData = speciesSelection.length != 0 ? searchData.filter(x => x.species.some(y => speciesSelection.includes(y))) : searchData;
    filteredData = diseaseSelection.length != 0 ? filteredData.filter(x => x.diseases.some(y => diseaseSelection.includes(y))) : filteredData;
    filteredData = authorsSelection.length != 0 ? filteredData.filter(function (x) {
        if (!x.authors) {
            return false;
        }
        return x.authors.some(y => authorsSelection.includes(y))
    }) : filteredData;
    filteredData = filteredData.filter(function (x) {
        let thisDate = new Date(x.date * 1000);
        if (thisDate > beforeSelection && (dateDropdownSelection == "Before" || dateDropdownSelection == "Between")) {
            return false;
        }
        if (thisDate < afterSelection && (dateDropdownSelection == "After" || dateDropdownSelection == "Between")) {
            return false;
        }
        return true;
    })
    list.option("dataSource", filteredData);
    list.reload();

}