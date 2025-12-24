// Background script for Quick Sidebar Pro
chrome.action.onClicked.addListener((tab) => {
    // We can add a message here if we want to toggle the sidebar visibility via the icon
    chrome.tabs.sendMessage(tab.id, { action: "toggle_sidebar" }).catch(err => {
        console.log("Cannot send message to this tab (likely a chrome:// page)");
    });
});
