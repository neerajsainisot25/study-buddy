// Main application JavaScript
document.addEventListener('DOMContentLoaded', function() {
    const healthBtn = document.getElementById('healthBtn');
    const healthResponse = document.getElementById('healthResponse');

    if (healthBtn && healthResponse) {
        healthBtn.addEventListener('click', async function() {
            healthBtn.disabled = true;
            healthBtn.textContent = 'Checking...';
            healthResponse.className = 'response loading';
            healthResponse.textContent = 'Checking API health...';

            try {
                const response = await fetch('/api/health');
                const data = await response.json();
                
                healthResponse.className = 'response success';
                healthResponse.innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
            } catch (error) {
                healthResponse.className = 'response error';
                healthResponse.textContent = 'Error: ' + (error.message || 'Failed to connect to API');
            } finally {
                healthBtn.disabled = false;
                healthBtn.textContent = 'Check API Health';
            }
        });
    }
});

