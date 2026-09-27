$(document).ready(function() {
    $('.nav-link').on('click', function(e) {
        e.preventDefault();  // Prevent the default action of the link
        
        var url = $(this).data('url');  // Get the URL from the data-url attribute

        // Check if the URL is valid
        if (url) {
            // Make an AJAX GET request
            $.get(url, function(data) {
                $('#content').html(data);  // Load the content into the #content div
            }).fail(function() {
                console.log('Error loading content.');
            });
        } else {
            console.log('Invalid URL');
        }
    });
});