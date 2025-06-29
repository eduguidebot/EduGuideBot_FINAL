/**
 * EduGuideBot - Main JavaScript file
 * Handles basic interactions on the main page
 */

document.addEventListener('DOMContentLoaded', function() {
    // Update bot link with actual username from environment if available
    const botLink = document.querySelector('a[href^="https://t.me/"]');
    const botUsername = getBotUsername();
    
    if (botLink && botUsername) {
        botLink.href = `https://t.me/${botUsername}`;
    }
});

/**
 * Get bot username from URL parameters or use default
 */
function getBotUsername() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('bot') || 'your_bot_username';
} 