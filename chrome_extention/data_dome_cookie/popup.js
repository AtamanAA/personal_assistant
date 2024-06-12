// popup.js

document.addEventListener('DOMContentLoaded', function() {
    var extractButton = document.getElementById('extractButton');
    extractButton.addEventListener('click', function() {
        // Extract the cookie
        chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
            if (tabs[0]) { // Check if tabs[0] exists
                chrome.cookies.get({ url: tabs[0].url, name: "datadome" }, function(cookie) {
                    if (cookie) {
                        chrome.storage.local.set({ 'datadome_cookie': cookie.value }, function() {
                            chrome.storage.local.get('datadome_cookie', function(result) {
                                if (result.datadome_cookie) {
                                    // alert('Cookie value saved locally:\n' + result.datadome_cookie);
                                    console.log('Cookie value saved locally:', result.datadome_cookie);

                                    // Get the current IP address
                                    fetch('https://httpbin.org/ip')
                                        .then(response => response.json())
                                        .then(data => {
                                            var ip_check = data.origin;
                                            console.log('Current IP:', ip_check);
                                            // alert('IP check:\n' + ip_check);

                                            // Now make the POST request
                                            fetch('http://167.172.189.14:8004/api/v1/uefa/sessions', {
                                                method: 'POST',
                                                headers: {
                                                    'Content-Type': 'application/json'
                                                },
                                                body: JSON.stringify({
                                                    proxy: null,
                                                    ip: ip_check,
                                                    data_dome_cookie: cookie.value
                                                })
                                            })
                                            .then(response => response.json())
                                            .then(data => alert(data + "\nIP:" + ip_check + "\nData dome cookie:\n" + result.datadome_cookie ))
                                            .catch(error => alert(error));
                                        })
                                        .catch(error => console.error('Error fetching IP:', error));
                                } else {
                                    console.error('Failed to retrieve the stored cookie value.');
                                }
                            });
                        });
                    } else {
                        console.error("No 'datadome' cookie found.");
                    }
                });
            } else {
                console.error("No active tab found.");
            }
        });
    });
});
