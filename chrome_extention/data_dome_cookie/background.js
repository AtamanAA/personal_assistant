// background.js
chrome.action.onClicked.addListener(function(tab) {
    chrome.cookies.get({ url: tab.url, name: "datadome" }, function(cookie) {
        if (cookie) {
            var fileContent = "datadome cookie value: " + cookie.value;
            var blob = new Blob([fileContent], { type: 'text/plain' });
            var url = URL.createObjectURL(blob);

            chrome.downloads.download({
                url: url,
                filename: 'datadome_cookie.txt',
                saveAs: true
            }, function(downloadId) {
                if (downloadId) {
                    console.log("Cookie value saved to file.");
                    
                } else {
                    console.error("Failed to save cookie value to file.");
                }
            });
        } else {
            console.error("No 'datadome' cookie found.");
        }
    });
});
