document.addEventListener('DOMContentLoaded', function() {
    const summaryButton = document.getElementById('summaryButton');
    const neighbourPanel = document.querySelector('.neighbourPanel');
    const resizablePanel = document.querySelector('.resizablePanel');
    const spinner = document.getElementById('spinner');

    // Function to get CSRF token from the meta tag
    function getCsrfToken() {
        return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    }

    summaryButton.addEventListener('click', function() {
        const text = neighbourPanel.textContent || neighbourPanel.innerText;
        const data = { text: text };

        // Show spinner and disable button
        spinner.style.display = 'block';
        summaryButton.disabled = true;
        let alertError = document.getElementById('alertError');
        
        // Send POST request
        fetch('http://localhost:8000/summary/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                // If the response includes an error key, display it
                alertError.textContent = data.error; // Set the error message
                alertError.style.display = 'block'; // Show the alert
            } else {
                // If the response is successful, update the resizablePanel
                alertError.style.display = 'none';
                resizablePanel.textContent = data.summary; // Assuming the response has a "summary" key
            }
            // Update the resizablePanel with the summary
            resizablePanel.textContent = data.summary; // Assuming the response has a "summary" key
        })
        .catch((error) => {
            
            console.error('Error:', error);
        })
        .finally(() => {
            // Hide spinner and enable button
            spinner.style.display = 'none';
            summaryButton.disabled = false;
        });
    });
});
