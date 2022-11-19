// Get the parent matching a selector of a given element.
function getParents(elem, selector) {
    // Element.matches() polyfill
    if (!Element.prototype.matches) {
        Element.prototype.matches =
            Element.prototype.matchesSelector ||
            Element.prototype.mozMatchesSelector ||
            Element.prototype.msMatchesSelector ||
            Element.prototype.oMatchesSelector ||
            Element.prototype.webkitMatchesSelector ||
            function(s) {
                var matches = (this.document || this.ownerDocument).querySelectorAll(s),
                    i = matches.length;
                while (--i >= 0 && matches.item(i) !== this) {}
                return i > -1;
            };
    }

    // Set up a parent array
    var parents = [];

    // Push each parent element to the array
    for ( ; elem && elem !== document; elem = elem.parentNode ) {
        if (selector) {
            if (elem.matches(selector)) {
                parents.push(elem);
            }
            continue;
        }
        parents.push(elem);
    }

    // Return our parent array
    return parents;
};

// Update the anchor link if the anchor is inside a tab
// The updated link will create a query string with the name of the tab.
function tabDeepLink(){
    var anchorCollection = document.getElementsByClassName("anchor-link");

    if(anchorCollection.length == 0){
        return
    }

    for (let i = 0; i < anchorCollection.length; i++) {

        anchor = anchorCollection[i];
        parentTab = getParents(anchor, ".tab-pane")


        // If the anchor is inside a tab, update the link
        if(parentTab.length == 1){
            tabID = parentTab[0].id.replace("-pane", "");

            link = '?tab=' + tabID + '#' + anchor.id;
            anchor.setAttribute('href', link);
        }
    }
}

// Click the tab found in the query string to make it active.
function openTab(){
    var urlParams = new URLSearchParams(window.location.search);
    if(urlParams.get('tab')){
        document.getElementById(urlParams.get('tab')).click();
    }
    //document.getElementById('tab-367').click();
}


window.onload = tabDeepLink();
window.onload = openTab();