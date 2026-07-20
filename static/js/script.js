
// ======================================
// Browser Monitoring Variables
// ======================================

let browserStatus = "Browser Active";

let focusLossCount = 0;

let lastFocusLossTime = "--";

// browser lost focus

window.addEventListener("blur", function () {

    browserStatus = "Browser Inactive";

    focusLossCount++;

    lastFocusLossTime =
        new Date().toLocaleTimeString();

    updateBrowserInformation();

    console.log(browserStatus);

    fetch("/log_browser_event", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({

            event_type: "Browser Focus Lost",

            remarks:
                "Candidate switched away from exam window"

        })

    });

});

// ======================================
// Browser Focus Regained
// ======================================

window.addEventListener("focus", function () {

    browserStatus = "Browser Active";

    updateBrowserInformation();

    console.log(browserStatus);

    fetch("/log_browser_event", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({

            event_type:
                "Browser Focus Regained",

            remarks:
                "Candidate returned to exam window"

        })

    });

});

// ======================================
// Update Browser Information
// ======================================

function updateBrowserInformation() {

    document.getElementById("browser-status").innerText =
        browserStatus;

    document.getElementById("focus-count").innerText =
        focusLossCount;

    document.getElementById("last-focus-time").innerText =
        lastFocusLossTime;

}

updateBrowserInformation();