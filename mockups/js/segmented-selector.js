function SegmentedSelector (element, listener) {
    var input = element.querySelector("input");

    var onValueSelected = function (selected) {
        var active = element.querySelector("a.active");

        var currentKey = active.getAttribute("data-selector-key");
        var selectedKey = selected.getAttribute("data-selector-key");

        input.value = selectedKey;

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
        var selected = element.querySelector("a[data-selector-key='" + input.value + "']");
        onValueSelected(selected);
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
