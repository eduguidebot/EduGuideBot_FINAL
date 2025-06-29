// Initialize Telegram WebApp
const tg = window.Telegram.WebApp;
tg.expand();
tg.MainButton.hide();

// DOM elements
const universitySelect = document.getElementById('university-select');
const majorSelect = document.getElementById('major-select');
const scholarshipsRange = document.getElementById('scholarships');
const scholarshipValue = document.getElementById('scholarship-value');
const livingExpensesRange = document.getElementById('living-expenses');
const livingValue = document.getElementById('living-value');
const yearsSelect = document.getElementById('years');
const calculateBtn = document.getElementById('calculate-btn');
const yearlyTuition = document.getElementById('yearly-tuition');
const yearlyLiving = document.getElementById('yearly-living');
const yearlyTotal = document.getElementById('yearly-total');
const totalCost = document.getElementById('total-cost');
const shareResultsBtn = document.getElementById('share-results');

// University data should be available from the injected script
const universities = window.universityData || [];

// Used to store currently selected university data
let selectedUniversity = null;
let selectedMajor = null;

// Initialize university select
function initializeUniversitySelect() {
    universities.forEach(uni => {
        const option = document.createElement('option');
        option.value = uni.id;
        option.textContent = uni.name_km || uni.name_en;
        universitySelect.appendChild(option);
    });
}

// Update major select based on selected university
function updateMajorSelect() {
    // Clear previous options
    majorSelect.innerHTML = '';
    majorSelect.disabled = true;
    
    const universityId = parseInt(universitySelect.value);
    if (!universityId) {
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = '-- ជ្រើសរើសសាកលវិទ្យាល័យមុន --';
        majorSelect.appendChild(defaultOption);
        selectedUniversity = null;
        return;
    }
    
    // Find selected university
    selectedUniversity = universities.find(uni => uni.id === universityId);
    
    if (!selectedUniversity) {
        return;
    }
    
    // Enable major select
    majorSelect.disabled = false;
    
    // Add default option
    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = '-- ជ្រើសរើសជំនាញ --';
    majorSelect.appendChild(defaultOption);
    
    // Add options for each faculty and major
    if (selectedUniversity.faculties && selectedUniversity.faculties.length > 0) {
        selectedUniversity.faculties.forEach(faculty => {
            if (faculty.majors && faculty.majors.length > 0) {
                // Create an optgroup for the faculty
                const optgroup = document.createElement('optgroup');
                optgroup.label = faculty.name_km || faculty.name_en;
                
                faculty.majors.forEach(major => {
                    const option = document.createElement('option');
                    option.value = JSON.stringify({ 
                        faculty: faculty.name_km || faculty.name_en,
                        major: major.name_km || major.name_en
                    });
                    option.textContent = major.name_km || major.name_en;
                    optgroup.appendChild(option);
                });
                
                majorSelect.appendChild(optgroup);
            }
        });
    }
}

// Update range input display values
function updateRangeDisplays() {
    scholarshipValue.textContent = `${scholarshipsRange.value}%`;
    livingValue.textContent = `$${livingExpensesRange.value}`;
}

// Calculate costs
function calculateCosts() {
    // Check if university is selected
    if (!selectedUniversity) {
        alert('សូមជ្រើសរើសសាកលវិទ្យាល័យ');
        return;
    }
    
    // Get values from form
    const scholarshipPercent = parseInt(scholarshipsRange.value);
    const monthlyLiving = parseInt(livingExpensesRange.value);
    const yearsOfStudy = parseInt(yearsSelect.value);
    
    // Get tuition range from selected university
    let tuitionMin = selectedUniversity.tuition_fees?.range_min || 0;
    let tuitionMax = selectedUniversity.tuition_fees?.range_max || 0;
    
    // Calculate average tuition
    let yearlyTuitionCost = (tuitionMin + tuitionMax) / 2;
    
    // Apply scholarship reduction
    yearlyTuitionCost = yearlyTuitionCost * (1 - scholarshipPercent / 100);
    
    // Calculate living costs (monthly * 12)
    const yearlyLivingCost = monthlyLiving * 12;
    
    // Calculate total yearly cost
    const totalYearlyCost = yearlyTuitionCost + yearlyLivingCost;
    
    // Calculate total program cost
    const totalProgramCost = totalYearlyCost * yearsOfStudy;
    
    // Update the displayed results
    yearlyTuition.textContent = `$${Math.round(yearlyTuitionCost).toLocaleString()}`;
    yearlyLiving.textContent = `$${Math.round(yearlyLivingCost).toLocaleString()}`;
    yearlyTotal.textContent = `$${Math.round(totalYearlyCost).toLocaleString()}`;
    totalCost.textContent = `$${Math.round(totalProgramCost).toLocaleString()}`;
}

// Event listeners
universitySelect.addEventListener('change', updateMajorSelect);

scholarshipsRange.addEventListener('input', updateRangeDisplays);
livingExpensesRange.addEventListener('input', updateRangeDisplays);

calculateBtn.addEventListener('click', calculateCosts);

shareResultsBtn.addEventListener('click', () => {
    if (!selectedUniversity) {
        alert('សូមជ្រើសរើសសាកលវិទ្យាល័យ និងគណនាមុន');
        return;
    }
    
    const selectedMajorText = majorSelect.options[majorSelect.selectedIndex]?.text || 'N/A';
    
    const resultData = {
        action: 'share_calculation',
        university_id: selectedUniversity.id,
        university_name: selectedUniversity.name_km || selectedUniversity.name_en,
        major: selectedMajorText,
        yearly_cost: yearlyTotal.textContent,
        total_cost: totalCost.textContent,
        years: yearsSelect.value
    };
    
    tg.sendData(JSON.stringify(resultData));
});

// Initialize the calculator
document.addEventListener('DOMContentLoaded', () => {
    initializeUniversitySelect();
    updateRangeDisplays();
}); 