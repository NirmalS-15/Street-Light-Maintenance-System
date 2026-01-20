$(document).ready(function () {
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    $('#complaintForm').submit(function (e) {
        e.preventDefault();
        const formData = {
            type: $('#type').val() || 'normal',
            district: $('#district').val() || '',
            place: $('#place').val() || '',
            location: $('#location').val() || '',
            issue: $('#issue').val() || '',
            description: $('#description').val() || ''
        };
        console.log('Sending complaint data:', formData);
        $.ajax({
            url: '/api/complaints/',
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json'
            },
            data: JSON.stringify(formData),
            success: function (response) {
                console.log('Success:', response);
                alert('Complaint submitted successfully!');
                $('#complaintForm')[0].reset();
                $('#websiteRatingModal').modal('show');
                history.pushState({}, '', '/');
            },
            error: function (xhr) {
                console.error('Error:', xhr.responseText);
                alert('Error submitting complaint: ' + xhr.responseText);
            }
        });
    });

    $('#websiteFeedbackForm').submit(function (e) {
        e.preventDefault();
        const feedbackData = {
            rating: $('#rating').val(),
            feedback: $('#feedback').val() || ''
        };
        $.ajax({
            url: '/api/feedback/',
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json'
            },
            data: JSON.stringify(feedbackData),
            success: function (response) {
                alert('Feedback submitted successfully!');
                $('#websiteRatingModal').modal('hide');
                $('#websiteFeedbackForm')[0].reset();
            },
            error: function (xhr) {
                console.error('Error:', xhr.responseText);
                alert('Error submitting feedback: ' + xhr.responseText);
            }
        });
    });

    function loadComplaints() {
        $.ajax({
            url: '/api/complaints/',
            method: 'GET',
            headers: { 'X-CSRFToken': csrftoken },
            success: function (data) {
                $('#complaintList').empty();
                data.forEach(complaint => {
                    $('#complaintList').append(`
                        <tr>
                            <td>${complaint.id}</td>
                            <td>${complaint.type}</td>
                            <td>${complaint.district}</td>
                            <td>${complaint.place}</td>
                            <td>${complaint.location}</td>
                            <td>${complaint.issue}</td>
                            <td>${complaint.description}</td>
                            <td>${complaint.status}</td>
                            <td>${complaint.created_at}</td>
                        </tr>
                    `);
                });
            },
            error: function (xhr) {
                console.error('Error:', xhr.responseText);
                alert('Error loading complaints: ' + xhr.responseText);
            }
        });
    }

    function loadAdminComplaints(containerId) {
        $.ajax({
            url: '/api/complaints/',
            method: 'GET',
            headers: { 'X-CSRFToken': csrftoken },
            success: function (data) {
                $(`#${containerId}`).empty();
                data.forEach(complaint => {
                    const resolutionImage = complaint.resolution_image ? 
                        `<a href="${complaint.resolution_image}" target="_blank">View Image</a>` : 'N/A';
                    $(`#${containerId}`).append(`
                        <tr>
                            <td>${complaint.id}</td>
                            <td>${complaint.user.username}</td>
                            <td>${complaint.type}</td>
                            <td>${complaint.district}</td>
                            <td>${complaint.place}</td>
                            <td>${complaint.location}</td>
                            <td>${complaint.issue}</td>
                            <td>${complaint.description}</td>
                            <td>${complaint.status}</td>
                            <td>${complaint.created_at}</td>
                            <td>${complaint.accepted_at || 'N/A'}</td>
                            <td>${complaint.resolved_at || 'N/A'}</td>
                            <td>${complaint.resolution_notes || 'N/A'}</td>
                            <td>${resolutionImage}</td>
                            <td>
                                ${complaint.status === 'pending' ? 
                                    `<button class="btn btn-primary accept-complaint" data-id="${complaint.id}">Accept</button>` : ''}
                                ${complaint.status === 'accepted' ? 
                                    `<button class="btn btn-success resolve-complaint" data-id="${complaint.id}" data-bs-toggle="modal" data-bs-target="#resolveModal${complaint.id}">Resolve</button>` : ''}
                            </td>
                        </tr>
                        <div class="modal fade" id="resolveModal${complaint.id}" tabindex="-1" aria-labelledby="resolveModalLabel${complaint.id}" aria-hidden="true">
                            <div class="modal-dialog">
                                <div class="modal-content">
                                    <div class="modal-header">
                                        <h5 class="modal-title" id="resolveModalLabel${complaint.id}">Resolve Complaint #${complaint.id}</h5>
                                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                                    </div>
                                    <div class="modal-body">
                                        <form id="resolveForm${complaint.id}" enctype="multipart/form-data">
                                            <div class="mb-3">
                                                <label for="resolution_notes${complaint.id}" class="form-label">Resolution Notes</label>
                                                <textarea class="form-control" id="resolution_notes${complaint.id}" name="resolution_notes" rows="4" required></textarea>
                                            </div>
                                            <div class="mb-3">
                                                <label for="resolution_image${complaint.id}" class="form-label">Resolution Image</label>
                                                <input type="file" class="form-control" id="resolution_image${complaint.id}" name="resolution_image" accept="image/*">
                                            </div>
                                            <button type="submit" class="btn btn-success">Resolve</button>
                                        </form>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `);
                });
                $('.accept-complaint').click(function () {
                    const id = $(this).data('id');
                    $.ajax({
                        url: `/api/complaints/${id}/accept/`,
                        method: 'POST',
                        headers: { 'X-CSRFToken': csrftoken },
                        success: function () {
                            alert('Complaint accepted');
                            loadAdminComplaints(containerId);
                        },
                        error: function (xhr) {
                            alert('Error accepting complaint: ' + xhr.responseText);
                        }
                    });
                });
                $('.resolve-complaint').click(function () {
                    const id = $(this).data('id');
                    $(`#resolveForm${id}`).submit(function (e) {
                        e.preventDefault();
                        const formData = new FormData();
                        formData.append('resolution_notes', $(`#resolution_notes${id}`).val());
                        const fileInput = $(`#resolution_image${id}`)[0].files[0];
                        if (fileInput) {
                            formData.append('resolution_image', fileInput);
                        }
                        $.ajax({
                            url: `/api/complaints/${id}/resolve/`,
                            method: 'POST',
                            headers: { 'X-CSRFToken': csrftoken },
                            data: formData,
                            processData: false,
                            contentType: false,
                            success: function () {
                                alert('Complaint resolved');
                                $(`#resolveModal${id}`).modal('hide');
                                loadAdminComplaints(containerId);
                            },
                            error: function (xhr) {
                                alert('Error resolving complaint: ' + xhr.responseText);
                            }
                        });
                    });
                });
            },
            error: function (xhr) {
                console.error('Error:', xhr.responseText);
                alert('Error loading KSEB complaints: ' + xhr.responseText);
            }
        });
    }

    if (window.location.pathname === '/complaints/') {
        loadComplaints();
    } else if (window.location.pathname === '/admin/kseb/') {
        loadAdminComplaints('adminComplaintList');
    }

    window.addEventListener('popstate', function (event) {
        console.log('Back/Forward button pressed', event.state);
        if (window.location.pathname === '/complaints/') {
            loadComplaints();
        } else if (window.location.pathname === '/admin/kseb/') {
            loadAdminComplaints('adminComplaintList');
        } else if (window.location.pathname === '/') {
            $('#complaintForm')[0].reset();
        }
    });
});