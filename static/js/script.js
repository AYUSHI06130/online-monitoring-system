// =======================================================
// Browser Activity Monitoring
// =======================================================

// -----------------------------------------
// Monitoring Variables
// -----------------------------------------

let browserStatus = "Browser Active";
let focusLossCount = 0;
let lastFocusLossTime = "--";

// =======================================================
// Update Browser Information on Dashboard
// =======================================================

function updateBrowserInformation() {

    const browserStatusElement =
        document.getElementById("browser-status");

    const focusCountElement =
        document.getElementById("focus-count");

    const lastFocusElement =
        document.getElementById("last-focus-time");

    if (browserStatusElement) {

        browserStatusElement.innerText = browserStatus;

    }

    if (focusCountElement) {

        focusCountElement.innerText = focusLossCount;

    }

    if (lastFocusElement) {

        lastFocusElement.innerText = lastFocusLossTime;

    }

}

// =======================================================
// Browser Lost Focus
// =======================================================

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

// =======================================================
// Browser Focus Regained
// =======================================================

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

            event_type: "Browser Focus Regained",

            remarks:
                "Candidate returned to exam window"

        })

    });

});

// =======================================================
// Current Date & Time
// =======================================================

function updateCurrentTime() {

    const currentTimeElement =
        document.getElementById("current-time");

    if (currentTimeElement) {

        currentTimeElement.innerText =
            new Date().toLocaleString();

    }

}

// =======================================================
// Session Timer
// =======================================================

let sessionSeconds = 0;

function updateSessionTimer() {

    sessionSeconds++;

    let hours =
        Math.floor(sessionSeconds / 3600);

    let minutes =
        Math.floor((sessionSeconds % 3600) / 60);

    let seconds =
        sessionSeconds % 60;

    const timerElement =
        document.getElementById("session-timer");

    if (timerElement) {

        timerElement.innerText =

            String(hours).padStart(2, "0") + ":" +

            String(minutes).padStart(2, "0") + ":" +

            String(seconds).padStart(2, "0");

    }

}

// =======================================================
// Initialize Dashboard
// =======================================================

updateBrowserInformation();

updateCurrentTime();

updateSessionTimer();

// =======================================================
// Start Automatic Updates
// =======================================================

setInterval(updateCurrentTime, 1000);

setInterval(updateSessionTimer, 1000);

// ======================================
// Update Face Monitoring Information
// ======================================

function updateFaceMonitoring() {

    fetch("/get_monitoring_status")

        .then(response => response.json())

        .then(data => {

            document.getElementById("face-status").innerText =
                data.face_status;

            document.getElementById("absence-count").innerText =
                data.face_absence_count;

        })

        .catch(error => {

            console.log(error);

        });

}

setInterval(updateFaceMonitoring, 1000);

updateFaceMonitoring();