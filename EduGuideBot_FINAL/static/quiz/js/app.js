// Initialize Telegram WebApp
const tg = window.Telegram.WebApp;
tg.expand();
tg.MainButton.hide();

// DOM elements
const budgetRange = document.getElementById('budget-range');
const budgetDisplay = document.getElementById('budget-display');
const englishRange = document.getElementById('english-range');
const englishDisplay = document.getElementById('english-display');
const fieldSelect = document.getElementById('field-select');
const submitBtn = document.getElementById('submit-quiz');
const nextButtons = document.querySelectorAll('.next-btn');
const locationNextBtn = document.querySelector('.location-next');
const fieldNextBtn = document.querySelector('.field-next');
const careerNextBtn = document.querySelector('.career-next');

// User answers object
const userAnswers = {
    location: '',
    max_budget: 1000,
    core_field: '',
    career_goal: '',
    english_proficiency: 5
};

// Update the display values for range inputs
budgetRange.addEventListener('input', () => {
    budgetDisplay.textContent = `$${budgetRange.value}`;
    userAnswers.max_budget = parseInt(budgetRange.value);
});

englishRange.addEventListener('input', () => {
    englishDisplay.textContent = englishRange.value;
    userAnswers.english_proficiency = parseInt(englishRange.value);
});

// Handle next button clicks - general step navigation
nextButtons.forEach(button => {
    button.addEventListener('click', () => {
        // Get the current and next step IDs
        const currentStep = button.closest('.quiz-step');
        const nextStepId = button.getAttribute('data-next');
        const nextStep = document.getElementById(nextStepId);
        
        // Hide current step
        currentStep.style.display = 'none';
        
        // Show next step
        nextStep.style.display = 'block';
    });
});

// Handle location selection validation
locationNextBtn.addEventListener('click', () => {
    const selectedLocation = document.querySelector('input[name="location"]:checked');
    
    if (!selectedLocation) {
        alert('សូមជ្រើសរើសទីតាំង');
        document.getElementById('step-1').style.display = 'block';
        document.getElementById('step-2').style.display = 'none';
        return;
    }
    
    userAnswers.location = selectedLocation.value;
});

// Handle field selection validation
fieldNextBtn.addEventListener('click', () => {
    if (!fieldSelect.value) {
        alert('សូមជ្រើសរើសផ្នែកសិក្សា');
        document.getElementById('step-3').style.display = 'block';
        document.getElementById('step-4').style.display = 'none';
        return;
    }
    
    userAnswers.core_field = fieldSelect.value;
});

// Handle career goal validation
careerNextBtn.addEventListener('click', () => {
    const selectedCareer = document.querySelector('input[name="career"]:checked');
    
    if (!selectedCareer) {
        alert('សូមជ្រើសរើសគោលដៅអាជីព');
        document.getElementById('step-4').style.display = 'block';
        document.getElementById('step-5').style.display = 'none';
        return;
    }
    
    userAnswers.career_goal = selectedCareer.value;
});

// Handle form submission
submitBtn.addEventListener('click', () => {
    // Show loading screen
    document.getElementById('step-5').style.display = 'none';
    document.getElementById('step-loading').style.display = 'block';
    
    // Final validation
    if (!userAnswers.location || !userAnswers.core_field || !userAnswers.career_goal) {
        alert('សូមបំពេញព័ត៌មានទាំងអស់');
        document.getElementById('step-5').style.display = 'block';
        document.getElementById('step-loading').style.display = 'none';
        return;
    }
    
    // Send data to Telegram app
    setTimeout(() => {
        tg.sendData(JSON.stringify({
            action: 'university_recommendations',
            user_profile: userAnswers
        }));
    }, 1500); // Artificial delay for loading effect
}); 