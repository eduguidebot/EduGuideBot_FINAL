/**
 * EduGuideBot - Results JavaScript file
 * Loads and displays user profile and university recommendations
 */

// Main initialization function
document.addEventListener('DOMContentLoaded', function() {
    // Get the result ID from URL parameters
    const resultId = getResultIdFromUrl();
    
    if (resultId) {
        loadResultData(resultId);
    } else {
        showError('No result ID found in the URL. Please start from the Telegram bot.');
    }
    
    // Update the bot link with actual username
    updateBotLink();
});

/**
 * Get the result ID from URL parameters
 */
function getResultIdFromUrl() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('id');
}

/**
 * Update Telegram bot link with actual username
 */
function updateBotLink() {
    const botLink = document.querySelector('a[href^="https://t.me/"]');
    const botUsername = urlParams.get('bot') || 'your_bot_username';
    
    if (botLink && botUsername) {
        botLink.href = `https://t.me/${botUsername}`;
    }
}

/**
 * Load result data from server
 */
function loadResultData(resultId) {
    // In a real implementation, this would be an API call
    // For this example, we'll use a static JSON file simulating the data
    fetch(`../data/result_${resultId}.json`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Result not found');
            }
            return response.json();
        })
        .then(data => {
            displayUserProfile(data.user_profile);
            displayRecommendations(data.recommendations);
        })
        .catch(error => {
            showError(`Error loading recommendations: ${error.message}`);
        });
}

/**
 * Display user profile information
 */
function displayUserProfile(profile) {
    const profileContainer = document.getElementById('user-profile');
    
    if (!profile) {
        profileContainer.innerHTML = '<p>Profile information not available.</p>';
        return;
    }
    
    // Create profile HTML
    let profileHtml = '';
    
    // Location
    profileHtml += `
        <div class="info-item">
            <span class="label">Location:</span>
            <span>${profile.location}</span>
        </div>
    `;
    
    // Budget
    profileHtml += `
        <div class="info-item">
            <span class="label">Maximum Budget:</span>
            <span>$${profile.max_budget} / year</span>
        </div>
    `;
    
    // Major Field
    profileHtml += `
        <div class="info-item">
            <span class="label">Field of Study:</span>
            <span class="khmer">${profile.core_field}</span>
        </div>
    `;
    
    // Career Goal
    profileHtml += `
        <div class="info-item">
            <span class="label">Career Goal:</span>
            <span class="khmer">${profile.career_goal}</span>
        </div>
    `;
    
    // English Proficiency
    profileHtml += `
        <div class="info-item">
            <span class="label">English Proficiency:</span>
            <span>${profile.english_proficiency}/10</span>
        </div>
    `;
    
    profileContainer.innerHTML = profileHtml;
}

/**
 * Display university recommendations
 */
function displayRecommendations(recommendations) {
    const listContainer = document.getElementById('university-list');
    
    if (!recommendations || recommendations.length === 0) {
        listContainer.innerHTML = '<p>No recommendations found based on your profile.</p>';
        return;
    }
    
    // Clear loading message
    listContainer.innerHTML = '';
    
    // Create a card for each recommended university
    recommendations.forEach(recommendation => {
        const university = recommendation.university;
        const score = recommendation.total_score;
        // Calculate percentage (assuming max score is 100)
        const percentage = Math.min(Math.round(score), 100);
        
        // Create university card HTML
        const card = document.createElement('div');
        card.className = 'university-card';
        
        card.innerHTML = `
            <div class="card-header">
                <h2 class="khmer">${university.name_km}</h2>
                <div class="university-type">
                    ${university.type} • Established ${university.established_year} • ${university.location}
                </div>
            </div>
            <div class="card-body">
                <div class="card-info">
                    <p><span class="label">English Name:</span> ${university.name_en}</p>
                    <p><span class="label">Tuition Range:</span> $${university.tuition_fees.range_min} - $${university.tuition_fees.range_max} / year</p>
                    <p><span class="label">Total Majors:</span> ${university.total_majors || 'N/A'}</p>
                </div>
                <div class="match-score">
                    <div class="match-bar">
                        <div class="match-bar-fill" style="width: ${percentage}%"></div>
                    </div>
                    <div class="percentage">${percentage}%</div>
                </div>
                <div class="card-actions">
                    <a href="#" class="button button-primary" onclick="viewDetails('${university.id}')">View Details</a>
                </div>
            </div>
        `;
        
        listContainer.appendChild(card);
    });
}

/**
 * Show an error message
 */
function showError(message) {
    const sections = document.querySelectorAll('section');
    sections.forEach(section => {
        section.innerHTML = `<div class="error-message"><p>${message}</p>
            <a href="https://t.me/your_bot_username" class="button button-primary">Return to Telegram Bot</a>
        </div>`;
    });
}

/**
 * View details for a specific university (placeholder function)
 */
function viewDetails(universityId) {
    alert('Detail view not implemented in this demo. University ID: ' + universityId);
    // In a real implementation, this would redirect to a detail page
    // window.location.href = `detail.html?id=${universityId}&result=${getResultIdFromUrl()}`;
} 