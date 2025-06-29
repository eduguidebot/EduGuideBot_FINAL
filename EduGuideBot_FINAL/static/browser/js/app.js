// Initialize Telegram WebApp
const tg = window.Telegram.WebApp;
tg.expand();
tg.MainButton.hide();

// DOM elements
const universityGrid = document.getElementById('university-grid');
const searchInput = document.getElementById('search-input');
const filterLocation = document.getElementById('filter-location');
const universityDetails = document.getElementById('university-details');
const closeDetailsButton = document.getElementById('close-details');
const detailsContent = document.querySelector('.details-content');

// University data should be available from the injected script
let universities = window.universityData || [];
let filteredUniversities = [...universities];

// Initialize the university grid
function initializeGrid() {
    if (universityGrid.querySelector('.loading')) {
        universityGrid.innerHTML = '';
    }
    
    if (filteredUniversities.length === 0) {
        universityGrid.innerHTML = '<p class="no-results">មិនមានលទ្ធផល</p>';
        return;
    }
    
    filteredUniversities.forEach(university => {
        const card = createUniversityCard(university);
        universityGrid.appendChild(card);
    });
}

// Create a university card
function createUniversityCard(university) {
    const card = document.createElement('div');
    card.className = 'university-card';
    card.dataset.id = university.id;
    
    let tuitionRange = '';
    if (university.tuition_fees) {
        tuitionRange = `$${university.tuition_fees.range_min} - $${university.tuition_fees.range_max}/ឆ្នាំ`;
    }
    
    card.innerHTML = `
        <div class="card-header">
            <h2>${university.name_km || university.name_en}</h2>
            <div class="card-location">${university.location || 'N/A'}</div>
        </div>
        <div class="card-body">
            <div class="card-info">
                <p><strong>ឈ្មោះជាភាសាអង់គ្លេស:</strong> ${university.name_en || 'N/A'}</p>
                <p><strong>ឆ្នាំបង្កើត:</strong> ${university.established_year || 'N/A'}</p>
                <p><strong>ថ្លៃសិក្សា:</strong> ${tuitionRange}</p>
            </div>
        </div>
    `;
    
    card.addEventListener('click', () => showUniversityDetails(university));
    
    return card;
}

// Show university details in a modal
function showUniversityDetails(university) {
    let faculties = '';
    if (university.faculties && university.faculties.length > 0) {
        faculties = '<h3>មហាវិទ្យាល័យ និងជំនាញ</h3><ul>';
        university.faculties.forEach(faculty => {
            faculties += `<li><strong>${faculty.name_km}</strong>`;
            
            if (faculty.majors && faculty.majors.length > 0) {
                faculties += '<ul>';
                faculty.majors.forEach(major => {
                    faculties += `<li>${major.name_km || 'N/A'} (${major.category_km || 'N/A'})</li>`;
                });
                faculties += '</ul>';
            }
            
            faculties += '</li>';
        });
        faculties += '</ul>';
    }
    
    let contact = '';
    if (university.contact) {
        contact = '<h3>ទំនាក់ទំនង</h3><ul>';
        
        if (university.contact.phones && university.contact.phones.length > 0) {
            contact += `<li><strong>ទូរស័ព្ទ:</strong> ${university.contact.phones.join(', ')}</li>`;
        }
        
        if (university.contact.email) {
            contact += `<li><strong>អ៊ីមែល:</strong> ${university.contact.email}</li>`;
        }
        
        if (university.contact.website) {
            contact += `<li><strong>គេហទំព័រ:</strong> <a href="${university.contact.website}" target="_blank">${university.contact.website}</a></li>`;
        }
        
        contact += '</ul>';
    }
    
    let admissionRequirements = '';
    if (university.admission_requirements_km && university.admission_requirements_km.length > 0) {
        admissionRequirements = '<h3>តម្រូវការចូលរៀន</h3><ul>';
        university.admission_requirements_km.forEach(req => {
            admissionRequirements += `<li>${req}</li>`;
        });
        admissionRequirements += '</ul>';
    }
    
    detailsContent.innerHTML = `
        <h2>${university.name_km || university.name_en}</h2>
        <p class="university-type">${university.type || 'N/A'} • បង្កើតឆ្នាំ ${university.established_year || 'N/A'}</p>
        
        <div class="details-section">
            <h3>ព័ត៌មានទូទៅ</h3>
            <p><strong>ទីតាំង:</strong> ${university.location || 'N/A'}</p>
            <p><strong>ថ្លៃសិក្សា:</strong> $${university.tuition_fees?.range_min || 'N/A'} - $${university.tuition_fees?.range_max || 'N/A'}/ឆ្នាំ</p>
            <p><strong>ចំនួនជំនាញសរុប:</strong> ${university.total_majors || 'N/A'}</p>
        </div>
        
        ${faculties}
        ${contact}
        ${admissionRequirements}
        
        <button class="share-button" id="share-university" data-id="${university.id}">ចែករំលែក</button>
    `;
    
    // Show the modal
    universityDetails.style.display = 'flex';
    
    // Set up share button
    const shareButton = document.getElementById('share-university');
    if (shareButton) {
        shareButton.addEventListener('click', () => {
            const universityData = {
                action: 'share_university',
                id: university.id,
                name: university.name_km || university.name_en
            };
            tg.sendData(JSON.stringify(universityData));
        });
    }
}

// Filter universities based on search and location
function filterUniversities() {
    const searchTerm = searchInput.value.toLowerCase();
    const location = filterLocation.value;
    
    filteredUniversities = universities.filter(uni => {
        const nameMatch = (uni.name_km && uni.name_km.toLowerCase().includes(searchTerm)) || 
                         (uni.name_en && uni.name_en.toLowerCase().includes(searchTerm));
        
        const locationMatch = location === '' || uni.location === location;
        
        return nameMatch && locationMatch;
    });
    
    // Re-render the grid
    universityGrid.innerHTML = '';
    initializeGrid();
}

// Event listeners
searchInput.addEventListener('input', filterUniversities);
filterLocation.addEventListener('change', filterUniversities);

closeDetailsButton.addEventListener('click', () => {
    universityDetails.style.display = 'none';
});

// Initialize the grid on load
document.addEventListener('DOMContentLoaded', initializeGrid); 