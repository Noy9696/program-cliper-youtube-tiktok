// Check cookies on load
window.addEventListener('load', async () => {
    const response = await fetch('/check_cookies');
    const data = await response.json();
    
    if (!data.exists) {
        document.getElementById('cookieWarning').style.display = 'block';
    }
});