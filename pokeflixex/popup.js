// Find the button in our popup.html
const copyButton = document.getElementById('copyButton');

// This function will be executed ON THE WEBPAGE. 
// It finds the URL, then finds text from CSS selectors, and combines them.
function findAndCombineData() {
    // --- START OF CONFIGURATION ---
    const urlRegex = /https?:\/\/[^\s"'<>]+?playlist\.m3u8/;
    
    // Selector for the main element containing both values
    const mainSelector = 'div.page-header > h2'; 

    // --- END OF CONFIGURATION ---

    const allValues = ["script.py"];

    // 1. Find the URL (same as before)
    const scripts = document.querySelectorAll('script');
    for (const script of scripts) {
        const match = script.textContent.match(urlRegex);
        if (match) {
            allValues.push(`"${match[0]}"`);
            break;
        }
    }

    // 2. Find the complex text values
    const mainElement = document.querySelector(mainSelector);
    if (mainElement) {
        // To get "Value 1" only, we clone the element and remove the child part
        const clone = mainElement.cloneNode(true);
        const childToRemove = clone.querySelector('p'); // Find the <p> inside the clone
        if (childToRemove) {
            clone.removeChild(childToRemove);
        }
        const value1 = clone.innerText.trim();
        if (value1) {
            allValues.push(`"${value1}"`);
        }

        // To get "Value 2", we select it directly
        const value2Element = mainElement.querySelector('small');
        if (value2Element) {
            const value2 = value2Element.innerText.trim();
            if (value2) {
                allValues.push(`"${value2}"`);
            }
        }
    }

    if (allValues.length > 0) {
        return allValues.join(' ');
    }
    
    return null;
}

// Add a click event listener to the button
copyButton.addEventListener('click', async () => {
    let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    chrome.scripting.executeScript({
        target: { tabId: tab.id },
        function: findAndCombineData,
    }, (injectionResults) => {
        if (chrome.runtime.lastError) {
            console.error(chrome.runtime.lastError.message);
            copyButton.textContent = 'Error!';
            return;
        }

        const finalString = injectionResults[0].result;

        if (finalString) {
            // Copy the final combined string to the clipboard
            navigator.clipboard.writeText(finalString).then(() => {
                console.log('Copied:', finalString);
                copyButton.textContent = 'Copied!';
            }).catch(err => {
                console.error('Failed to copy:', err);
                copyButton.textContent = 'Copy Failed';
            });
        } else {
            console.log('No values were found on the page.');
            copyButton.textContent = 'Not Found';
        }

        // Reset button text after a moment
        setTimeout(() => { copyButton.textContent = 'Copy Value'; }, 2000);
    });
});
