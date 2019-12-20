$(document).ready(function () {
    $("#sidebar").mCustomScrollbar({
        theme: "minimal"
    });

    $('#menu-toggle').on('click', function () {
        
        
        $('#sidebar, .side_container').toggleClass('active');
        
        $('.main').toggleClass('active');
        
        $('.collapse.in').toggleClass('in');
        $('a[aria-expanded=true]').attr('aria-expanded', 'false');
    });
});