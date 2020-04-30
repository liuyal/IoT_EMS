$(document).ready(function () {

    $("#sidebar").mCustomScrollbar({
        theme: "minimal"
    });

    $('#menu-toggle').on('click', function (e) {
        var save_state = !$('#sidebar, .side_container').hasClass('collapsed');
        localStorage.setItem('menu-closed', save_state);
        $('#sidebar, .main_wrapper, .nav-header, .footer_wrapper').toggleClass('collapsed');
        $('a[aria-expanded=true]').attr('aria-expanded', 'false');
    });

});



