// Generic helpers

async function apiFetch(url, options = {}) {
    const response = await fetch(url, options);
    if (!response.ok) {
        let errorMsg = 'خطایی رخ داد';
        try {
            const err = await response.json();
            errorMsg = err.error || errorMsg;
        } catch (e) {
            console.error('Non-JSON error response');
        }
        throw new Error(errorMsg);
    }
    return response.json();
}

function showAlert(message, type = 'success') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    // Find a suitable place to prepend
    const main = document.querySelector('main');
    if (main) {
        main.prepend(alertDiv);
        // Auto dismiss after 5 seconds
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alertDiv);
            bsAlert.close();
        }, 5000);
    }
}
