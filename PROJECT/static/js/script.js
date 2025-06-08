document.addEventListener('DOMContentLoaded', function() {
    // Gender selection
    const genderButtons = document.querySelectorAll('#genderGroup .option-btn');
    let selectedGender = null;

    genderButtons.forEach(button => {
        button.addEventListener('click', function() {
            genderButtons.forEach(btn => btn.classList.remove('selected'));
            this.classList.add('selected');
            selectedGender = parseInt(this.getAttribute('data-value'));
        });
    });

    // Symptoms selection
    const symptomButtons = document.querySelectorAll('.symptom-category .option-btn');
    const selectedSymptoms = new Set();

    symptomButtons.forEach(button => {
        button.addEventListener('click', function() {
            this.classList.toggle('selected');
            const symptom = this.getAttribute('data-value');
            if (this.classList.contains('selected')) {
                selectedSymptoms.add(symptom);
            } else {
                selectedSymptoms.delete(symptom);
            }
        });
    });

    // Category collapse/expand
    const categoryTitles = document.querySelectorAll('.category-title');
    categoryTitles.forEach(title => {
        const content = title.nextElementSibling;
        content.style.display = 'none'; // Start collapsed
        title.classList.add('collapsed');

        title.addEventListener('click', function() {
            this.classList.toggle('collapsed');
            content.style.display = this.classList.contains('collapsed') ? 'none' : 'flex';
        });
    });

    // Symptom search
    const symptomSearch = document.getElementById('symptomSearch');
    symptomSearch.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        symptomButtons.forEach(button => {
            const symptomText = button.textContent.toLowerCase();
            button.style.display = symptomText.includes(searchTerm) ? 'inline-block' : 'none';
        });
    });

    // Form submission
    const form = document.getElementById('symptomForm');
    const resultsDiv = document.getElementById('results');
    const resultsContent = document.getElementById('resultsContent');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        const age = document.getElementById('ageInput').value;

        // Validate inputs
        if (selectedGender === null) {
            alert('Please select your gender');
            return;
        }
        if (!age || age < 1 || age > 120) {
            alert('Please enter a valid age (1-120)');
            return;
        }
        if (selectedSymptoms.size === 0) {
            alert('Please select at least one symptom');
            return;
        }

        // Prepare data
        const payload = {
            gender: selectedGender,
            age: parseInt(age),
            symptoms: Array.from(selectedSymptoms)
        };

        try {
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const result = await response.json();

            if (result.error) {
                throw new Error(result.error);
            }

            resultsContent.innerHTML = `
                <p><strong>Predicted Disease:</strong> ${result.disease}</p>
                <p><strong>Description:</strong> ${result.description}</p>
                <p><strong>Medicines:</strong> ${result.medicines}</p>
                <p><strong>Diet:</strong> ${result.diet}</p>
                <p><strong>Precautions:</strong> ${result.precautions.join(', ')}</p>
                <p><strong>Workout:</strong> ${result.workout.join(', ')}</p>
            `;

            resultsDiv.style.display = 'block';
            resultsDiv.scrollIntoView({ behavior: 'smooth' });
        } catch (err) {
            console.error('Error:', err);
            alert(`Failed to get prediction: ${err.message}`);
        }
    });
});