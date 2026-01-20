document.addEventListener('DOMContentLoaded', function () {
    const resolveModal = document.getElementById('resolveModal');
    const resolveForm = document.getElementById('resolveForm');
    const complaintIdSpan = document.getElementById('complaint-id');
    const complaintIdInput = document.getElementById('complaint-id-input');

    // Open modal and set complaint ID
    document.querySelectorAll('.resolve-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const id = this.getAttribute('data-id');
            complaintIdSpan.textContent = id;
            complaintIdInput.value = id;
            resolveModal.querySelector('form').action = `/api/complaints/${id}/resolve/`;
            new bootstrap.Modal(resolveModal).show();
        });
    });

    // Handle Accept buttons (via AJAX)
    document.querySelectorAll('.accept-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const id = this.getAttribute('data-id');
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            fetch(`/api/complaints/${id}/accept/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'complaint accepted') {
                    location.reload();
                }
            });
        });
    });
});