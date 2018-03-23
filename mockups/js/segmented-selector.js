function SegmentedSelector (element, listener) {
    if (!element) {
        console.error("Segmented selector created with invalid root element");
        return;
    }

    var input = element.querySelector("input");

    var onValueSelected = function (selected) {
        var active = element.querySelector("a.active");

        var currentKey = active.getAttribute("data-selector-key");
        var selectedKey = selected.getAttribute("data-selector-key");
        
        var selectedValue = selected.getAttribute("data-selector-value");
        input.value = selectedValue;

        active.className = "inactive";
        selected.className = "active";

        if (listener) {
            listener(currentKey, selectedKey);
        }
    };

    // init event if there's a default value, eg hitting back after filling the form
    // the fields will have values and the UI needs to reflect that
    // TODO: check this is still useful when the app is implemented server-side. This will be unused if the page is rerendered
    //       by the server in such cases.
    if (input.value) {
        var selected = element.querySelector("a[data-selector-value='" + input.value + "']");
        onValueSelected(selected);
    } else {
        var visuallyActive = element.querySelector("a.active");
        if (visuallyActive) {
            onValueSelected(visuallyActive);
        } else {
            // Shouldn't happen in the html, that'd mean the segmented selector has no possible values at all
            console.error("No default value found for SegmentedSelector: no input value, and no active links");
        }
    }

    var links = element.querySelectorAll("a");
    for (var i = 0; i < links.length; ++i) {
        var link = links[i];
        link.addEventListener("click", function (e) {
            e.preventDefault();
            onValueSelected(e.target);
        }.bind (this), false);
    }
}
