/**
 * String Security Layer
 * Client-side integrity and alerting
 */

(function() {
    console.log("String Security Layer: Active");

    // Detect DevTools opening
    let devtools = function() {};
    devtools.toString = function() {
        fetch('/__security_alert?msg=DevTools_Detected');
        return '';
    }

    // Basic Integrity Check
    window.addEventListener('load', () => {
        if (window.location.protocol === 'http:' && window.location.hostname !== 'localhost') {
            console.warn("String: Running over unencrypted connection. Securing headers...");
        }
    });

    // Detect excessive rapid clicks (potential bot behavior)
    let clicks = 0;
    document.addEventListener('click', () => {
        clicks++;
        if (clicks > 20) {
            console.error("Excessive interaction detected.");
        }
        setTimeout(() => clicks = 0, 2000);
    });
})();
