document.getElementById("examSearch").addEventListener('input', ev => {
    const MAX_RESULTS = 10;
    let inputValue = ev.target.value
    let searchResults = document.getElementById("searchResults")
    searchResults.style.visibility = inputValue ? "visible" : "hidden";
    let cnt = 0
    for (const child of searchResults.children) {
        child.style.display = inputValue && child.firstChild.textContent.includes(inputValue) && ++cnt <= MAX_RESULTS ? "block" : "none";
    }
})